import sys
import tkinter as tk
import webbrowser
from datetime import datetime, date
from pathlib import Path
from typing import Optional, Callable
import logging

import customtkinter as ctk
from PIL import Image

from src.config import (
    APP_NAME,
    APP_SUBTITLE,
    APP_VERSION,
    ICON_PNG,
    ICON_ICO,
    COLOR_PRIMARY,
    COLOR_ACCENT,
    COLOR_SAFE,
    COLOR_WARNING,
    COLOR_DANGER,
    COLOR_EXPIRED,
    BRADESCO_PASSWORD_URL,
)
from src.storage import Storage
from src.reminder_engine import calculate_status, MESSAGES_BY_THRESHOLD
from src.notifier import Notifier

logger = logging.getLogger(__name__)

# Configurações do CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MainWindow(ctk.CTk):
    def __init__(
        self,
        storage: Storage,
        notifier: Notifier,
        on_exit_callback: Optional[Callable] = None,
        on_status_change_callback: Optional[Callable[[str], None]] = None,
    ):
        super().__init__()

        self.storage = storage
        self.notifier = notifier
        self.on_exit_callback = on_exit_callback
        self.on_status_change_callback = on_status_change_callback

        # Configurações da Janela - Limpa, sem barra de rolagem
        self.title(f"{APP_NAME} - {APP_SUBTITLE}")

        self.resizable(True, True)
        self.minsize(450, 560)

        # Centralizado na tela
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        target_w = 480
        target_h = 600

        pos_x = max(0, (screen_w - target_w) // 2)
        pos_y = max(0, (screen_h - target_h) // 2)
        self.geometry(f"{target_w}x{target_h}+{pos_x}+{pos_y}")

        # Ícone da janela
        if sys.platform.startswith("win") and ICON_ICO.exists():
            try:
                self.iconbitmap(str(ICON_ICO))
            except Exception:
                pass

        # Intercepta o evento de fechamento da janela (X)
        self.protocol("WM_DELETE_WINDOW", self.on_window_close)

        # Monta os componentes fixos e o container central
        self._build_header()
        self._build_footer()

        # Container principal limpo (sem barra de rolagem, entre o cabeçalho e o rodapé)
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(side="top", fill="both", expand=True, padx=8, pady=(0, 2))

        self._build_status_card(self.main_container)
        self._build_action_card(self.main_container)

        # Atualiza a interface com os dados persistidos
        self.refresh_ui()

    def _build_header(self):
        """Cabeçalho com logo, título e badge de versão."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(side="top", fill="x", padx=16, pady=(10, 4))

        # Logo / Ícone
        try:
            pil_img = Image.open(str(ICON_PNG))
            ctk_icon = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(40, 40))
            logo_label = ctk.CTkLabel(header_frame, image=ctk_icon, text="")
            logo_label.pack(side="left", padx=(0, 12))
        except Exception:
            pass

        title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_container.pack(side="left", fill="both", expand=True)

        title_label = ctk.CTkLabel(
            title_container,
            text=APP_NAME,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#f8fafc"
        )
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            title_container,
            text=APP_SUBTITLE,
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8"
        )
        subtitle_label.pack(anchor="w")

        version_badge = ctk.CTkLabel(
            header_frame,
            text=f"v{APP_VERSION}",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#1e293b",
            text_color="#38bdf8",
            corner_radius=8,
            padx=8,
            pady=4
        )
        version_badge.pack(side="right", anchor="n")

    def _build_status_card(self, parent):
        """Card com o status atual de validade da chave M."""
        self.status_card = ctk.CTkFrame(parent, corner_radius=12, fg_color="#1e293b", border_width=1, border_color="#334155")
        self.status_card.pack(fill="x", padx=8, pady=4)

        # Status Pill (tag superior)
        self.status_pill = ctk.CTkLabel(
            self.status_card,
            text="● CARREGANDO...",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#0f172a",
            text_color=COLOR_SAFE,
            corner_radius=12,
            padx=12,
            pady=4
        )
        self.status_pill.pack(anchor="w", padx=16, pady=(8, 4))

        # Destaque de dias restantes
        days_box = ctk.CTkFrame(self.status_card, fg_color="transparent")
        days_box.pack(anchor="w", padx=16, pady=0)

        self.days_number_label = ctk.CTkLabel(
            days_box,
            text="--",
            font=ctk.CTkFont(size=38, weight="bold"),
            text_color="#ffffff"
        )
        self.days_number_label.pack(side="left", padx=(0, 8))

        self.days_text_label = ctk.CTkLabel(
            days_box,
            text="dias restantes\npara expirar",
            font=ctk.CTkFont(size=14),
            text_color="#94a3b8",
            justify="left"
        )
        self.days_text_label.pack(side="left")

        # Barra de progresso do ciclo
        self.progress_bar = ctk.CTkProgressBar(self.status_card, height=10, corner_radius=5)
        self.progress_bar.pack(fill="x", padx=20, pady=(8, 4))
        self.progress_bar.set(0.0)

        # Informações complementares (Datas e avisos)
        self.info_date_label = ctk.CTkLabel(
            self.status_card,
            text="Última troca: Não informada | Limite útil: --/--/----",
            font=ctk.CTkFont(size=12),
            text_color="#cbd5e1"
        )
        self.info_date_label.pack(anchor="w", padx=20, pady=(2, 2))

        # Banner de antecipação (quando cai em fim de semana ou feriado)
        self.adjustment_banner = ctk.CTkLabel(
            self.status_card,
            text="",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#fcd34d",
            fg_color="#451a03",
            corner_radius=6,
            padx=10,
            pady=3
        )

        # Regra de alertas ativos
        alerts_info = ctk.CTkLabel(
            self.status_card,
            text="🔔 Alertas automáticos programados para 5, 3, 2 e 1 dia antes.",
            font=ctk.CTkFont(size=11),
            text_color="#64748b"
        )
        alerts_info.pack(anchor="w", padx=20, pady=(4, 8))

    def _build_action_card(self, parent):
        """Card para registrar quando a senha foi trocada e link para o portal."""
        action_card = ctk.CTkFrame(parent, corner_radius=12, fg_color="#1e293b", border_width=1, border_color="#334155")
        action_card.pack(fill="x", padx=8, pady=4)

        action_title = ctk.CTkLabel(
            action_card,
            text="Acesso e Renovação da Chave M",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#f8fafc"
        )
        action_title.pack(anchor="w", padx=16, pady=(8, 6))

        # Botão: Acessar página de troca de senha no portal Bradesco
        btn_portal = ctk.CTkButton(
            action_card,
            text="🌐 Acessar Página de Troca de Senha (Bradesco)",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#dc2626",
            hover_color="#b91c1c",
            height=36,
            corner_radius=8,
            command=self.open_bradesco_portal
        )
        btn_portal.pack(fill="x", padx=16, pady=(0, 6))

        # Botão Rápido: Troquei Hoje
        btn_today = ctk.CTkButton(
            action_card,
            text="⚡ Já Troquei Minha Senha Hoje",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#0284c7",
            hover_color="#0369a1",
            height=34,
            corner_radius=8,
            command=self.set_changed_today
        )
        btn_today.pack(fill="x", padx=16, pady=(0, 6))

        # Opção manual de outra data
        manual_frame = ctk.CTkFrame(action_card, fg_color="transparent")
        manual_frame.pack(fill="x", padx=16, pady=(0, 6))

        lbl_manual = ctk.CTkLabel(
            manual_frame,
            text="Ou digite outra data (DD/MM/AAAA):",
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8"
        )
        lbl_manual.pack(anchor="w", pady=(0, 2))

        input_row = ctk.CTkFrame(manual_frame, fg_color="transparent")
        input_row.pack(fill="x")

        self.date_entry = ctk.CTkEntry(
            input_row,
            placeholder_text="Ex: 28/09/2026",
            font=ctk.CTkFont(size=13),
            height=32,
            corner_radius=8
        )
        self.date_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        btn_save_custom = ctk.CTkButton(
            input_row,
            text="Salvar Data",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#334155",
            hover_color="#475569",
            height=32,
            width=90,
            corner_radius=8,
            command=self.save_custom_date
        )
        btn_save_custom.pack(side="right")

        # Mensagem de confirmação / erro
        self.feedback_label = ctk.CTkLabel(
            action_card,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#10b981"
        )
        self.feedback_label.pack(anchor="w", padx=16, pady=(0, 6))

    def _build_footer(self):
        """Botões inferiores de utilidade."""
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(side="bottom", fill="x", padx=16, pady=(4, 10))

        btn_test_notif = ctk.CTkButton(
            footer_frame,
            text="🔔 Testar Notificação",
            font=ctk.CTkFont(size=12),
            fg_color="#1e293b",
            hover_color="#334155",
            text_color="#cbd5e1",
            height=34,
            corner_radius=8,
            command=self.test_notification
        )
        btn_test_notif.pack(side="left", padx=(0, 8))

        btn_manual = ctk.CTkButton(
            footer_frame,
            text="📖 Manual",
            font=ctk.CTkFont(size=12),
            fg_color="#1e293b",
            hover_color="#334155",
            text_color="#cbd5e1",
            width=80,
            height=34,
            corner_radius=8,
            command=self.open_manual
        )
        btn_manual.pack(side="left")

        btn_minimize = ctk.CTkButton(
            footer_frame,
            text="📥 Ocultar na Bandeja",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#0f766e",
            hover_color="#115e59",
            text_color="#f0fdfa",
            height=34,
            corner_radius=8,
            command=self.minimize_to_tray
        )
        btn_minimize.pack(side="right")

    def refresh_ui(self):
        """Recalcula e atualiza todos os componentes visuais."""
        last_date = self.storage.get_last_change_date()
        cycle_days = self.storage.get_cycle_days()
        status = calculate_status(last_date, cycle_days=cycle_days)

        if not status["has_date"]:
            self.status_pill.configure(
                text="● AGUARDANDO CONFIGURAÇÃO",
                text_color=COLOR_WARNING
            )
            self.days_number_label.configure(text="--", text_color="#94a3b8")
            self.days_text_label.configure(text="Nenhuma data registrada.\nClique abaixo para cadastrar.")
            self.progress_bar.set(0.0)
            self.progress_bar.configure(progress_color="#64748b")
            self.info_date_label.configure(text="Data de expiração não configurada.")
            self.adjustment_banner.pack_forget()
            status_text = "Sem data cadastrada"
        else:
            days = status["days_remaining"]
            deadline_str = status["effective_deadline"].strftime("%d/%m/%Y")
            exp_date_str = status["expiration_date"].strftime("%d/%m/%Y")
            last_date_str = status["last_change_date"].strftime("%d/%m/%Y")

            self.status_pill.configure(
                text=f"● {status['status_label'].upper()}",
                text_color=status["color"]
            )
            self.days_number_label.configure(
                text=str(max(0, days)),
                text_color=status["color"]
            )

            if days < 0:
                self.days_text_label.configure(
                    text=f"dias ATRASADA!\nPrazo limite era {deadline_str}",
                    text_color=COLOR_EXPIRED
                )
            elif days == 0:
                self.days_text_label.configure(
                    text=f"ÚLTIMO DIA ÚTIL!\nTroque hoje antes de expirar.",
                    text_color=COLOR_EXPIRED
                )
            else:
                self.days_text_label.configure(
                    text=f"dias úteis restantes\nPrazo limite: {deadline_str}",
                    text_color="#94a3b8"
                )

            self.progress_bar.set(status["progress"])
            self.progress_bar.configure(progress_color=status["color"])
            self.info_date_label.configure(
                text=f"Última troca: {last_date_str}  •  Limite Útil: {deadline_str}  (Expira: {exp_date_str})"
            )

            # Exibe aviso de antecipação caso o dia 29 tenha caído em fim de semana ou feriado
            if status["was_adjusted"]:
                raw_str = status["raw_deadline"].strftime("%d/%m")
                self.adjustment_banner.configure(
                    text=f"📅 Prazo antecipado de {raw_str} ({status['adjustment_reason']})"
                )
                self.adjustment_banner.pack(anchor="w", padx=20, pady=(2, 4), after=self.info_date_label)
            else:
                self.adjustment_banner.pack_forget()

            status_text = f"{days} dias restantes (Limite: {deadline_str})"

        if self.on_status_change_callback:
            self.on_status_change_callback(status_text)

    def set_changed_today(self):
        """Registra a data de hoje como a última troca."""
        today = date.today()
        self.storage.set_last_change_date(today)
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, today.strftime("%d/%m/%Y"))
        self.feedback_label.configure(
            text=f"✅ Data atualizada com sucesso para hoje ({today.strftime('%d/%m/%Y')})!",
            text_color="#10b981"
        )
        self.refresh_ui()

    def save_custom_date(self):
        """Salva a data digitada manualmente pelo usuário."""
        raw_text = self.date_entry.get().strip()
        if not raw_text:
            self.feedback_label.configure(
                text="⚠️ Por favor, digite uma data válida (ex: 28/09/2026).",
                text_color=COLOR_WARNING
            )
            return

        try:
            parsed_date = datetime.strptime(raw_text, "%d/%m/%Y").date()
            if parsed_date > date.today():
                self.feedback_label.configure(
                    text="⚠️ A data da troca não pode ser no futuro!",
                    text_color=COLOR_WARNING
                )
                return

            self.storage.set_last_change_date(parsed_date)
            self.feedback_label.configure(
                text=f"✅ Data registrada: {parsed_date.strftime('%d/%m/%Y')}",
                text_color="#10b981"
            )
            self.refresh_ui()
        except ValueError:
            self.feedback_label.configure(
                text="❌ Formato inválido! Use o padrão DD/MM/AAAA.",
                text_color=COLOR_DANGER
            )

    def open_bradesco_portal(self):
        """Abre a página oficial de troca de senha Bradesco no navegador padrão."""
        try:
            webbrowser.open(BRADESCO_PASSWORD_URL)
            self.feedback_label.configure(
                text="🌐 Abrindo portal de troca de senha no navegador...",
                text_color="#38bdf8"
            )
        except Exception as e:
            logger.error(f"Erro ao abrir navegador: {e}")
            self.feedback_label.configure(
                text="⚠️ Não foi possível abrir o navegador automaticamente.",
                text_color=COLOR_WARNING
            )

    def test_notification(self):
        """Dispara a notificação correspondente à situação atual de expiração da chave M do funcionário."""
        last_date = self.storage.get_last_change_date()
        cycle_days = self.storage.get_cycle_days()
        status = calculate_status(last_date, cycle_days=cycle_days)

        if not status["has_date"]:
            title = "Lembrete Chave M | Configuração Pendente"
            message = "Nenhuma data registrada. Abra o aplicativo para cadastrar a data da última troca de senha."
        else:
            days = status["days_remaining"]
            deadline_str = status["effective_deadline"].strftime("%d/%m/%Y")
            if days < 0:
                title = "🚨 URGENTE: Chave M Vencida!"
                message = f"O prazo útil de troca venceu há {abs(days)} dia(s) (limite: {deadline_str})! Troque imediatamente no portal Bradesco."
            elif days == 0:
                title = "🚨 ÚLTIMO DIA ÚTIL: Troque Hoje!"
                message = f"Hoje ({deadline_str}) é o último dia útil permitido para trocar sua chave M! Acesse o portal Bradesco agora."
            elif days in MESSAGES_BY_THRESHOLD:
                alert_info = MESSAGES_BY_THRESHOLD[days]
                title = alert_info["title"]
                message = alert_info["message"]
            elif days == 4:
                title = "Aviso Chave M (4 dias úteis)"
                message = f"Faltam 4 dias úteis para a data limite de troca da chave M ({deadline_str}). Planeje a troca."
            else:
                title = f"Lembrete Chave M | Status Seguro ({days} dias)"
                message = f"Sua chave M está segura por mais {days} dias úteis (data limite útil: {deadline_str})."

        self.notifier.notify(title=title, message=message, timeout=12)
        self.feedback_label.configure(
            text=f"🔔 Notificação enviada: {title}",
            text_color="#38bdf8"
        )

    def open_manual(self):
        """Abre o manual de uso do aplicativo no navegador."""
        manual_candidates = [
            Path(__file__).resolve().parent.parent / "Manual_de_Uso.html",
            Path(sys.executable).parent / "Manual_de_Uso.html",
            Path.cwd() / "Manual_de_Uso.html",
        ]
        for candidate in manual_candidates:
            if candidate.exists():
                try:
                    webbrowser.open(candidate.as_uri())
                    self.feedback_label.configure(
                        text="📖 Manual de uso aberto no navegador!",
                        text_color="#38bdf8"
                    )
                    return
                except Exception as e:
                    logger.error(f"Erro ao abrir manual local: {e}")

        # Fallback online
        webbrowser.open("https://github.com/Paulorsimplicio/lembrete-chave-m#readme")
        self.feedback_label.configure(
            text="📖 Abrindo documentação online...",
            text_color="#38bdf8"
        )

    def minimize_to_tray(self):
        """Oculta a janela principal para a bandeja do sistema."""
        self.withdraw()
        self.notifier.notify(
            title=f"{APP_NAME} Minimizado",
            message="O gadget foi minimizado na bandeja e está sendo executado em segundo plano.",
            timeout=5
        )

    def show_window(self):
        """Restaura a janela na tela e traz para o primeiro plano."""
        self.deiconify()
        self.lift()
        self.focus_force()
        self.refresh_ui()

    def on_window_close(self):
        """Ação ao clicar no botão fechar (X): sempre minimiza para a bandeja como padrão."""
        self.minimize_to_tray()
