import os

# Usa porta fornecida pelo Render ou fallback para 5000
port = os.environ.get("PORT", 5000)
bind = f"0.0.0.0:{port}"

# Configurações de workers
workers = 2  # Reduzido para melhor performance no Render
threads = 2
worker_class = "gthread"
timeout = 120
keepalive = 5

# Configuração pré-fork
def pre_fork(server, worker):
    # Usa diretório temporário do sistema para uploads
    uploads_dir = os.path.join('/tmp', 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)

# Reinicia workers periodicamente para evitar memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Configurações específicas para cloud
worker_tmp_dir = "/tmp"  # Usa /tmp para arquivos temporários
timeout = 120  # Aumenta timeout para uploads maiores
