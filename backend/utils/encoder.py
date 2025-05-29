from PIL import Image
from typing import Tuple, Optional

def str_to_bin(text: str) -> str:
    """Converte texto em uma string binária"""
    try:
        # Converte apenas caracteres ASCII imprimíveis
        binary = ''
        for char in text:
            code = ord(char)
            if 32 <= code <= 126:  # ASCII imprimíveis
                binary += format(code, '08b')
            else:
                print(f"Ignorando caractere não-ASCII: {char}")
        print(f"Texto convertido para binário: {len(binary)} bits")
        return binary
    except Exception as e:
        print(f"Erro na conversão de texto para binário: {e}")
        return ""

def hide_text_in_image(image_path: str, output_path: str, secret_text: str) -> bool:
    """
    Esconde texto em uma imagem usando LSB
    Retorna True se a operação foi bem sucedida
    """
    try:
        print(f"Iniciando ocultação do texto na imagem: {image_path}")
        print(f"Tamanho do texto: {len(secret_text)} caracteres")

        # Converte o texto para binário
        binary_text = str_to_bin(secret_text)
        if not binary_text:
            print("Erro: texto inválido ou vazio")
            return False

        # Adiciona delimitador de fim
        binary_text += '1111111111111110'

        # Abre e converte a imagem para RGB
        img = Image.open(image_path)
        img = img.convert('RGB')
        width, height = img.size
        pixels = list(img.getdata())

        # Verifica se a imagem tem capacidade suficiente
        if len(binary_text) > len(pixels) * 3:
            print(f"Erro: imagem muito pequena. Necessário: {len(binary_text)} bits, Disponível: {len(pixels) * 3} bits")
            return False

        # Modifica os pixels
        new_pixels = []
        binary_index = 0

        for pixel in pixels:
            r, g, b = pixel
            
            # Modifica cada canal apenas se ainda houver bits para esconder
            if binary_index < len(binary_text):
                r = (r & ~1) | int(binary_text[binary_index])
                binary_index += 1
            if binary_index < len(binary_text):
                g = (g & ~1) | int(binary_text[binary_index])
                binary_index += 1
            if binary_index < len(binary_text):
                b = (b & ~1) | int(binary_text[binary_index])
                binary_index += 1
                
            new_pixels.append((r, g, b))

            if binary_index >= len(binary_text):
                # Adiciona os pixels restantes sem modificação
                new_pixels.extend(pixels[len(new_pixels):])
                break

        # Cria nova imagem com os pixels modificados
        new_img = Image.new('RGB', (width, height))
        new_img.putdata(new_pixels)

        # Salva a imagem modificada com alta qualidade
        new_img.save(output_path, 'PNG', quality=100)
        print(f"Imagem com mensagem oculta salva em: {output_path}")
        return True

    except Exception as e:
        print(f"Erro ao ocultar texto: {e}")
        return False

def encode_message(image_path: str, message: str) -> Optional[Tuple[Image.Image, bool]]:
    """
    Codifica uma mensagem em uma imagem usando LSB
    Retorna a imagem modificada e um booleano indicando sucesso
    """
    try:
        # Converte o texto para binário
        binary_text = str_to_bin(message)
        if not binary_text:
            return None, False

        # Adiciona delimitador
        binary_text += '1111111111111110'

        # Abre e converte a imagem para RGB
        img = Image.open(image_path).convert('RGB')
        width, height = img.size
        pixels = list(img.getdata())

        # Verifica se a imagem tem capacidade suficiente
        if len(binary_text) > len(pixels) * 3:
            print("Imagem muito pequena para a mensagem")
            return None, False

        # Modifica os pixels
        new_pixels = []
        binary_index = 0

        for pixel in pixels:
            r, g, b = pixel
            
            # Modifica cada canal apenas se ainda houver bits para esconder
            if binary_index < len(binary_text):
                r = (r & ~1) | int(binary_text[binary_index])
                binary_index += 1
            if binary_index < len(binary_text):
                g = (g & ~1) | int(binary_text[binary_index])
                binary_index += 1
            if binary_index < len(binary_text):
                b = (b & ~1) | int(binary_text[binary_index])
                binary_index += 1
                
            new_pixels.append((r, g, b))

            if binary_index >= len(binary_text):
                # Adiciona os pixels restantes sem modificação
                new_pixels.extend(pixels[len(new_pixels):])
                break

        # Cria nova imagem com os pixels modificados
        new_img = Image.new('RGB', (width, height))
        new_img.putdata(new_pixels)
        return new_img, True

    except Exception as e:
        print(f"Erro durante a codificação: {e}")
        return None, False

def encode_and_save(image_path: str, message: str, output_path: str) -> bool:
    """
    Codifica uma mensagem em uma imagem e salva o resultado
    Retorna True se a operação foi bem sucedida
    """
    try:
        return hide_text_in_image(image_path, output_path, message)
    except Exception as e:
        print(f"Erro ao codificar e salvar: {e}")
        return False
