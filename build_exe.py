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

    # Copia o Manual de Uso para a pasta dist
    manual_src = os.path.abspath("Manual_de_Uso.html")
    manual_dist = os.path.join("dist", "Manual_de_Uso.html")
    if os.path.exists(manual_src):
        shutil.copy(manual_src, manual_dist)

    import zipfile

    # No Windows: empacotar LembreteChaveM.exe e Manual_de_Uso.html em LembreteChaveM-Windows.zip
    if sys.platform.startswith("win"):
        exe_file = os.path.join("dist", "LembreteChaveM.exe")
        win_zip = os.path.join("dist", "LembreteChaveM-Windows.zip")
        if os.path.exists(exe_file):
            with zipfile.ZipFile(win_zip, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.write(exe_file, "LembreteChaveM.exe")
                if os.path.exists(manual_dist):
                    zf.write(manual_dist, "Manual_de_Uso.html")
            print(f"Pacote Windows gerado com executável e manual em: {win_zip}")

    # No macOS: compactar o .app e o manual preservando links simbólicos para distribuição
    elif sys.platform == "darwin":
        app_path = os.path.join("dist", "LembreteChaveM.app")
        zip_path = os.path.join("dist", "LembreteChaveM-MacOS.zip")
        if os.path.exists(app_path):
            import subprocess
            try:
                cmd = ["zip", "-r", "-y", "LembreteChaveM-MacOS.zip", "LembreteChaveM.app"]
                if os.path.exists(manual_dist):
                    cmd.append("Manual_de_Uso.html")
                subprocess.run(cmd, cwd="dist", check=True)
                print(f"Pacote macOS .app compactado com manual em: {zip_path}")
            except Exception as e:
                print(f"Aviso ao compactar .app no macOS: {e}")

    # No Linux: empacotar o binário e o manual em LembreteChaveM-Linux.zip
    else:
        bin_file = os.path.join("dist", "LembreteChaveM")
        linux_zip = os.path.join("dist", "LembreteChaveM-Linux.zip")
        script_file = os.path.abspath("iniciar_linux.sh")
        if os.path.exists(bin_file):
            with zipfile.ZipFile(linux_zip, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.write(bin_file, "LembreteChaveM")
                if os.path.exists(manual_dist):
                    zf.write(manual_dist, "Manual_de_Uso.html")
                if os.path.exists(script_file):
                    zf.write(script_file, "iniciar_linux.sh")
            print(f"Pacote Linux gerado com binário e manual em: {linux_zip}")

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
