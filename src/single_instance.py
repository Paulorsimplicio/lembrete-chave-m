import socket
import threading
import logging
import tkinter as tk
from tkinter import messagebox
from typing import Optional, Callable

logger = logging.getLogger(__name__)

PORT = 58421  # Porta local para controle de instância única


class SingleInstanceManager:
    def __init__(self, on_activate_callback: Optional[Callable] = None):
        self.on_activate_callback = on_activate_callback
        self.server_socket: Optional[socket.socket] = None
        self.is_running = False

    def is_already_running(self, show_popup: bool = True) -> bool:
        """
        Verifica se já existe outra instância do aplicativo em execução.
        Se existir, envia um sinal para a instância existente restaurar a janela
        e exibe uma mensagem informativa.
        Retorna True se JÁ ESTÁ em execução, ou False se for a PRIMEIRA instância.
        """
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Tenta prender a porta local
            self.server_socket.bind(("127.0.0.1", PORT))
            self.server_socket.listen(2)
            self.is_running = True
            
            # Inicia thread de escuta para reativar a janela se o usuário tentar abrir de novo
            listener_thread = threading.Thread(target=self._listen_for_pings, daemon=True)
            listener_thread.start()
            return False

        except OSError:
            # Porta ocupada -> Já existe outra instância rodando!
            logger.info("Outra instância do Lembrete Chave M já está em execução.")
            
            # Avisa a instância existente para restaurar a janela na tela
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.settimeout(2.0)
                client.connect(("127.0.0.1", PORT))
                client.sendall(b"SHOW")
                client.close()
            except Exception as e:
                logger.debug(f"Não foi possível sinalizar instância existente: {e}")

            # Exibe mensagem informativa ao usuário se solicitado
            if show_popup:
                self._show_already_running_message()
            return True

    def _listen_for_pings(self):
        """Escuta sinais de novas tentativas de abertura e traz a janela para frente."""
        while self.is_running and self.server_socket:
            try:
                conn, _ = self.server_socket.accept()
                data = conn.recv(32)
                conn.close()
                if data == b"SHOW" and self.on_activate_callback:
                    logger.info("Recebido comando para restaurar janela existente.")
                    self.on_activate_callback()
            except Exception:
                break

    def _show_already_running_message(self):
        """Exibe popup informando que o gadget já está aberto."""
        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            messagebox.showinfo(
                "Lembrete Chave M",
                "O Lembrete Chave M já está em execução!\n\n"
                "Verifique o ícone ao lado do relógio (bandeja do sistema) ou na barra de tarefas.",
                parent=root
            )
            root.destroy()
        except Exception as e:
            logger.error(f"Erro ao exibir mensagem de instância existente: {e}")

    def close(self):
        """Fecha o socket liberando a porta."""
        self.is_running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass
            self.server_socket = None
