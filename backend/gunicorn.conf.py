bind = "0.0.0.0:5000"
workers = 4
threads = 2
worker_class = "gthread"
timeout = 120
keepalive = 5

# Configuração pré-fork
def pre_fork(server, worker):
    import os
    # Cria diretório de uploads em um local garantido
    uploads_dir = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)

# Reinicia workers periodicamente
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
