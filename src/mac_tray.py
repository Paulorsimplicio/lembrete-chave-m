import sys
import socket
import logging
import webbrowser
from PIL import Image
import pystray
from pystray import MenuItem as item
from src.config import ICON_PNG, APP_NAME, BRADESCO_PASSWORD_URL

logger = logging.getLogger(__name__)

PORT = 58421


def _send_socket_cmd(cmd: bytes):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(1.5)
        client.connect(("127.0.0.1", PORT))
        client.sendall(cmd)
        client.close()
    except Exception as e:
        logger.debug(f"Erro ao enviar comando socket do tray helper: {e}")


def _open_main_window(icon=None, item=None):
    _send_socket_cmd(b"SHOW")
    try:
        import subprocess
        subprocess.run(["osascript", "-e", 'tell application "LembreteChaveM" to activate'], check=False)
    except Exception:
        pass


def _update_today(icon=None, item=None):
    _send_socket_cmd(b"UPDATE_TODAY")
    _open_main_window()


def _open_portal(icon=None, item=None):
    try:
        webbrowser.open(BRADESCO_PASSWORD_URL)
    except Exception as e:
        logger.error(f"Erro ao abrir portal Bradesco: {e}")


def _exit_app(icon=None, item=None):
    _send_socket_cmd(b"SHUTDOWN")
    if icon:
        icon.stop()
    sys.exit(0)


def run_mac_tray_helper():
    """Roda na thread principal do processo auxiliar para criar o item na Status Bar do macOS."""
    try:
        import AppKit
        # NSApplicationActivationPolicyAccessory (1): roda como acessório da barra sem duplicar ícone no Dock
        AppKit.NSApplication.sharedApplication().setActivationPolicy_(AppKit.NSApplicationActivationPolicyAccessory)
    except Exception as e:
        logger.debug(f"Não foi possível ajustar política de ativação do AppKit: {e}")

    try:
        image = Image.open(str(ICON_PNG))
    except Exception as e:
        logger.error(f"Erro ao carregar ícone para a Status Bar do macOS: {e}")
        return

    menu = pystray.Menu(
        item(APP_NAME, None, enabled=False),
        pystray.Menu.SEPARATOR,
        item("Abrir Painel", _open_main_window, default=True),
        item("Troquei Minha Senha Hoje", _update_today),
        item("Ir para Portal de Troca de Senha", _open_portal),
        pystray.Menu.SEPARATOR,
        item("Sair", _exit_app)
    )

    icon = pystray.Icon(
        name="LembreteChaveM_Tray",
        icon=image,
        title=APP_NAME,
        menu=menu
    )

    icon.run()

