from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from utils import encode_and_save, decode_message
from PIL import Image
import io
import logging

# Configuração de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configurações
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# Cria o diretório de uploads se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar a saúde da API"""
    return jsonify({"status": "healthy"}), 200

@app.route('/encode', methods=['POST'])
def encode():
    """
    Endpoint para codificar uma mensagem em uma imagem
    Espera um arquivo de imagem e uma mensagem no formato multipart/form-data
    """
    try:
        logger.debug("Iniciando processo de codificação")
        
        # Verifica se foi enviado um arquivo
        if 'image' not in request.files:
            logger.error("Nenhuma imagem enviada")
            return jsonify({"error": "Nenhuma imagem enviada"}), 400
            
        file = request.files['image']
        message = request.form.get('message', '')
        
        logger.debug(f"Arquivo recebido: {file.filename}")
        logger.debug(f"Tamanho da mensagem: {len(message)} caracteres")
        
        if not message:
            logger.error("Mensagem não fornecida")
            return jsonify({"error": "Mensagem não fornecida"}), 400
            
        if file.filename == '':
            logger.error("Nome do arquivo vazio")
            return jsonify({"error": "Nome do arquivo vazio"}), 400
            
        if not allowed_file(file.filename):
            logger.error("Tipo de arquivo não permitido")
            return jsonify({"error": "Tipo de arquivo não permitido"}), 400
            
        # Salva o arquivo temporariamente
        filename = secure_filename(file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(temp_path)
        logger.debug(f"Arquivo salvo temporariamente em: {temp_path}")
        
        # Gera um nome para o arquivo de saída
        output_filename = f"encoded_{filename}"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        
        # Codifica a mensagem na imagem
        logger.debug("Iniciando codificação LSB")
        if encode_and_save(temp_path, message, output_path):
            logger.debug("Codificação concluída com sucesso")
            
            # Prepara o arquivo para envio
            with open(output_path, 'rb') as f:
                file_data = io.BytesIO(f.read())
                
            # Remove os arquivos temporários
            os.remove(temp_path)
            os.remove(output_path)
            logger.debug("Arquivos temporários removidos")
            
            return send_file(
                file_data,
                mimetype=f'image/{filename.rsplit(".", 1)[1].lower()}',
                as_attachment=True,
                download_name=output_filename
            )
        else:
            logger.error("Falha na codificação da mensagem")
            # Remove o arquivo temporário em caso de erro
            os.remove(temp_path)
            return jsonify({"error": "Erro ao codificar mensagem"}), 500
            
    except Exception as e:
        logger.error(f"Erro durante a codificação: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/decode', methods=['POST'])
def decode():
    """
    Endpoint para decodificar uma mensagem de uma imagem
    Espera um arquivo de imagem no formato multipart/form-data
    """
    try:
        logger.debug("Iniciando processo de decodificação")
        
        if 'image' not in request.files:
            logger.error("Nenhuma imagem enviada")
            return jsonify({"error": "Nenhuma imagem enviada"}), 400
            
        file = request.files['image']
        logger.debug(f"Arquivo recebido: {file.filename}")
        
        if file.filename == '':
            logger.error("Nome do arquivo vazio")
            return jsonify({"error": "Nome do arquivo vazio"}), 400
            
        if not allowed_file(file.filename):
            logger.error("Tipo de arquivo não permitido")
            return jsonify({"error": "Tipo de arquivo não permitido"}), 400
            
        # Salva o arquivo temporariamente
        filename = secure_filename(file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(temp_path)
        logger.debug(f"Arquivo salvo temporariamente em: {temp_path}")
        
        # Decodifica a mensagem
        logger.debug("Iniciando decodificação LSB")
        message, success = decode_message(temp_path)
        
        # Remove o arquivo temporário
        os.remove(temp_path)
        logger.debug("Arquivo temporário removido")
        
        if success and message:
            logger.debug(f"Mensagem extraída: {message}")
            return jsonify({"message": message}), 200
        else:
            logger.error("Nenhuma mensagem encontrada")
            return jsonify({"error": "Nenhuma mensagem encontrada"}), 200  # Mudado para 200
            
    except Exception as e:
        logger.error(f"Erro durante a decodificação: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("Iniciando servidor Flask")
    app.run(host='0.0.0.0', port=5000, debug=True)