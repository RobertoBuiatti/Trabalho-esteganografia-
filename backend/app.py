from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from utils import encode_and_save, decode_message
import logging
import time
from threading import Thread
import shutil
from werkzeug.middleware.proxy_fix import ProxyFix
import gc

# Configuração de logging
logging.basicConfig(
    level=os.environ.get('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

# Configuração do CORS baseada no ambiente
ALLOWED_ORIGINS = [
    'https://trabalho-esteganografia.onrender.com',
    'http://localhost:5000',
    'http://127.0.0.1:5000'
]
CORS(app, resources={
    r"/*": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"],
        "supports_credentials": True
    }
})

# Configurações otimizadas
IS_PRODUCTION = os.environ.get('RENDER', False)
UPLOAD_FOLDER = os.path.join('/tmp', 'uploads') if IS_PRODUCTION else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}
MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 8 * 1024 * 1024))  # 8MB default
MAX_FILE_AGE = int(os.environ.get('MAX_FILE_AGE', 1800))  # 30 minutos default
CHUNK_SIZE = int(os.environ.get('CHUNK_SIZE', 4096))  # 4KB default
MAX_UPLOAD_DIR_SIZE = int(os.environ.get('MAX_UPLOAD_DIR_SIZE', 50 * 1024 * 1024))  # 50MB default

def init_app():
    """Inicializa a aplicação com configurações otimizadas"""
    try:
        # Cria diretório de uploads com path absoluto
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Limpa arquivos antigos do diretório de uploads
        if os.path.exists(UPLOAD_FOLDER):
            for file in os.listdir(UPLOAD_FOLDER):
                try:
                    os.remove(os.path.join(UPLOAD_FOLDER, file))
                except OSError:
                    pass
        
        # Inicia thread de limpeza periódica
        cleanup_thread = Thread(target=periodic_cleanup, daemon=True)
        cleanup_thread.start()
        
        # Configura GC
        gc.enable()
        gc.collect()
        
        logger.info(f"Aplicação iniciada - Upload dir: {UPLOAD_FOLDER}")
        return True
    except Exception as e:
        logger.error(f"Erro na inicialização: {str(e)}")
        return False

def allowed_file(filename: str) -> bool:
    """Verifica se o arquivo tem uma extensão permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def periodic_cleanup():
    """Remove arquivos temporários e gerencia uso de memória"""
    while True:
        try:
            now = time.time()
            total_size = 0
            
            # Lista todos os arquivos uma única vez
            files = [(f, os.path.join(UPLOAD_FOLDER, f)) for f in os.listdir(UPLOAD_FOLDER)]
            
            for filename, filepath in files:
                try:
                    if os.path.isfile(filepath):
                        file_age = now - os.path.getmtime(filepath)
                        file_size = os.path.getsize(filepath)
                        total_size += file_size
                        
                        # Remove arquivos antigos ou se diretório estiver muito grande
                        if file_age > MAX_FILE_AGE or total_size > MAX_UPLOAD_DIR_SIZE:
                            os.remove(filepath)
                except OSError:
                    continue
            
            # Força limpeza de memória
            gc.collect()
            
        except Exception as e:
            logger.error(f"Erro durante limpeza: {e}")
        
        time.sleep(300)  # Executa a cada 5 minutos

def stream_file(file_path: str):
    """Stream otimizado de arquivo"""
    def generate():
        try:
            with open(file_path, 'rb') as f:
                while data := f.read(CHUNK_SIZE):
                    yield data
        finally:
            # Limpa o arquivo após streaming
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except OSError:
                pass
    return generate()

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de healthcheck"""
    gc.collect()  # Força limpeza de memória
    return jsonify({"status": "healthy"}), 200

