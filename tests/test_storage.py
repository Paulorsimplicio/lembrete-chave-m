import unittest
import tempfile
import os
from pathlib import Path
from datetime import date

from src.storage import Storage

class TestStorage(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file = Path(self.temp_dir.name) / "test_config.json"
        self.storage = Storage(data_file=self.test_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_default_values(self):
        self.assertIsNone(self.storage.get_last_change_date())
        self.assertEqual(self.storage.get_cycle_days(), 30)
        self.assertEqual(self.storage.get_notified_thresholds(), [])
        self.assertTrue(self.storage.get_autostart())
        self.assertTrue(self.storage.get_minimize_to_tray())

    def test_set_last_change_date(self):
        d = date(2026, 9, 20)
        self.storage.set_last_change_date(d)
        self.assertEqual(self.storage.get_last_change_date(), d)
        
        # Recarregar novo objeto a partir do mesmo arquivo
        new_storage = Storage(data_file=self.test_file)
        self.assertEqual(new_storage.get_last_change_date(), d)

    def test_threshold_notification_lifecycle(self):
        d = date(2026, 9, 1)
        self.storage.set_last_change_date(d)
        self.assertEqual(self.storage.get_notified_thresholds(), [])

        self.storage.mark_threshold_notified(7)
        self.assertIn(7, self.storage.get_notified_thresholds())

        self.storage.mark_threshold_notified(3)
        self.assertIn(3, self.storage.get_notified_thresholds())
        self.assertEqual(len(self.storage.get_notified_thresholds()), 2)

        # Ao atualizar a data da troca (novo ciclo), os limiares devem ser resetados!
        new_date = date(2026, 9, 28)
        self.storage.set_last_change_date(new_date)
        self.assertEqual(self.storage.get_notified_thresholds(), [])

    def test_autostart_and_tray_flags(self):
        self.storage.set_autostart(True)
        self.assertTrue(self.storage.get_autostart())

        self.storage.set_minimize_to_tray(False)
        self.assertFalse(self.storage.get_minimize_to_tray())

if __name__ == "__main__":
    unittest.main()
