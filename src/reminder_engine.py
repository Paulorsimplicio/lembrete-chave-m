from datetime import date, timedelta
from typing import Optional, Dict, Any
import logging

from src.config import (
    DEFAULT_CYCLE_DAYS,
    MAX_CYCLE_DAY,
    ALERT_THRESHOLDS,
    COLOR_SAFE,
    COLOR_WARNING,
    COLOR_DANGER,
    COLOR_EXPIRED,
)
from src.holidays import get_deadline_business_day
from src.storage import Storage
from src.notifier import Notifier

logger = logging.getLogger(__name__)

MESSAGES_BY_THRESHOLD = {
    5: {
        "title": "Aviso Chave M (5 dias)",
        "message": "Faltam 5 dias para a data limite segura de troca da sua chave M! Planeje a troca."
    },
    3: {
        "title": "Atenção Chave M (3 dias)",
        "message": "Faltam 3 dias para a data limite de troca da chave M! Troque antes que expire."
    },
    2: {
        "title": "Urgente Chave M (2 dias)",
        "message": "Faltam apenas 2 dias úteis para a troca da sua chave M! Troque para evitar bloqueio."
    },
    1: {
        "title": "ALERTA MÁXIMO: Expira Amanhã!",
        "message": "Amanhã é o ÚLTIMO dia útil para trocar sua chave M! Acesse o portal hoje mesmo."
    },
    0: {
        "title": "🚨 ÚLTIMO DIA ÚTIL: Troque Hoje!",
        "message": "Hoje é o último dia útil permitido para trocar sua chave M! Troque agora no portal Bradesco."
    }
}


def calculate_status(
    last_change_date: Optional[date],
    cycle_days: int = DEFAULT_CYCLE_DAYS,
    today: Optional[date] = None
) -> Dict[str, Any]:
    """
    Calcula os dias restantes, status, cor visual e data limite de troca.
    Regra: A senha expira no 30º dia, portanto o limite seguro é até o 29º dia.
    Se o 29º dia cair em final de semana ou feriado nacional, a data limite
    é antecipada para o dia útil anterior.
    """
    if today is None:
        today = date.today()

    if not last_change_date:
        return {
            "has_date": False,
            "days_remaining": 0,
            "expiration_date": None,
            "effective_deadline": None,
            "raw_deadline": None,
            "was_adjusted": False,
            "adjustment_reason": "",
            "status_code": "not_set",
            "status_label": "Data não informada",
            "message": "Informe a data da sua última troca de senha.",
            "color": COLOR_WARNING,
            "progress": 0.0,
        }

    # Data de expiração técnica (30 dias)
    expiration_date = last_change_date + timedelta(days=cycle_days)

    # Data máxima aceitável antes de expirar (dia 29 da contagem)
    raw_deadline = last_change_date + timedelta(days=MAX_CYCLE_DAY)

    # Ajuste para dia útil anterior se sábado, domingo ou feriado
    effective_deadline, was_adjusted, adjustment_reason = get_deadline_business_day(raw_deadline)

    # Dias restantes para trocar (em relação à data limite útil)
    days_remaining = (effective_deadline - today).days

    # Progresso do ciclo
    total_period = (effective_deadline - last_change_date).days
    days_passed = (today - last_change_date).days
    progress = max(0.0, min(1.0, days_passed / total_period if total_period > 0 else 1.0))

    if days_remaining > 5:
        status_code = "safe"
        status_label = "Acesso Seguro"
        message = f"Sua senha está segura por mais {days_remaining} dias úteis."
        color = COLOR_SAFE
    elif 3 <= days_remaining <= 5:
        status_code = "warning"
        status_label = "Atenção: Troca Próxima"
        message = f"Faltam {days_remaining} dias para a data limite de troca."
        color = COLOR_WARNING
    elif 1 <= days_remaining <= 2:
        status_code = "danger"
        status_label = "Urgente: Trocar Senha"
        message = f"Faltam apenas {days_remaining} dia(s)! Troque para evitar bloqueio."
        color = COLOR_DANGER
    elif days_remaining == 0:
        status_code = "today"
        status_label = "ÚLTIMO DIA PARA A TROCA!"
        message = "Hoje é o último dia útil para trocar sua senha! Troque imediatamente."
        color = COLOR_EXPIRED
    else:
        status_code = "overdue"
        status_label = "PRAZO DE TROCA VENCIDO!"
        message = f"O prazo útil de troca venceu há {abs(days_remaining)} dia(s)."
        color = COLOR_EXPIRED

    return {
        "has_date": True,
        "last_change_date": last_change_date,
        "expiration_date": expiration_date,
        "effective_deadline": effective_deadline,
        "raw_deadline": raw_deadline,
        "was_adjusted": was_adjusted,
        "adjustment_reason": adjustment_reason,
        "days_remaining": days_remaining,
        "status_code": status_code,
        "status_label": status_label,
        "message": message,
        "color": color,
        "progress": progress,
    }


def check_and_notify(
    storage: Storage,
    notifier: Notifier,
    today: Optional[date] = None
) -> Optional[int]:
    """
    Verifica se a data atual atingiu os limiares de alerta (5, 3, 2, 1 ou 0 dias)
    em relação à data limite útil de troca e dispara a notificação nativa se
    ainda não foi disparada neste ciclo.
    """
    if today is None:
        today = date.today()

    last_date = storage.get_last_change_date()
    if not last_date:
        return None

    cycle_days = storage.get_cycle_days()
    status = calculate_status(last_date, cycle_days, today)
    days_remaining = status["days_remaining"]
    notified = storage.get_notified_thresholds()

    # Itera pelos limiares em ordem decrescente (5, 3, 2, 1, 0)
    for threshold in sorted(ALERT_THRESHOLDS, reverse=True):
        if days_remaining <= threshold and threshold not in notified:
            alert_info = MESSAGES_BY_THRESHOLD.get(threshold)
            if alert_info:
                notifier.notify(
                    title=alert_info["title"],
                    message=alert_info["message"],
                    timeout=15
                )
                storage.mark_threshold_notified(threshold)
                logger.info(f"Alerta do limiar {threshold} dias disparado com sucesso.")
                return threshold

    return None
