import os
import sys
import logging
from pathlib import Path
from src.config import ICON_ICO, ICON_PNG, APP_NAME

logger = logging.getLogger(__name__)

class Notifier:
    def __init__(self):
        self.app_name = APP_NAME
        self.icon_path = self._resolve_icon_path()

    def _resolve_icon_path(self) -> str:
        """Determina o caminho do ícone adequado para o sistema operacional."""
        if sys.platform.startswith("win"):
            if ICON_ICO.exists():
                return str(ICON_ICO.resolve())
        if ICON_PNG.exists():
            return str(ICON_PNG.resolve())
        return ""

    def notify(self, title: str, message: str, timeout: int = 10) -> bool:
        """Dispara uma notificação nativa do sistema operacional."""
        # 1. Tenta via biblioteca plyer
        try:
            from plyer import notification
            notification.notify(
                title=title,
                message=message,
                app_name=self.app_name,
                app_icon=self.icon_path if self.icon_path else None,
                timeout=timeout,
            )
            logger.info(f"Notificação enviada com sucesso: [{title}] {message}")
            return True
        except Exception as e:
            logger.warning(f"Falha ao enviar notificação via plyer: {e}")

        # 2. Fallback específico para Windows se plyer falhar
        if sys.platform.startswith("win"):
            try:
                # Utiliza comando PowerShell com BurntToast ou Windows.UI.Notifications
                ps_script = f"""
                [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
                $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
                $texts = $template.GetElementsByTagName("text")
                $texts[0].AppendChild($template.CreateTextNode("{title}")) > $null
                $texts[1].AppendChild($template.CreateTextNode("{message}")) > $null
                $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
                [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("{self.app_name}").Show($toast)
                """
                import subprocess
                subprocess.run(
                    ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                    capture_output=True,
                    timeout=5,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
                )
                return True
            except Exception as ps_err:
                logger.error(f"Fallback do Windows falhou: {ps_err}")

        # 3. Fallback no Linux usando notify-send
        if sys.platform.startswith("linux"):
            try:
                import subprocess
                args = ["notify-send", title, message]
                if self.icon_path:
                    args.extend(["-i", self.icon_path])
                subprocess.run(args, check=False)
                return True
            except Exception:
                pass

        # 4. Fallback no macOS usando osascript
        if sys.platform == "darwin":
            try:
                import subprocess
                script = f'display notification "{message}" with title "{title}"'
                subprocess.run(["osascript", "-e", script], check=False)
                return True
            except Exception:
                pass

        return False

    def send_test_notification(self) -> bool:
        """Envia uma notificação de teste para o usuário confirmar o funcionamento."""
        return self.notify(
            title="Lembrete Chave M | Teste",
            message="As notificações locais estão funcionando perfeitamente em sua máquina!"
        )
