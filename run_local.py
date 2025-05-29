import http.server
import socketserver
import webbrowser
import subprocess
import threading
import os
import time

def run_backend():
    """Executa o servidor backend Flask com configurações otimizadas"""
    os.chdir('backend')
    
    # Define variáveis de ambiente para otimização
    env = os.environ.copy()
    env['PYTHONOPTIMIZE'] = '1'  # Ativa otimizações do Python
    env['FLASK_ENV'] = 'production'  # Modo produção para melhor performance
    
    # Configura garbage collector para ser mais agressivo
    subprocess.run(['python', '-c', 'import gc; gc.set_threshold(100, 5, 5)'])
    
    # Inicia o servidor Flask com workers otimizados
    process = subprocess.Popen(
        ['python', '-X', 'utf8', 'app.py'],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        universal_newlines=True
    )
    
    # Monitora a saída do processo para debug
    def monitor_output():
        for line in process.stdout:
            print(f"[Backend] {line.strip()}")
        for line in process.stderr:
            print(f"[Backend Error] {line.strip()}")
    
    output_thread = threading.Thread(target=monitor_output, daemon=True)
    output_thread.start()
    
    os.chdir('..')
    return process

def run_frontend():
    """Executa o servidor frontend com configurações otimizadas"""
    PORT = 8000
    
    class OptimizedHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            # Adiciona headers de cache para conteúdo estático
            self.send_header('Cache-Control', 'public, max-age=31536000')
            super().end_headers()
            
        def log_message(self, format, *args):
            # Logging customizado
            print(f"[Frontend] {format%args}")
    
    with socketserver.TCPServer(("", PORT), OptimizedHandler) as httpd:
        print(f"\nFrontend rodando em http://localhost:{PORT}")
        print("\nPressione Ctrl+C para encerrar os servidores")
        httpd.serve_forever()

if __name__ == '__main__':
    print("Iniciando servidores...")
    
    # Limpa memória antes de iniciar
    import gc
    gc.collect()
    
    # Inicia o backend
    backend_process = run_backend()
    
    # Aguarda o backend iniciar e verifica saúde
    max_retries = 10
    retries = 0
    backend_ready = False
    
    while retries < max_retries and not backend_ready:
        try:
            import requests
            response = requests.get('http://localhost:5000/health')
            if response.status_code == 200:
                backend_ready = True
                print("Backend iniciado com sucesso!")
            else:
                raise Exception("Backend não está saudável")
        except Exception as e:
            retries += 1
            time.sleep(1)
    
    if not backend_ready:
        print("Erro: Backend não iniciou corretamente")
        backend_process.terminate()
        exit(1)
    
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
        # Limpa recursos
        backend_process.terminate()
        backend_process.wait()
        os.chdir('..')
        gc.collect()  # Força limpeza de memória final
