#!/bin/bash
# Script de 1 clique para Linux
cd "$(dirname "$0")"

echo "=========================================================="
echo "   Iniciando Lembrete Chave M (Foursys • Bradesco)       "
echo "=========================================================="
echo ""

if ! command -v python3 &> /dev/null; then
    echo "Python 3 não foi encontrado. Por favor, instale o pacote python3."
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "[1/2] Configurando dependências locais pela primeira vez..."
    python3 -m venv .venv
    ./.venv/bin/python3 -m pip install --quiet --upgrade pip
    ./.venv/bin/python3 -m pip install --quiet -r requirements.txt
    echo "[2/2] Configuração concluída!"
fi

echo "Abrindo o aplicativo..."
./.venv/bin/python3 main.py &
