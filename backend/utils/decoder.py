from PIL import Image
import numpy as np
from typing import Optional, Generator, Tuple

def extract_bits(block: np.ndarray) -> Generator[int, None, None]:
    """Extrai bits menos significativos de um bloco numpy"""
    for pixel in block.reshape(-1, 3):
        for color in pixel:
            yield color & 1

def bits_to_text(bits_iterator: Generator[int, None, None], buffer_size: int = 1024) -> Optional[str]:
    """Converte bits em texto, procurando pelo delimitador"""
    DELIMITADOR = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0]
    buffer = []
    text = []
    
    try:
        while True:
            bit = next(bits_iterator)
            buffer.append(bit)
            
            # Verifica delimitador
            if len(buffer) >= 16 and buffer[-16:] == DELIMITADOR:
                break
                
            # Converte bytes completos em caracteres
            if len(buffer) >= 8:
                byte_bits = buffer[:8]
                char_code = sum(bit << (7-i) for i, bit in enumerate(byte_bits))
                
                if 32 <= char_code <= 126:
                    text.append(chr(char_code))
                    buffer = buffer[8:]
            
            # Limita tamanho do buffer
            if len(buffer) > buffer_size:
                buffer = buffer[-16:]  # Mantém apenas bits suficientes para detectar delimitador
                
        return ''.join(text) if text else None
        
    except StopIteration:
        return None

def decode_image(image_path: str) -> Optional[str]:
    """Decodifica mensagem oculta em uma imagem usando processamento eficiente"""
    try:
        with Image.open(image_path) as img:
            img = img.convert('RGB')
            width, height = img.size
            
            # Processa a imagem em blocos
            BATCH_ROWS = 50
            all_bits = None
            
            for y_start in range(0, height, BATCH_ROWS):
                y_end = min(y_start + BATCH_ROWS, height)
                
                # Processa bloco atual
                block = np.array(img.crop((0, y_start, width, y_end)))
                
                if all_bits is None:
                    all_bits = extract_bits(block)
                else:
                    # Encadeia geradores de bits
                    all_bits = (bit for iterator in [all_bits, extract_bits(block)] for bit in iterator)
                
                # Tenta extrair mensagem do buffer atual
                result = bits_to_text(all_bits)
                if result:
                    return result
            
            return None
            
    except Exception as e:
        print(f"Erro ao decodificar imagem: {e}")
        return None

def decode_message(image_path: str) -> Tuple[Optional[str], bool]:
    """Wrapper para manter compatibilidade com API existente"""
    try:
        result = decode_image(image_path)
        return (result, True) if result else (None, False)
    except Exception as e:
        print(f"Erro durante decodificação: {e}")
        return None, False
