import threading
import logging
from PIL import Image
import pystray
from pystray import MenuItem as item
import webbrowser
from src.config import ICON_PNG, APP_NAME, BRADESCO_PASSWORD_URL

logger = logging.getLogger(__name__)

class TrayManager:
    def __init__(self, on_show_window, on_update_today, on_exit):
        self.on_show_window = on_show_window
        self.on_update_today = on_update_today
        self.on_exit = on_exit
        self.icon: pystray.Icon = None
        self.current_status_text = "Chave M: Carregando..."

    def set_status_text(self, text: str):
        """Atualiza a legenda de status exibida no menu de contexto da bandeja."""
        self.current_status_text = text
        if self.icon:
            self.icon.title = f"{APP_NAME} - {text}"
            self.icon.update_menu()

    def _open_portal(self, icon=None, item=None):
        """Abre o portal IdentityNow do Bradesco no navegador padrão."""
        try:
            webbrowser.open(BRADESCO_PASSWORD_URL)
        except Exception as e:
            logger.error(f"Erro ao abrir link do portal: {e}")

    def _create_menu(self):
        return pystray.Menu(
            item(lambda text: self.current_status_text, None, enabled=False),
            pystray.Menu.SEPARATOR,
            item("Abrir Painel", self._on_show_window, default=True),
            item("Troquei Minha Senha Hoje", self._on_update_today),
            item("Ir para Portal de Troca de Senha", self._open_portal),
            pystray.Menu.SEPARATOR,
            item("Sair", self._on_exit)
        )

    def _on_show_window(self, icon=None, item=None):
        if self.on_show_window:
            self.on_show_window()

    def _on_update_today(self, icon=None, item=None):
        if self.on_update_today:
            self.on_update_today()

    def _on_exit(self, icon=None, item=None):
        if self.icon:
            self.icon.stop()
        if self.on_exit:
            self.on_exit()

    def start(self):
        """Inicia o ícone da bandeja em uma thread secundária."""
        try:
            image = Image.open(str(ICON_PNG))
            self.icon = pystray.Icon(
                name="ChaveMNotifier",
                icon=image,
                title=f"{APP_NAME}",
                menu=self._create_menu()
            )
            tray_thread = threading.Thread(target=self.icon.run, daemon=True)
            tray_thread.start()
            logger.info("Ícone na bandeja do sistema iniciado com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao inicializar ícone da bandeja: {e}")

    def stop(self):
        """Para o ícone da bandeja."""
        if self.icon:
            try:
                self.icon.stop()
            except Exception:
                pass
