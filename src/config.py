import os
import sys
from pathlib import Path

APP_NAME = "Lembrete Chave M"
APP_SUBTITLE = "Foursys | Controle de Acesso Bradesco"
APP_VERSION = "1.4.0"

# Regra de negócio
DEFAULT_CYCLE_DAYS = 30   # Expiração técnica
MAX_CYCLE_DAY = 29        # Limite máximo seguro (trocar até o 29º dia)
ALERT_THRESHOLDS = [5, 3, 2, 1, 0]  # Dias restantes para disparar alerta (5, 3, 2, 1 dia antes e dia 0)

# Link para o portal oficial de troca de senha Bradesco (SailPoint IdentityNow)
BRADESCO_PASSWORD_URL = "https://bradesco.identitynow.com/r/default/password-management"

# Intervalo de checagem em segundo plano (em segundos)
# Checa a cada 30 minutos
BACKGROUND_CHECK_INTERVAL = 1800

# Diretório e arquivo de dados locais (100% offline no perfil do usuário)
DATA_DIR = Path.home() / ".foursys_chave_m"
DATA_FILE = DATA_DIR / "config.json"

# Localização dos recursos estáticos (compatível com PyInstaller)
if getattr(sys, "frozen", False):
    # Executável empacotado pelo PyInstaller
    BASE_DIR = Path(sys._MEIPASS)
else:
    # Em desenvolvimento
    BASE_DIR = Path(__file__).resolve().parent.parent

ASSETS_DIR = BASE_DIR / "assets"
ICON_PNG = ASSETS_DIR / "icon.png"
ICON_ICO = ASSETS_DIR / "icon.ico"

# Paleta de cores moderna
COLOR_PRIMARY = "#0284c7"      # Azul Céu Corporativo
COLOR_ACCENT = "#06b6d4"       # Ciano Foursys
COLOR_SAFE = "#10b981"         # Verde Esmeralda (Seguro > 7 dias)
COLOR_WARNING = "#f59e0b"      # Amarelo/Laranja (Atenção 4-7 dias)
COLOR_DANGER = "#ef4444"       # Vermelho (Crítico 1-3 dias)
COLOR_EXPIRED = "#b91c1c"      # Vermelho Escuro (Expirado <= 0 dias)
