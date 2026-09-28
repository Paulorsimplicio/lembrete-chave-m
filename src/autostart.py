import os
import sys
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

APP_KEY = "LembreteChaveMFoursys"

def get_executable_command() -> str:
    """Retorna o comando adequado para iniciar a aplicação no boot."""
    if getattr(sys, "frozen", False):
        # Executável compilado (.exe ou binário)
        return f'"{sys.executable}"'
    else:
        # Script em execução via interpretador pythonw ou python
        script_path = Path(__file__).resolve().parent.parent / "main.py"
        # Se no Windows, preferir pythonw.exe para não abrir janela de terminal preta
        python_exe = sys.executable
        if sys.platform.startswith("win") and "python.exe" in python_exe.lower():
            pythonw_candidate = python_exe.lower().replace("python.exe", "pythonw.exe")
            if os.path.exists(pythonw_candidate):
                python_exe = pythonw_candidate
        return f'"{python_exe}" "{script_path}"'


def is_autostart_enabled() -> bool:
    """Verifica se a inicialização com o sistema está habilitada."""
    if sys.platform.startswith("win"):
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ
            )
            try:
                winreg.QueryValueEx(key, APP_KEY)
                return True
            except FileNotFoundError:
                return False
            finally:
                winreg.CloseKey(key)
        except Exception as e:
            logger.debug(f"Erro ao verificar autostart Windows: {e}")
            return False

    elif sys.platform.startswith("linux"):
        desktop_file = Path.home() / ".config" / "autostart" / f"{APP_KEY}.desktop"
        return desktop_file.exists()

    elif sys.platform == "darwin":
        plist_file = Path.home() / "Library" / "LaunchAgents" / f"com.foursys.{APP_KEY}.plist"
        return plist_file.exists()

    return False


def set_autostart(enable: bool) -> bool:
    """Ativa ou desativa a inicialização com o sistema."""
    cmd = get_executable_command()

    if sys.platform.startswith("win"):
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            if enable:
                winreg.SetValueEx(key, APP_KEY, 0, winreg.REG_SZ, cmd)
                logger.info(f"Autostart Windows habilitado com: {cmd}")
            else:
                try:
                    winreg.DeleteValue(key, APP_KEY)
                    logger.info("Autostart Windows desabilitado.")
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
            return True
        except Exception as e:
            logger.error(f"Erro ao definir autostart Windows: {e}")
            return False

    elif sys.platform.startswith("linux"):
        desktop_dir = Path.home() / ".config" / "autostart"
        desktop_file = desktop_dir / f"{APP_KEY}.desktop"
        try:
            if enable:
                desktop_dir.mkdir(parents=True, exist_ok=True)
                content = f"""[Desktop Entry]
Type=Application
Exec={cmd}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=Lembrete Chave M
Comment=Lembrete de expiração Chave M Bradesco
"""
                desktop_file.write_text(content, encoding="utf-8")
            else:
                if desktop_file.exists():
                    desktop_file.unlink()
            return True
        except Exception as e:
            logger.error(f"Erro ao configurar autostart Linux: {e}")
            return False

    elif sys.platform == "darwin":
        agent_dir = Path.home() / "Library" / "LaunchAgents"
        plist_file = agent_dir / f"com.foursys.{APP_KEY}.plist"
        try:
            if enable:
                agent_dir.mkdir(parents=True, exist_ok=True)
                content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.foursys.{APP_KEY}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{cmd}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""
                plist_file.write_text(content, encoding="utf-8")
            else:
                if plist_file.exists():
                    plist_file.unlink()
            return True
        except Exception as e:
            logger.error(f"Erro ao configurar autostart macOS: {e}")
            return False

    return False
