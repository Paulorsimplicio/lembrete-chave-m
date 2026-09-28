import unittest
from datetime import date, timedelta
from unittest.mock import MagicMock
from pathlib import Path
import tempfile

from src.reminder_engine import calculate_status, check_and_notify
from src.storage import Storage

class TestReminderEngine(unittest.TestCase):
    def test_calculate_status_no_date(self):
        status = calculate_status(None)
        self.assertFalse(status["has_date"])
        self.assertEqual(status["status_code"], "not_set")

    def test_calculate_status_safe(self):
        today = date(2026, 9, 28)
        # Troca em 20/09/2026:
        # Dia 29 = 19/10/2026 (Segunda-feira, dia útil)
        last_change = date(2026, 9, 20)
        status = calculate_status(last_change, cycle_days=30, today=today)
        self.assertTrue(status["has_date"])
        self.assertEqual(status["effective_deadline"], date(2026, 10, 19))
        self.assertEqual(status["expiration_date"], date(2026, 10, 20))
        self.assertEqual(status["days_remaining"], 21)
        self.assertEqual(status["status_code"], "safe")

    def test_deadline_weekend_anticipation(self):
        # Testando quando o dia 29 cai num sábado
        # Se última troca = 04/09/2026 (Sexta)
        # Dia 29 = 03/10/2026 (Sábado) -> Deve antecipar para 02/10/2026 (Sexta-feira)!
        last_change = date(2026, 9, 4)
        status = calculate_status(last_change, cycle_days=30, today=date(2026, 9, 28))
        self.assertTrue(status["was_adjusted"])
        self.assertEqual(status["raw_deadline"], date(2026, 10, 3))
        self.assertEqual(status["effective_deadline"], date(2026, 10, 2))

    def test_calculate_status_warning_5_days(self):
        # Limite útil em 03/10/2026 seria Sábado -> vira 02/10/2026 (Sexta)
        # Hoje = 27/09/2026 -> 02/10 - 27/09 = 5 dias
        today = date(2026, 9, 27)
        last_change = date(2026, 9, 4)
        status = calculate_status(last_change, cycle_days=30, today=today)
        self.assertEqual(status["days_remaining"], 5)
        self.assertEqual(status["status_code"], "warning")

    def test_calculate_status_danger_2_days(self):
        today = date(2026, 9, 30)
        last_change = date(2026, 9, 4) # Limite útil = 02/10/2026 (Sexta)
        status = calculate_status(last_change, cycle_days=30, today=today)
        self.assertEqual(status["days_remaining"], 2)
        self.assertEqual(status["status_code"], "danger")

    def test_calculate_status_last_business_day_today(self):
        today = date(2026, 10, 2)
        last_change = date(2026, 9, 4) # Limite útil = 02/10/2026 (Sexta)
        status = calculate_status(last_change, cycle_days=30, today=today)
        self.assertEqual(status["days_remaining"], 0)
        self.assertEqual(status["status_code"], "today")

    def test_calculate_status_overdue(self):
        today = date(2026, 10, 5)
        last_change = date(2026, 9, 4) # Limite útil = 02/10/2026
        status = calculate_status(last_change, cycle_days=30, today=today)
        self.assertLess(status["days_remaining"], 0)
        self.assertEqual(status["status_code"], "overdue")

    def test_check_and_notify_thresholds(self):
        temp_dir = tempfile.TemporaryDirectory()
        test_file = Path(temp_dir.name) / "test_config.json"
        storage = Storage(data_file=test_file)

        # Última troca em 04/09/2026 -> limite útil 02/10/2026
        storage.set_last_change_date(date(2026, 9, 4))

        mock_notifier = MagicMock()
        mock_notifier.notify.return_value = True

        # Testando limiar de 5 dias (Hoje: 27/09/2026)
        triggered = check_and_notify(storage, mock_notifier, today=date(2026, 9, 27))
        self.assertEqual(triggered, 5)
        self.assertEqual(mock_notifier.notify.call_count, 1)
        self.assertIn(5, storage.get_notified_thresholds())

        # Segunda checagem no mesmo dia não deve disparar novamente
        triggered_again = check_and_notify(storage, mock_notifier, today=date(2026, 9, 27))
        self.assertIsNone(triggered_again)
        self.assertEqual(mock_notifier.notify.call_count, 1)

        temp_dir.cleanup()

if __name__ == "__main__":
    unittest.main()
