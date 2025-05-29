from PIL import Image
from typing import Optional, Tuple

def bin_to_str(binary: str) -> str:
    """Converte uma string binária em texto"""
    try:
        message = ""
        # Processa 8 bits por vez
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            if len(byte) == 8:
                # Converte para decimal
                char_code = int(byte, 2)
                # Só aceita caracteres ASCII imprimíveis
                if 32 <= char_code <= 126:
                    message += chr(char_code)
                else:
                    print(f"Caractere inválido encontrado (código: {char_code})")
        return message
    except Exception as e:
        print(f"Erro na conversão binária para texto: {e}")
        return ""

def extract_text_from_image(image_path: str) -> Optional[str]:
    """
    Extrai texto oculto de uma imagem usando LSB
    Retorna o texto extraído ou None se houver erro
    """
    try:
        print(f"Iniciando decodificação da imagem: {image_path}")
        
        # Abre e converte a imagem para RGB
        img = Image.open(image_path).convert('RGB')
        # Obtém os pixels como uma lista
        pixels = list(img.getdata())
        
        # Extrai os bits menos significativos
        binary_text = ""
        
        # Processa cada pixel
        for r, g, b in pixels:
            # Extrai o bit menos significativo de cada canal
            binary_text += str(r & 1)
            binary_text += str(g & 1)
            binary_text += str(b & 1)
            
            # Verifica se encontrou o delimitador a cada 24 bits (um múltiplo do tamanho do delimitador)
            if len(binary_text) % 24 == 0:
                end_index = binary_text.find('1111111111111110')
                if end_index != -1:
                    # Extrai o texto até o delimitador
                    binary_message = binary_text[:end_index]
                    # Converte para texto
                    message = bin_to_str(binary_message)
                    if message:
                        print(f"Mensagem extraída com sucesso: {message}")
                        return message
                    break

        print("Nenhuma mensagem válida encontrada na imagem")
        return None

    except Exception as e:
        error_msg = str(e)
        print(f"Erro ao extrair texto da imagem: {error_msg}")
        if "cannot identify image file" in error_msg:
            print("O arquivo não é uma imagem válida ou está corrompido")
        elif "truncated" in error_msg:
            print("A imagem está incompleta ou corrompida")
        else:
            print("Erro desconhecido ao processar a imagem")
        return None

def decode_message(image_path: str) -> Tuple[Optional[str], bool]:
    """
    Extrai uma mensagem oculta de uma imagem
    Retorna a mensagem e um booleano indicando sucesso
    """
    try:
        print(f"Iniciando decodificação da imagem: {image_path}")
        message = extract_text_from_image(image_path)

        if message is not None and message.strip():
            return message, True

        print("Falha ao extrair mensagem da imagem")
        return None, False

    except Exception as e:
        print(f"Erro durante a decodificação: {e}")
        return None, False
