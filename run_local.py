import http.server
import socketserver
import webbrowser
import subprocess
import threading
import os
import time

def run_backend():
    """Executa o servidor backend Flask com configurações otimizadas"""
    backend_dir = os.path.abspath('backend')
    if not os.path.exists(backend_dir):
        raise Exception(f"Diretório backend não encontrado: {backend_dir}")
    
    os.chdir(backend_dir)
    
    try:
        # Define variáveis de ambiente para otimização
        env = os.environ.copy()
        env['PYTHONOPTIMIZE'] = '1'
        env['FLASK_ENV'] = 'production'
        env['PYTHONPATH'] = backend_dir
        
        # Garante que o GC está ativo e otimizado
        gc.collect()
        gc.set_threshold(100, 5, 5)
        
        print("[Backend] Iniciando servidor Flask...")
        
        # Inicia o servidor Flask
        process = subprocess.Popen(
            ['python', '-X', 'utf8', 'app.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            universal_newlines=True,
            cwd=backend_dir  # Garante diretório correto
        )
        
        # Monitora a saída do processo para debug
        def monitor_output():
            while True:
                # Lê stderr primeiro para capturar erros
                error = process.stderr.readline()
                if error:
                    print(f"[Backend Error] {error.strip()}")
                    continue
                
                output = process.stdout.readline()
                if output:
                    print(f"[Backend] {output.strip()}")
                
                # Verifica se o processo ainda está rodando
                if process.poll() is not None:
                    break
        
        output_thread = threading.Thread(target=monitor_output, daemon=True)
        output_thread.start()
        
        # Aguarda um pouco para o servidor iniciar
        time.sleep(2)
        
        if process.poll() is not None:
            raise Exception("Servidor Flask falhou ao iniciar")
        
        os.chdir('..')
        return process
        
    except Exception as e:
        print(f"[Backend Error] Falha ao iniciar servidor: {str(e)}")
        os.chdir('..')
        raise

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
    
    # Aguarda o backend iniciar com retry exponencial
    wait_time = 1
    while retries < max_retries and not backend_ready:
        try:
            import requests
            response = requests.get('http://localhost:5000/health', timeout=5)
            if response.status_code == 200:
                backend_ready = True
                print("[Backend] Servidor iniciado e saudável!")
                break
            else:
                print(f"[Backend] Aguardando servidor... (tentativa {retries + 1}/{max_retries})")
                raise Exception(f"Status inesperado: {response.status_code}")
        except Exception as e:
            if retries == max_retries - 1:
                print(f"[Backend Error] Falha ao iniciar: {str(e)}")
                backend_process.terminate()
                backend_process.wait()
                exit(1)
            retries += 1
            time.sleep(wait_time)
            wait_time = min(wait_time * 2, 5)  # Exponential backoff, max 5 seconds
    
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
