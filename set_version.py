import sys
import re
import os

def update_version(ver_input: str):
    ver = ver_input.strip().lstrip('v')
    print(f"Atualizando versão do projeto para: {ver}")

    # 1. Atualizar src/config.py
    cfg_path = os.path.join("src", "config.py")
    if os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf-8") as f:
            content = f.read()
        content = re.sub(r'APP_VERSION\s*=\s*["\'][^"\']+["\']', f'APP_VERSION = "{ver}"', content)
        with open(cfg_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  [OK] Atualizado {cfg_path}")

    # 2. Atualizar arquivos do Manual de Uso
    manual_files = [
        "Manual_de_Uso.html",
        os.path.join("assets", "Manual_de_Uso.html"),
        os.path.join("web", "public", "Manual_de_Uso.html")
    ]
    for mf in manual_files:
        if os.path.exists(mf):
            with open(mf, "r", encoding="utf-8") as f:
                content = f.read()
            content = re.sub(r'v\d+\.\d+\.\d+', f'v{ver}', content)
            with open(mf, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  [OK] Atualizado {mf}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python set_version.py <versao>")
        sys.exit(1)
    update_version(sys.argv[1])
