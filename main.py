import sys
import argparse
import logging
from datetime import date
from src.config import (
    APP_NAME,
    BACKGROUND_CHECK_INTERVAL,
)
from src.storage import Storage
from src.notifier import Notifier
from src.reminder_engine import check_and_notify, calculate_status
from src.tray import TrayManager
from src.gui import MainWindow
from src.single_instance import SingleInstanceManager

# Configuração de Logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


class Application:
    def __init__(self, start_minimized: bool = False):
        # 1. Verifica se já existe uma instância do gadget em execução
        self.single_instance = SingleInstanceManager(
            on_activate_callback=self._on_reactivate_requested
        )
        if self.single_instance.is_already_running():
            sys.exit(0)

        self.start_minimized = start_minimized
        self.storage = Storage()
        self.notifier = Notifier()
        self.is_running = True

        # Cria a janela principal
        self.window = MainWindow(
            storage=self.storage,
            notifier=self.notifier,
            on_exit_callback=self.shutdown,
            on_status_change_callback=self._on_status_change
        )

        # Gerenciador da Bandeja do Sistema
        self.tray = TrayManager(
            on_show_window=self._show_window_from_tray,
            on_update_today=self._update_today_from_tray,
            on_exit=self.shutdown
        )

        # Se solicitado para iniciar minimizado (ex: no boot do Windows)
        if self.start_minimized:
            self.window.withdraw()

        # OTIMIZAÇÃO DE PERFORMANCE:
        # A janela gráfica é exibida IMEDIATAMENTE na tela.
        # Os serviços secundários (bandeja, checagem e timers) são carregados logo em seguida (50ms)
        # sem travar ou atrasar a abertura da interface para o usuário.
        self.window.after(50, self._lazy_init_services)

    def _lazy_init_services(self):
        """Inicializa serviços em segundo plano de forma assíncrona após a janela abrir."""
        try:
            self.tray.start()
            self._perform_scheduled_check()
            self._schedule_periodic_check()
        except Exception as e:
            logger.error(f"Erro ao inicializar serviços secundários: {e}")

    def _on_status_change(self, status_text: str):
        """Atualiza a mensagem de status exibida no menu da bandeja."""
        if hasattr(self, "tray") and self.tray:
            self.tray.set_status_text(status_text)

    def _show_window_from_tray(self):
        """Chamado pela thread da bandeja para exibir a janela principal."""
        self.window.after(0, self.window.show_window)

    def _on_reactivate_requested(self):
        """Chamado quando outra tentativa de abertura do gadget for detectada."""
        logger.info("Reativação da janela solicitada por nova tentativa de execução.")
        if hasattr(self, "window") and self.window:
            self.window.after(0, self.window.show_window)

    def _update_today_from_tray(self):
        """Chamado pelo menu da bandeja para marcar a troca hoje."""
        self.window.after(0, self.window.set_changed_today)

    def _perform_scheduled_check(self):
        """Executa a verificação dos limiares (7, 3, 1, 0 dias) e dispara avisos se necessário."""
        try:
            triggered = check_and_notify(self.storage, self.notifier)
            if triggered is not None:
                logger.info(f"Notificação de limiar disparada: {triggered} dias.")
            # Atualiza o texto na bandeja
            last_date = self.storage.get_last_change_date()
            if last_date:
                status = calculate_status(last_date, self.storage.get_cycle_days())
                self.tray.set_status_text(f"{status['days_remaining']} dias restantes")
        except Exception as e:
            logger.error(f"Erro durante a verificação de expiração: {e}")

    def _schedule_periodic_check(self):
        """Agenda a próxima verificação no loop de eventos."""
        if not self.is_running:
            return
        # Intervalo em milissegundos
        interval_ms = BACKGROUND_CHECK_INTERVAL * 1000
        self.window.after(interval_ms, self._on_periodic_timer)

    def _on_periodic_timer(self):
        self._perform_scheduled_check()
        self._schedule_periodic_check()

    def shutdown(self):
        """Encerra a aplicação de forma limpa."""
        logger.info("Encerrando aplicação...")
        self.is_running = False
        try:
            if hasattr(self, "single_instance") and self.single_instance:
                self.single_instance.close()
        except Exception:
            pass
        try:
            self.tray.stop()
        except Exception:
            pass
        try:
            self.window.destroy()
        except Exception:
            pass
        sys.exit(0)

    def run(self):
        """Inicia o loop principal da interface."""
        try:
            self.window.mainloop()
        except KeyboardInterrupt:
            self.shutdown()


def main():
    parser = argparse.ArgumentParser(description=f"{APP_NAME} - Foursys Bradesco")
    parser.add_argument(
        "--minimized", "--tray",
        action="store_true",
        help="Inicia a aplicação minimizada diretamente na bandeja do sistema."
    )
    args = parser.parse_args()

    app = Application(start_minimized=args.minimized)
    app.run()


if __name__ == "__main__":
    main()
