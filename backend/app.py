import os
from flask import Flask, request, jsonify, send_file
from PIL import Image
from werkzeug.utils import secure_filename
from flask_cors import CORS
import tempfile
import shutil
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Configurações
UPLOAD_FOLDER = Path(tempfile.gettempdir()) / "steganography_uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def str_to_bin(text):
    """Converte uma string em binário."""
    return ''.join(format(ord(c), '08b') for c in text)

def bin_to_str(binary):
    """Converte binário em string."""
    chars = [binary[i:i+8] for i in range(0, len(binary), 8)]
    return ''.join([chr(int(char, 2)) for char in chars])

def hide_text_in_image(image_path, output_path, secret_text):
    """Esconde texto em uma imagem usando LSB."""
    try:
        img = Image.open(image_path)
        img = img.convert('RGB')
        pixels = img.load()

        binary_text = str_to_bin(secret_text) + '1111111111111110'  # delimitador de fim
        idx = 0

        for y in range(img.height):
            for x in range(img.width):
                r, g, b = pixels[x, y]
                if idx < len(binary_text):
                    r = (r & ~1) | int(binary_text[idx])
                    idx += 1
                if idx < len(binary_text):
                    g = (g & ~1) | int(binary_text[idx])
                    idx += 1
                if idx < len(binary_text):
                    b = (b & ~1) | int(binary_text[idx])
                    idx += 1
                pixels[x, y] = (r, g, b)
                if idx >= len(binary_text):
                    break
            if idx >= len(binary_text):
                break

        img.save(output_path)
        return True
    except Exception as e:
        print(f"Erro ao ocultar texto: {str(e)}")
        return False

def extract_text_from_image(image_path):
    """Extrai texto de uma imagem."""
    try:
        img = Image.open(image_path)
        img = img.convert('RGB')
        pixels = img.load()

        binary_text = ''
        for y in range(img.height):
            for x in range(img.width):
                r, g, b = pixels[x, y]
                binary_text += str(r & 1)
                binary_text += str(g & 1)
                binary_text += str(b & 1)

        end_index = binary_text.find('1111111111111110')
        if end_index != -1:
            binary_text = binary_text[:end_index]
            return bin_to_str(binary_text)
        else:
            return None
    except Exception as e:
        print(f"Erro ao extrair texto: {str(e)}")
        return None

# Rotas da API
@app.route('/api/hide', methods=['POST'])
def hide_text():
    """Rota para ocultar texto em uma imagem."""
    if 'image' not in request.files:
        return jsonify({'error': 'Nenhuma imagem enviada'}), 400
    
    file = request.files['image']
    text = request.form.get('text')
    
    if not text:
        return jsonify({'error': 'Nenhum texto fornecido'}), 400
    
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Tipo de arquivo não permitido'}), 400

    try:
        # Criar diretório de upload se não existir
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Salvar arquivo original
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"input_{filename}")
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"output_{filename}")
        
        file.save(input_path)
        
        # Processar imagem
        success = hide_text_in_image(input_path, output_path, text)
        
        if not success:
            return jsonify({'error': 'Erro ao processar imagem'}), 500
        
        # Enviar arquivo processado
        return send_file(output_path, as_attachment=True, download_name=f"steganography_{filename}")
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Limpar arquivos temporários
        try:
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)
        except:
            pass

@app.route('/api/extract', methods=['POST'])
def extract_text():
    """Rota para extrair texto de uma imagem."""
    if 'image' not in request.files:
        return jsonify({'error': 'Nenhuma imagem enviada'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Tipo de arquivo não permitido'}), 400

    try:
        # Criar diretório de upload se não existir
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Salvar arquivo
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Extrair texto
        extracted_text = extract_text_from_image(file_path)
        
        if extracted_text is None:
            return jsonify({'error': 'Nenhum texto encontrado na imagem'}), 404
        
        return jsonify({'text': extracted_text})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Limpar arquivo temporário
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass

@app.route('/')
def index():
    """Rota principal que serve o frontend."""
    return send_file('../frontend/index.html')

if __name__ == '__main__':
    # Configuração para desenvolvimento local
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
