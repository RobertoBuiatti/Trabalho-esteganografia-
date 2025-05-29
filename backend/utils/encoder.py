from PIL import Image
from typing import Tuple, Optional

def str_to_bin(text: str) -> str:
    """Converte texto em uma string binária"""
    try:
        # Converte apenas caracteres ASCII imprimíveis
        valid_chars = [c for c in text if 32 <= ord(c) <= 126 or ord(c) == 32]
        binary = ''.join(format(ord(char), '08b') for char in valid_chars)
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
        
        # Abre e converte a imagem para RGB
        img = Image.open(image_path)
        img = img.convert('RGB')
        pixels = img.load()
        width, height = img.size
        
        # Remove caracteres não ASCII e converte para binário
        binary_text = str_to_bin(secret_text)
        if not binary_text:
            print("Erro: texto inválido ou vazio")
            return False
            
        # Adiciona delimitador
        binary_text += '1111111111111110'
        
        # Verifica se a imagem tem capacidade suficiente
        if len(binary_text) > width * height * 3:
            print("Erro: imagem muito pequena para a mensagem")
            return False
            
        print(f"Tamanho do texto em binário (com delimitador): {len(binary_text)} bits")
        idx = 0

        # Percorre cada pixel da imagem
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                
                # Modifica o bit menos significativo de cada canal
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
                
                # Verifica se terminou de processar o texto
                if idx >= len(binary_text):
                    break
            if idx >= len(binary_text):
                break

        # Salva a imagem modificada
        img.save(output_path)
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
        # Abre e converte a imagem para RGB
        img = Image.open(image_path).convert('RGB')
        pixels = img.load()
        width, height = img.size
        
        # Remove caracteres não ASCII e converte para binário
        binary_text = str_to_bin(message)
        if not binary_text:
            return None, False
            
        # Adiciona delimitador
        binary_text += '1111111111111110'
        
        # Verifica se a imagem tem capacidade suficiente
        if len(binary_text) > width * height * 3:
            print("Imagem muito pequena para a mensagem")
            return None, False
            
        idx = 0

        # Percorre cada pixel da imagem
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                
                # Modifica o bit menos significativo de cada canal
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
                
                # Verifica se terminou de processar o texto
                if idx >= len(binary_text):
                    break
            if idx >= len(binary_text):
                break
                
        return img, True
        
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