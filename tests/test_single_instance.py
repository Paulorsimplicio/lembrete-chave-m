import unittest
import time
from src.single_instance import SingleInstanceManager

class TestSingleInstance(unittest.TestCase):
    def test_single_instance_detection(self):
        # Usamos uma porta específica para os testes para não colidir com app aberto
        test_port = 58432
        
        # Primeira instância deve iniciar com sucesso
        inst1 = SingleInstanceManager(port=test_port)
        self.assertFalse(inst1.is_already_running(show_popup=False))

        # Segunda instância deve detectar que já está rodando
        inst2 = SingleInstanceManager(port=test_port)
        self.assertTrue(inst2.is_already_running(show_popup=False))
        inst2.close()

        # Após fechar a primeira instância, uma nova deve conseguir iniciar
        inst1.close()
        time.sleep(0.1)

        inst3 = SingleInstanceManager(port=test_port)
        self.assertFalse(inst3.is_already_running(show_popup=False))
        inst3.close()

if __name__ == "__main__":
    unittest.main()
