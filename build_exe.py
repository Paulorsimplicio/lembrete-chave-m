import os
import sys
import shutil
import PyInstaller.__main__

def build():
    print("Iniciando compilação do executável LembreteChaveM...")

    sep = ";" if sys.platform.startswith("win") else ":"
    
    if sys.platform.startswith("win"):
        icon_arg = "assets/icon.ico"
    elif sys.platform == "darwin":
        icon_arg = "assets/icon.icns" if os.path.exists("assets/icon.icns") else "assets/icon.png"
    else:
        icon_arg = "assets/icon.png"

    # Argumentos do PyInstaller com otimizações de performance
    args = [
        "main.py",
        "--name=LembreteChaveM",
        "--noconsole",
        f"--icon={icon_arg}",
        f"--add-data=assets{sep}assets",
        "--clean",
        "--noupx",          # UPX desativado para carregamento 2x a 3x mais rápido em SSDs
        "--optimize=2",      # Otimização máxima de bytecode Python (.pyo)
        "--hidden-import=customtkinter",
        "--hidden-import=PIL",
        "--hidden-import=pystray",
        "--hidden-import=plyer",
        "--hidden-import=src.holidays",
        "--hidden-import=src.single_instance",
        # Exclusão de módulos pesados não utilizados para acelerar a descompactação
        "--exclude-module=unittest",
        "--exclude-module=pydoc",
        "--exclude-module=doctest",
        "--exclude-module=test",
        "--exclude-module=sqlite3",
        "--exclude-module=asyncio",
        "--exclude-module=xmlrpc",
        "--exclude-module=distutils",
        "--exclude-module=setuptools",
        "--exclude-module=pkg_resources",
        "--exclude-module=multiprocessing",
        "--exclude-module=concurrent",
        "--exclude-module=tkinter.test",
    ]

    # No Windows e Linux usamos --onefile para gerar um único binário executável
    # No macOS usamos --windowed para gerar um pacote nativo LembreteChaveM.app
    if sys.platform == "darwin":
        args.append("--windowed")
    else:
        args.append("--onefile")

    PyInstaller.__main__.run(args)

    # No macOS, compactar o .app preservando links simbólicos para distribuição
    if sys.platform == "darwin":
        app_path = os.path.join("dist", "LembreteChaveM.app")
        zip_path = os.path.join("dist", "LembreteChaveM-MacOS.zip")
        if os.path.exists(app_path):
            import subprocess
            try:
                subprocess.run(["zip", "-r", "-y", "LembreteChaveM-MacOS.zip", "LembreteChaveM.app"], cwd="dist", check=True)
                print(f"Pacote macOS .app compactado em: {zip_path}")
            except Exception as e:
                print(f"Aviso ao compactar .app no macOS: {e}")

    print("\n" + "=" * 60)
    print("Compilação concluída!")
    if sys.platform.startswith("win"):
        exe_path = os.path.abspath("dist/LembreteChaveM.exe")
        print(f"Executável gerado em: {exe_path}")
    elif sys.platform == "darwin":
        app_path = os.path.abspath("dist/LembreteChaveM.app")
        print(f"Aplicativo macOS gerado em: {app_path}")
    else:
        bin_path = os.path.abspath("dist/LembreteChaveM")
        print(f"Binário gerado em: {bin_path}")
    print("=" * 60)

if __name__ == "__main__":
    build()
