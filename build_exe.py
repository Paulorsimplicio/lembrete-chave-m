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
    # e --target-arch=universal2 para suportar nativamente tanto Intel (x86_64) quanto Apple Silicon (arm64)
    if sys.platform == "darwin":
        args.append("--windowed")
        args.append("--target-arch=universal2")
    else:
        args.append("--onefile")

    PyInstaller.__main__.run(args)

    # Copia o Manual de Uso para a pasta dist
    manual_src = os.path.abspath("Manual_de_Uso.html")
    manual_dist = os.path.join("dist", "Manual_de_Uso.html")
    if os.path.exists(manual_src):
        shutil.copy(manual_src, manual_dist)

    from src.config import APP_VERSION
    ver_tag = f"v{APP_VERSION}"

    import zipfile

    # No Windows: empacotar apenas o executável versionado e Manual_de_Uso.html em LembreteChaveM-Windows.zip e versionado
    if sys.platform.startswith("win"):
        exe_file = os.path.join("dist", "LembreteChaveM.exe")
        ver_exe_name = f"LembreteChaveM-{ver_tag}.exe"
        ver_exe_file = os.path.join("dist", ver_exe_name)
        if os.path.exists(exe_file):
            shutil.copy(exe_file, ver_exe_file)

        win_zip = os.path.join("dist", "LembreteChaveM-Windows.zip")
        ver_win_zip = os.path.join("dist", f"LembreteChaveM-Windows-{ver_tag}.zip")
        if os.path.exists(exe_file):
            for zpath in (win_zip, ver_win_zip):
                with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
                    zf.write(exe_file, ver_exe_name)
                    if os.path.exists(manual_dist):
                        zf.write(manual_dist, "Manual_de_Uso.html")
            print(f"Pacotes Windows gerados em: {win_zip} e {ver_win_zip}")

    # No macOS: gerar instalador .pkg e pacote de distribuição
    elif sys.platform == "darwin":
        app_path = os.path.join("dist", "LembreteChaveM.app")
        pkg_file = os.path.join("dist", "LembreteChaveM-MacOS.pkg")
        ver_pkg_file = os.path.join("dist", f"LembreteChaveM-MacOS-{ver_tag}.pkg")
        if os.path.exists(app_path):
            # Injeta metadata de versão e bundle no Info.plist do .app
            info_plist_path = os.path.join(app_path, "Contents", "Info.plist")
            if os.path.exists(info_plist_path):
                try:
                    import plistlib
                    with open(info_plist_path, "rb") as fp:
                        plist_data = plistlib.load(fp)
                    plist_data["CFBundleShortVersionString"] = APP_VERSION
                    plist_data["CFBundleVersion"] = APP_VERSION
                    plist_data["CFBundleName"] = "LembreteChaveM"
                    plist_data["CFBundleDisplayName"] = "Lembrete Chave M"
                    plist_data["CFBundleIdentifier"] = "br.com.foursys.lembretechavem"
                    with open(info_plist_path, "wb") as fp:
                        plistlib.dump(plist_data, fp)
                    print(f"Info.plist atualizado com versao {APP_VERSION}")
                except Exception as e:
                    print(f"Aviso ao atualizar Info.plist: {e}")

            import subprocess
            try:
                # Gera o instalador .pkg apontando para instalar diretamente em /Applications
                cmd_pkg = [
                    "pkgbuild",
                    "--component", "LembreteChaveM.app",
                    "--install-location", "/Applications",
                    "--version", APP_VERSION,
                    "LembreteChaveM-MacOS.pkg"
                ]
                subprocess.run(cmd_pkg, cwd="dist", check=True)
                shutil.copy(pkg_file, ver_pkg_file)
                print(f"Instaladores macOS (.pkg) gerados: {pkg_file} e {ver_pkg_file}")
            except Exception as e:
                print(f"Aviso ao gerar pacote .pkg no macOS: {e}")

    # No Linux: empacotar o binário versionado e o manual em LembreteChaveM-Linux.zip
    else:
        bin_file = os.path.join("dist", "LembreteChaveM")
        ver_bin_name = f"LembreteChaveM-{ver_tag}"
        ver_bin_file = os.path.join("dist", ver_bin_name)
        if os.path.exists(bin_file):
            shutil.copy(bin_file, ver_bin_file)

        linux_zip = os.path.join("dist", "LembreteChaveM-Linux.zip")
        ver_linux_zip = os.path.join("dist", f"LembreteChaveM-Linux-{ver_tag}.zip")
        script_file = os.path.abspath("iniciar_linux.sh")
        if os.path.exists(bin_file):
            for zpath in (linux_zip, ver_linux_zip):
                with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
                    zf.write(bin_file, ver_bin_name)
                    if os.path.exists(manual_dist):
                        zf.write(manual_dist, "Manual_de_Uso.html")
                    if os.path.exists(script_file):
                        zf.write(script_file, "iniciar_linux.sh")
            print(f"Pacotes Linux gerados em: {linux_zip} e {ver_linux_zip}")

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
