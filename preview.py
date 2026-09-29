import http.server
import socketserver
import os
import webbrowser
import json

PORT = 3000
WEB_DIR = os.path.abspath("web")

class PreviewHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Normalizar rota
        clean_path = path.split('?')[0].split('#')[0]
        
        if clean_path in ('/', '/index.html'):
            return os.path.join(WEB_DIR, 'preview.html')
        elif clean_path.startswith('/icon.png'):
            return os.path.join(WEB_DIR, 'public', 'icon.png')
        elif clean_path.startswith('/favicon.ico'):
            return os.path.join(WEB_DIR, 'public', 'favicon.ico')
        elif clean_path.startswith('/Manual_de_Uso.html'):
            return os.path.join(WEB_DIR, 'public', 'Manual_de_Uso.html')
        elif clean_path.startswith('/app/'):
            rel = clean_path.replace('/app/', '')
            return os.path.join(WEB_DIR, 'app', rel)
        
        return os.path.join(WEB_DIR, clean_path.lstrip('/'))

    def do_GET(self):
        clean_path = self.path.split('?')[0].split('#')[0]
        
        # Simular o endpoint de API /api/version
        if clean_path == '/api/version':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            data = {
                "success": True,
                "version": "v1.2.1",
                "notes": "Versão ativa no repositório",
                "assets": {
                    "windows": {
                        "name": "LembreteChaveM-Windows.exe",
                        "url": "https://github.com/Paulorsimplicio/lembrete-chave-m/releases/latest/download/LembreteChaveM-Windows.exe"
                    },
                    "macos": {
                        "name": "LembreteChaveM-MacOS.zip",
                        "url": "https://github.com/Paulorsimplicio/lembrete-chave-m/releases/latest/download/LembreteChaveM-MacOS.zip"
                    },
                    "linux": {
                        "name": "LembreteChaveM-Linux",
                        "url": "https://github.com/Paulorsimplicio/lembrete-chave-m/releases/latest/download/LembreteChaveM-Linux"
                    }
                }
            }
            self.wfile.write(json.dumps(data).encode('utf-8'))
            return
            
        return super().do_GET()

def run():
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    
    with socketserver.ThreadingTCPServer(("", PORT), PreviewHandler) as httpd:
        url = f"http://localhost:{PORT}"
        print("=" * 60)
        print("  Servidor de Visualizacao da Landing Page")
        print(f"  URL Local: {url}")
        print("  Pressione Ctrl+C para encerrar o servidor.")
        print("=" * 60)
        
        # Abrir automaticamente no navegador padrão do usuário
        try:
            webbrowser.open(url)
        except Exception:
            pass
            
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor encerrado com sucesso.")

if __name__ == "__main__":
    run()
