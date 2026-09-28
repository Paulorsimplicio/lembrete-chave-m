import os
import sys
import shutil
import PyInstaller.__main__

def build():
    print("Iniciando compilação do executável LembreteChaveM...")

    sep = ";" if sys.platform.startswith("win") else ":"
    icon_arg = "assets/icon.ico" if sys.platform.startswith("win") else "assets/icon.png"

    # Argumentos do PyInstaller
    args = [
        "main.py",
        "--name=LembreteChaveM",
        "--onefile",
        "--noconsole",
        f"--icon={icon_arg}",
        f"--add-data=assets{sep}assets",
        "--clean",
        "--hidden-import=customtkinter",
        "--hidden-import=PIL",
        "--hidden-import=pystray",
        "--hidden-import=plyer",
        "--hidden-import=src.holidays",
    ]

    PyInstaller.__main__.run(args)

    print("\n" + "=" * 60)
    print("Compilação concluída!")
    if sys.platform.startswith("win"):
        exe_path = os.path.abspath("dist/LembreteChaveM.exe")
        print(f"Executável gerado em: {exe_path}")
    else:
        bin_path = os.path.abspath("dist/LembreteChaveM")
        print(f"Binário gerado em: {bin_path}")
    print("=" * 60)

if __name__ == "__main__":
    build()