@app.route('/encode', methods=['POST'])
def encode():
    """Endpoint para codificar mensagem em imagem"""
    temp_path = output_path = None
    try:
        # Validações iniciais
        if not request.content_length or request.content_length > MAX_CONTENT_LENGTH:
            return jsonify({"error": "Arquivo muito grande", "code": "FILE_TOO_LARGE"}), 413
            
        if 'image' not in request.files:
            return jsonify({"error": "Imagem não enviada", "code": "MISSING_IMAGE"}), 400
            
        file = request.files['image']
        message = request.form.get('message', '').strip()
        
        if not message or not file.filename or not allowed_file(file.filename):
            return jsonify({"error": "Parâmetros inválidos", "code": "INVALID_PARAMS"}), 400
            
        # Processa arquivo
        filename = secure_filename(file.filename)
        timestamp = int(time.time())
        temp_path = os.path.join(UPLOAD_FOLDER, f"temp_{timestamp}_{filename}")
        output_path = os.path.join(UPLOAD_FOLDER, f"encoded_{timestamp}_{filename}")
        
        # Salva arquivo em chunks pequenos
        with open(temp_path, 'wb') as f:
            while chunk := file.read(CHUNK_SIZE):
                f.write(chunk)
        
        # Codifica mensagem
        if encode_and_save(temp_path, message, output_path):
            os.remove(temp_path)
            temp_path = None
            
            response = Response(
                stream_file(output_path),
                mimetype=f'image/{filename.rsplit(".", 1)[1].lower()}'
            )
            response.headers.update({
                'Content-Disposition': f'attachment; filename="encoded_{filename}"',
                'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
                'Pragma': 'no-cache'
            })
            
            # Arquivo será removido após streaming
            return response
            
        raise Exception("Falha na codificação")
            
    except Exception as e:
        logger.error(f"Erro durante a codificação: {str(e)}", exc_info=True)
        error_msg = str(e)
        if "too large" in error_msg.lower():
            return jsonify({
                "error": "Arquivo muito grande",
                "details": f"O tamanho máximo permitido é {MAX_CONTENT_LENGTH/(1024*1024)}MB.",
                "code": "FILE_TOO_LARGE"
            }), 413
        return jsonify({
            "error": "Erro interno",
            "details": f"Ocorreu um erro inesperado: {error_msg}",
            "code": "INTERNAL_ERROR"
        }), 500

@app.route('/decode', methods=['POST'])
def decode():
    """Endpoint para decodificar mensagem de uma imagem"""
    temp_path = None
    try:
        # Validações iniciais
        if not request.content_length or request.content_length > MAX_CONTENT_LENGTH:
            return jsonify({"error": "Arquivo muito grande", "code": "FILE_TOO_LARGE"}), 413
        
        if 'image' not in request.files:
            return jsonify({"error": "Imagem não enviada", "code": "MISSING_IMAGE"}), 400
            
        file = request.files['image']
        if not file.filename or not allowed_file(file.filename):
            return jsonify({"error": "Arquivo inválido", "code": "INVALID_FILE"}), 400
            
        # Processa arquivo
        filename = secure_filename(file.filename)
        timestamp = int(time.time())
        temp_path = os.path.join(UPLOAD_FOLDER, f"temp_decode_{timestamp}_{filename}")
        
        with open(temp_path, 'wb') as f:
            while chunk := file.read(CHUNK_SIZE):
                f.write(chunk)
        
        # Decodifica mensagem
        message, success = decode_message(temp_path)
        
        # Limpa arquivo temporário
        if os.path.exists(temp_path):
            os.remove(temp_path)
            temp_path = None
            
        if success and message:
            return jsonify({"message": message, "success": True}), 200
            
        return jsonify({"error": "Mensagem não encontrada", "code": "NO_MESSAGE"}), 404
            
    except Exception as e:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500
    finally:
        gc.collect()  # Força limpeza de memória

if __name__ == '__main__':
    # Verifica inicialização antes de subir o servidor
    if init_app():
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    else:
        print("Erro: Falha na inicialização da aplicação")
        exit(1)
