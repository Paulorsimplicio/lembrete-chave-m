@echo off
echo ========================================================
echo   Gerador do Executavel: Lembrete Chave M (Foursys)
echo ========================================================
echo.

IF NOT EXIST ".venv\Scripts\python.exe" (
    echo [1/3] Criando ambiente virtual...
    python -m venv .venv
    echo [2/3] Instalando dependencias...
    .\.venv\Scripts\python -m pip install -r requirements.txt
) ELSE (
    echo Ambiente virtual encontrado.
)

echo.
echo [3/3] Compilando executavel standalone...
.\.venv\Scripts\python build_exe.py

echo.
echo Concluido! O executavel esta na pasta "dist\LembreteChaveM.exe".
pause
