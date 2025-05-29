import os
import multiprocessing

# Configurações do servidor
bind = "0.0.0.0:5000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
threads = 2
timeout = 120

# Configurações de logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Configurações de performance
worker_tmp_dir = "/dev/shm"
max_requests = 1000
max_requests_jitter = 50

# Garante diretório de uploads
def on_starting(server):
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    os.makedirs(upload_dir, exist_ok=True)

# Limpa recursos ao encerrar
def worker_exit(server, worker):
    import gc
    gc.collect()
