from PIL import Image
import numpy as np
from typing import Optional

def str_to_binary_generator(text: str):
    """Gerador que converte texto em bits, um por vez"""
    for char in text:
        code = ord(char)
        if 32 <= code <= 126:  # ASCII imprimíveis
            for bit in format(code, '08b'):
                yield int(bit)
    # Adiciona delimitador
    for bit in '1111111111111110':
        yield int(bit)

def encode_image(image_path: str, output_path: str, secret_text: str) -> bool:
    """Esconde texto em uma imagem usando processamento eficiente de memória"""
    try:
        if not secret_text:
            print("Erro: texto vazio")
            return False

        # Abre a imagem e converte para array numpy
        with Image.open(image_path) as img:
            img = img.convert('RGB')
            width, height = img.size
            
            # Verifica capacidade
            text_bits = len(secret_text) * 8 + 16  # texto + delimitador
            if text_bits > width * height * 3:
                print(f"Erro: imagem pequena demais. Necessário: {text_bits} bits")
                return False

            # Processa a imagem em pequenos blocos
            BATCH_ROWS = 50
            new_img = Image.new('RGB', (width, height))
            binary_gen = str_to_binary_generator(secret_text)
            next_bit = next(binary_gen, None)

            for y_start in range(0, height, BATCH_ROWS):
                y_end = min(y_start + BATCH_ROWS, height)
                
                # Processa bloco atual
                block = np.array(img.crop((0, y_start, width, y_end)))
                
                if next_bit is not None:
                    # Modifica apenas os bits necessários
                    for i in range(block.shape[0]):
                        for j in range(block.shape[1]):
                            for c in range(3):
                                if next_bit is not None:
                                    block[i,j,c] = (block[i,j,c] & ~1) | next_bit
                                    next_bit = next(binary_gen, None)
                
                # Converte bloco processado de volta para imagem
                block_img = Image.fromarray(block)
                new_img.paste(block_img, (0, y_start))
                
                if next_bit is None:
                    # Copia o resto da imagem sem modificações
                    if y_end < height:
                        new_img.paste(img.crop((0, y_end, width, height)), (0, y_end))
                    break

            new_img.save(output_path, 'PNG', optimize=True)
            print(f"Imagem salva em: {output_path}")
            return True

    except Exception as e:
        print(f"Erro ao codificar imagem: {e}")
        return False

def encode_and_save(image_path: str, message: str, output_path: str) -> bool:
    """Wrapper para manter compatibilidade com API existente"""
    return encode_image(image_path, output_path, message)
