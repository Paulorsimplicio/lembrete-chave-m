import unittest
from datetime import date
from src.holidays import (
    get_easter_date,
    get_brazilian_national_holidays,
    is_brazilian_holiday,
    is_business_day,
    get_deadline_business_day,
)

class TestHolidays(unittest.TestCase):
    def test_easter_and_mobile_holidays(self):
        # Páscoa em 2026 é 05/04/2026
        easter_2026 = get_easter_date(2026)
        self.assertEqual(easter_2026, date(2026, 4, 5))

        holidays = get_brazilian_national_holidays(2026)
        # Sexta-feira Santa 2026: 03/04/2026
        self.assertIn(date(2026, 4, 3), holidays)
        # Corpus Christi 2026: 04/06/2026
        self.assertIn(date(2026, 6, 4), holidays)

    def test_fixed_national_holidays(self):
        # 07 de Setembro
        is_hol, name = is_brazilian_holiday(date(2026, 9, 7))
        self.assertTrue(is_hol)
        self.assertIn("Independência", name)

        # 25 de Dezembro
        is_hol, _ = is_brazilian_holiday(date(2026, 12, 25))
        self.assertTrue(is_hol)

        # 20 de Novembro (Consciência Negra)
        is_hol, _ = is_brazilian_holiday(date(2026, 11, 20))
        self.assertTrue(is_hol)

    def test_business_day(self):
        # Sábado não é dia útil
        self.assertFalse(is_business_day(date(2026, 10, 3)))
        # Domingo não é dia útil
        self.assertFalse(is_business_day(date(2026, 10, 4)))
        # Segunda-feira comum é dia útil
        self.assertTrue(is_business_day(date(2026, 10, 5)))
        # Feriado em dia de semana não é dia útil (12/10/2026 cai numa segunda)
        self.assertFalse(is_business_day(date(2026, 10, 12)))

    def test_get_deadline_business_day_anticipation(self):
        # Se cair num Sábado (ex: 03/10/2026), deve antecipar para Sexta (02/10/2026)
        target = date(2026, 10, 3)
        adjusted, was_adj, reason = get_deadline_business_day(target)
        self.assertTrue(was_adj)
        self.assertEqual(adjusted, date(2026, 10, 2))
        self.assertIn("Sábado", reason)

        # Se cair num Domingo (ex: 04/10/2026), deve antecipar para Sexta (02/10/2026)
        target_sun = date(2026, 10, 4)
        adjusted_sun, was_adj_sun, reason_sun = get_deadline_business_day(target_sun)
        self.assertTrue(was_adj_sun)
        self.assertEqual(adjusted_sun, date(2026, 10, 2))

        # Se já for dia útil (ex: Quarta-feira 07/10/2026), não altera
        wednesday = date(2026, 10, 7)
        adjusted_wed, was_adj_wed, _ = get_deadline_business_day(wednesday)
        self.assertFalse(was_adj_wed)
        self.assertEqual(adjusted_wed, wednesday)

if __name__ == "__main__":
    unittest.main()
