import socket
import threading
import logging
import sys
import os
import time
import re
from typing import Optional, Callable, Tuple

logger = logging.getLogger(__name__)

PORT = 58421  # Porta local para controle de instância única


def parse_version(v_str: str) -> Tuple[int, ...]:
    """Converte string de versão (ex: 'v1.4.0' ou '1.4.0') em tupla de inteiros para comparação."""
    if not v_str:
        return (0, 0, 0)
    clean = v_str.strip().lstrip('v')
    parts = re.findall(r'\d+', clean)
    return tuple(int(p) for p in parts) if parts else (0, 0, 0)


class SingleInstanceManager:
    def __init__(
        self,
        on_activate_callback: Optional[Callable] = None,
        on_upgrade_requested_callback: Optional[Callable] = None,
        port: int = PORT,
        current_version: str = "1.0.0"
    ):
        self.on_activate_callback = on_activate_callback
        self.on_upgrade_requested_callback = on_upgrade_requested_callback
        self.port = port
        self.current_version = current_version
        self.server_socket: Optional[socket.socket] = None
        self.is_running = False
        
        # Flags sobre substituição de versão
        self.was_upgraded = False
        self.replaced_version: Optional[str] = None

    def is_already_running(self, show_popup: bool = True) -> bool:
        """
        Verifica se já existe outra instância do aplicativo em execução.
        Se existir:
        1. Consulta a versão da instância em execução via socket.
        2. Se a versão deste executável for MAIS NOVA que a vigente, solicita
           que a antiga se encerre de forma limpa, assume a porta e continua a execução.
        3. Se a versão for IGUAL ou ANTERIOR, sinaliza para restaurar a janela existente
           e retorna True (indicando que este processo duplicado deve encerrar).
        """
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if not sys.platform.startswith("win"):
                self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            self.server_socket.bind(("127.0.0.1", self.port))
            self.server_socket.listen(2)
            self.server_socket.settimeout(0.5)
            self.is_running = True
            
            listener_thread = threading.Thread(target=self._listen_for_pings, daemon=True)
            listener_thread.start()
            return False

        except OSError:
            if self.server_socket:
                try:
                    self.server_socket.close()
                except Exception:
                    pass
                self.server_socket = None

            # Outra instância detectada na porta
            logger.info("Outra instância do Lembrete Chave M detectada em execução.")
            
            # Consulta a versão da instância que já está rodando
            running_version = self._query_running_version()
            logger.info(f"Versão em execução: {running_version} | Versão deste executável: {self.current_version}")

            my_ver_tuple = parse_version(self.current_version)
            run_ver_tuple = parse_version(running_version) if running_version else (0, 0, 0)

            # Se este executável for mais recente que o em execução: SUBSTITUIR!
            if my_ver_tuple > run_ver_tuple:
                logger.info(
                    f"Nova versão detectada ({self.current_version} > {running_version}). "
                    "Solicitando encerramento da versão anterior para assumir a execução..."
                )
                if self._request_old_instance_shutdown():
                    # Aguarda até 3 segundos pela liberação da porta pela instância antiga
                    for _ in range(30):
                        time.sleep(0.1)
                        try:
                            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            if not sys.platform.startswith("win"):
                                self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                            self.server_socket.bind(("127.0.0.1", self.port))
                            self.server_socket.listen(2)
                            self.server_socket.settimeout(0.5)
                            self.is_running = True
                            
                            listener_thread = threading.Thread(target=self._listen_for_pings, daemon=True)
                            listener_thread.start()
                            
                            self.was_upgraded = True
                            self.replaced_version = running_version
                            logger.info(f"Instância anterior (v{running_version}) substituída com sucesso pela v{self.current_version}!")
                            return False
                        except OSError:
                            continue

            # Se for versão igual ou inferior, sinaliza para trazer a janela existente para frente
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.settimeout(1.0)
                client.connect(("127.0.0.1", self.port))
                client.sendall(b"SHOW")
                client.close()
            except Exception as e:
                logger.debug(f"Não foi possível sinalizar instância existente: {e}")

            if show_popup:
                self._show_already_running_message(running_version)
            return True

    def _query_running_version(self) -> Optional[str]:
        """Pergunta à instância em execução qual é a versão dela."""
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(1.5)
            client.connect(("127.0.0.1", self.port))
            client.sendall(b"GET_VERSION")
            data = client.recv(64).decode("utf-8", errors="ignore").strip()
            client.close()
            if data.startswith("VERSION:"):
                return data.replace("VERSION:", "").strip()
        except Exception as e:
            logger.debug(f"Falha ao consultar versão da instância ativa: {e}")
        return None

    def _request_old_instance_shutdown(self) -> bool:
        """Envia comando para a instância antiga fechar para dar lugar à versão mais nova."""
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(2.0)
            client.connect(("127.0.0.1", self.port))
            client.sendall(b"SHUTDOWN_FOR_UPGRADE")
            client.close()
            return True
        except Exception as e:
            logger.warning(f"Erro ao solicitar shutdown da instância anterior: {e}")
            return False

    def _listen_for_pings(self):
        """Escuta comandos enviados por outras instâncias."""
        while self.is_running and self.server_socket:
            try:
                conn, _ = self.server_socket.accept()
            except (socket.timeout, OSError):
                continue
            except Exception:
                break

            try:
                data = conn.recv(64)
                if data == b"GET_VERSION":
                    conn.sendall(f"VERSION:{self.current_version}".encode("utf-8"))
                    conn.close()
                elif data == b"SHUTDOWN_FOR_UPGRADE":
                    conn.close()
                    logger.info("Comando de encerramento recebido de versão mais recente. Fechando instância antiga...")
                    self.close()
                    if self.on_upgrade_requested_callback:
                        self.on_upgrade_requested_callback()
                    break
                elif data == b"SHOW":
                    conn.close()
                    if self.on_activate_callback:
                        logger.info("Recebido comando para restaurar janela existente.")
                        self.on_activate_callback()
                else:
                    conn.close()
            except Exception:
                pass

    def _show_already_running_message(self, running_version: Optional[str] = None):
        """Exibe popup informando que o gadget já está aberto."""
        if sys.platform.startswith("linux") and not os.environ.get("DISPLAY"):
            logger.info("Sem display gráfico (DISPLAY ausente); ignorando popup.")
            return

        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            ver_text = f" (versão {running_version})" if running_version else ""
            messagebox.showinfo(
                "Lembrete Chave M",
                f"O Lembrete Chave M{ver_text} já está aberto no seu computador!\n\n"
                "Verifique o ícone ao lado do relógio do sistema (bandeja)."
            )
            root.destroy()
        except Exception as e:
            logger.debug(f"Não foi possível exibir popup informativo: {e}")

    def close(self):
        """Encerra o listener de instância única."""
        self.is_running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass
            self.server_socket = None
