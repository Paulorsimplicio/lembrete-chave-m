#!/bin/bash
# Script de 1 clique para macOS
# Arquivos .command no Mac abrem com duplo clique diretamente pelo Finder!

cd "$(dirname "$0")"

echo "=========================================================="
echo "   Iniciando Lembrete Chave M (Foursys • Bradesco)       "
echo "=========================================================="
echo ""

# Verifica se o Python 3 está disponível no Mac
if ! command -v python3 &> /dev/null; then
    echo "Python 3 não foi encontrado no seu Mac."
    echo "Geralmente ele já vem instalado ou pode ser instalado via Terminal: xcode-select --install"
    read -p "Pressione Enter para sair..."
    exit 1
fi

# Cria o ambiente virtual se ainda não existir
if [ ! -d ".venv" ]; then
    echo "[1/2] Configurando ambiente local pela primeira vez..."
    python3 -m venv .venv
    ./.venv/bin/python3 -m pip install --quiet --upgrade pip
    ./.venv/bin/python3 -m pip install --quiet -r requirements.txt
    echo "[2/2] Tudo pronto!"
fi

echo "Abrindo o aplicativo..."
./.venv/bin/python3 main.py &
