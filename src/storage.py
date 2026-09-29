import json
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any, Optional

from src.config import DATA_DIR, DATA_FILE, DEFAULT_CYCLE_DAYS

logger = logging.getLogger(__name__)

DEFAULT_DATA: Dict[str, Any] = {
    "last_change_date": None,         # Formato: "YYYY-MM-DD"
    "cycle_days": DEFAULT_CYCLE_DAYS, # Padrão: 30 dias
    "notified_thresholds": [],        # Ex: [7, 3] para não repetir alertas no mesmo ciclo
    "autostart": True,                # Padrão permanente: sempre inicia com o sistema
    "minimize_to_tray": True,         # Padrão permanente: sempre minimiza para a bandeja
    "theme": "dark"
}


class Storage:
    def __init__(self, data_file: Path = DATA_FILE):
        self.data_file = data_file
        self.data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        """Carrega os dados locais do arquivo JSON ou inicializa com valores padrão."""
        if not self.data_file.exists():
            return DEFAULT_DATA.copy()
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                content = json.load(f)
                data = DEFAULT_DATA.copy()
                data.update(content)
                # Garante os padrões corporativos obrigatórios
                data["autostart"] = True
                data["minimize_to_tray"] = True
                return data
        except Exception as e:
            logger.error(f"Erro ao carregar dados locais ({self.data_file}): {e}")
            return DEFAULT_DATA.copy()

    def save(self) -> bool:
        """Salva o estado atual no disco em formato JSON."""
        try:
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar dados locais ({self.data_file}): {e}")
            return False

    def get_last_change_date(self) -> Optional[date]:
        """Retorna a data da última troca ou None se não configurada."""
        val = self.data.get("last_change_date")
        if not val:
            return None
        try:
            return datetime.strptime(val, "%Y-%m-%d").date()
        except ValueError:
            return None

    def set_last_change_date(self, new_date: date) -> None:
        """Define a nova data de troca e reinicia os alertas já enviados para o novo ciclo."""
        self.data["last_change_date"] = new_date.strftime("%Y-%m-%d")
        self.data["notified_thresholds"] = []
        self.save()

    def get_cycle_days(self) -> int:
        return int(self.data.get("cycle_days", DEFAULT_CYCLE_DAYS))

    def set_cycle_days(self, days: int) -> None:
        self.data["cycle_days"] = max(1, days)
        self.save()

    def get_notified_thresholds(self) -> list:
        return self.data.get("notified_thresholds", [])

    def mark_threshold_notified(self, threshold: int) -> None:
        """Registra que o alerta deste limiar já foi disparado no ciclo atual."""
        if threshold not in self.data["notified_thresholds"]:
            self.data["notified_thresholds"].append(threshold)
            self.save()

    def get_autostart(self) -> bool:
        return bool(self.data.get("autostart", False))

    def set_autostart(self, enabled: bool) -> None:
        self.data["autostart"] = enabled
        self.save()

    def get_minimize_to_tray(self) -> bool:
        return bool(self.data.get("minimize_to_tray", True))

    def set_minimize_to_tray(self, enabled: bool) -> None:
        self.data["minimize_to_tray"] = enabled
        self.save()
