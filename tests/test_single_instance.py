import unittest
import time
from src.single_instance import SingleInstanceManager, parse_version

class TestSingleInstance(unittest.TestCase):
    def test_parse_version(self):
        self.assertEqual(parse_version("1.2.1"), (1, 2, 1))
        self.assertEqual(parse_version("v1.4.0"), (1, 4, 0))
        self.assertTrue(parse_version("1.4.0") > parse_version("1.3.0"))
        self.assertTrue(parse_version("2.0.0") > parse_version("1.9.9"))
        self.assertFalse(parse_version("1.3.0") > parse_version("1.3.0"))

    def test_single_instance_detection_same_version(self):
        test_port = 58432
        
        # Primeira instância inicia com versão 1.4.0
        inst1 = SingleInstanceManager(port=test_port, current_version="1.4.0")
        self.assertFalse(inst1.is_already_running(show_popup=False))

        # Segunda instância com mesma versão (1.4.0) deve detectar duplicata
        inst2 = SingleInstanceManager(port=test_port, current_version="1.4.0")
        self.assertTrue(inst2.is_already_running(show_popup=False))
        inst2.close()

        inst1.close()
        time.sleep(0.1)

    def test_upgrade_replaces_older_instance(self):
        test_port = 58433
        
        # Instância 1 antiga (v1.3.0) rodando
        inst_old = SingleInstanceManager(port=test_port, current_version="1.3.0")
        self.assertFalse(inst_old.is_already_running(show_popup=False))

        # Nova instância mais recente (v1.4.0) tenta rodar
        inst_new = SingleInstanceManager(port=test_port, current_version="1.4.0")
        
        # Deve substituir a versão antiga e assumir a execução (is_already_running retorna False)
        self.assertFalse(inst_new.is_already_running(show_popup=False))
        self.assertTrue(inst_new.was_upgraded)
        self.assertEqual(inst_new.replaced_version, "1.3.0")

        inst_new.close()
        time.sleep(0.1)

if __name__ == "__main__":
    unittest.main()
