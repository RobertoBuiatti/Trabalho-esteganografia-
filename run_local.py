import http.server
import socketserver
import webbrowser
import subprocess
import threading
import os
import time

def run_backend():
    """Executa o servidor backend Flask"""
    os.chdir('backend')
    subprocess.Popen(['python', 'app.py'])
    os.chdir('..')

def run_frontend():
    """Executa o servidor frontend"""
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"\nFrontend rodando em http://localhost:{PORT}")
        print("\nPressione Ctrl+C para encerrar os servidores")
        httpd.serve_forever()

if __name__ == '__main__':
    print("Iniciando servidores...")
    
    # Inicia o backend
    backend_thread = threading.Thread(target=run_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    # Aguarda o backend iniciar
    time.sleep(2)
    
    # Muda para o diretório frontend
    os.chdir('frontend')
    
    try:
        # Abre o navegador
        webbrowser.open('http://localhost:8000')
        
        # Inicia o frontend
        run_frontend()
    except KeyboardInterrupt:
        print("\nEncerrando servidores...")
    finally:
        os.chdir('..')
