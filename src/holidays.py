from datetime import date, timedelta
from typing import Dict, Set, Tuple

def get_easter_date(year: int) -> date:
    """Calcula a data do Domingo de Páscoa usando o algoritmo de Meeus/Jones/Butcher."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def get_brazilian_national_holidays(year: int) -> Dict[date, str]:
    """Retorna todos os feriados nacionais brasileiros (fixos e móveis) para o ano especificado."""
    holidays: Dict[date, str] = {
        date(year, 1, 1): "Confraternização Universal",
        date(year, 4, 21): "Tiradentes",
        date(year, 5, 1): "Dia do Trabalhador",
        date(year, 9, 7): "Independência do Brasil",
        date(year, 10, 12): "Nossa Senhora Aparecida",
        date(year, 11, 2): "Finados",
        date(year, 11, 15): "Proclamação da República",
        date(year, 11, 20): "Dia Nacional de Zumbi e da Consciência Negra",
        date(year, 12, 25): "Natal",
    }

    # Feriados móveis baseados na Páscoa
    easter = get_easter_date(year)
    holidays[easter - timedelta(days=2)] = "Sexta-feira Santa (Paixão de Cristo)"
    holidays[easter - timedelta(days=47)] = "Carnaval (Terça-feira)"
    holidays[easter + timedelta(days=60)] = "Corpus Christi"

    return holidays


def is_brazilian_holiday(d: date) -> Tuple[bool, str]:
    """Verifica se uma data é feriado nacional brasileiro."""
    year_holidays = get_brazilian_national_holidays(d.year)
    if d in year_holidays:
        return True, year_holidays[d]
    return False, ""


def is_business_day(d: date) -> bool:
    """Retorna True se for dia útil (segunda a sexta e não feriado)."""
    # 0=Segunda, 4=Sexta, 5=Sábado, 6=Domingo
    if d.weekday() >= 5:
        return False
    is_hol, _ = is_brazilian_holiday(d)
    return not is_hol


def get_deadline_business_day(target_date: date) -> Tuple[date, bool, str]:
    """
    Se target_date cair em final de semana ou feriado,
    recua para o dia útil imediatamente anterior.
    Retorna (data_ajustada, foi_ajustado, motivo).
    """
    current = target_date
    adjusted = False
    reasons = []

    while not is_business_day(current):
        adjusted = True
        if current.weekday() == 5:
            reasons.append(f"{current.strftime('%d/%m')} é Sábado")
        elif current.weekday() == 6:
            reasons.append(f"{current.strftime('%d/%m')} é Domingo")
        else:
            _, hol_name = is_brazilian_holiday(current)
            reasons.append(f"{current.strftime('%d/%m')} é Feriado ({hol_name})")

        current -= timedelta(days=1)

    reason_str = ", ".join(reasons) if adjusted else ""
    return current, adjusted, reason_str
