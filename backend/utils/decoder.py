from PIL import Image
from typing import Optional, Tuple


def bin_to_str(binary: str) -> str:
    """Converte uma string binária em texto"""
    try:
        # Divide a string binária em grupos de 8 bits
        chars = []
        for i in range(0, len(binary), 8):
            byte = binary[i : i + 8]
            if len(byte) == 8:
                # Converte o byte em um número inteiro
                char_code = int(byte, 2)
                # Aceita apenas caracteres ASCII imprimíveis e espaço
                if (32 <= char_code <= 126) or char_code == 32:
                    chars.append(chr(char_code))
                else:
                    print(f"Caractere inválido encontrado (código ASCII: {char_code})")
                    break
        
        message = ''.join(chars)
        # Verifica se a mensagem contém apenas caracteres válidos
        if all(32 <= ord(c) <= 126 or ord(c) == 32 for c in message):
            if len(message) == 0:
                print("Sequência binária não resultou em caracteres válidos")
                return ""
            return message
        print("Mensagem contém caracteres inválidos")
        return ""
        
    except Exception as e:
        print(f"Erro na conversão binária para texto: {e}")
        if "invalid literal" in str(e):
            print("Dados binários corrompidos ou inválidos")
        elif "out of range" in str(e):
            print("Valor binário fora do intervalo permitido")
        return ""


def extract_text_from_image(image_path: str) -> Optional[str]:
    """
    Extrai texto oculto de uma imagem usando LSB
    Retorna o texto extraído ou None se houver erro
    """
    try:
        # Abre e converte a imagem para RGB
        img = Image.open(image_path)
        img = img.convert("RGB")
        pixels = img.load()
        width, height = img.size

        # Extrai os bits menos significativos
        binary_text = ""
        bit_count = 0

        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                # Extrai o bit menos significativo de cada canal
                binary_text += str(r & 1)
                binary_text += str(g & 1)
                binary_text += str(b & 1)

                bit_count += 3
                # Verifica se temos bits suficientes para uma mensagem razoável
                if bit_count >= 24000:  # Aproximadamente 3000 caracteres
                    break
            if bit_count >= 24000:
                break

        # Procura pelo delimitador
        delimitador = "1111111111111110"
        start_index = 0
        chunk_size = 1000  # Procura em chunks para melhor performance
        end_index = -1

        while start_index < len(binary_text):
            chunk = binary_text[start_index : start_index + chunk_size]
            chunk_index = chunk.find(delimitador)

            if chunk_index != -1:
                end_index = start_index + chunk_index
                break

            start_index += chunk_size - len(
                delimitador
            )  # Sobrepõe um pouco para não perder o delimitador entre chunks

        if end_index != -1:
            # Extrai apenas o texto até o delimitador
            binary_message = binary_text[:end_index]
            # Converte para texto
            message = bin_to_str(binary_message)
            if message:
                return message

        print("Nenhuma mensagem válida encontrada na imagem. Possíveis causas:")
        print("- A imagem não contém uma mensagem oculta")
        print("- O delimitador não foi encontrado")
        print("- A mensagem está corrompida")
        return None

    except Exception as e:
        error_msg = str(e)
        print(f"Erro ao extrair texto da imagem: {error_msg}")
        if "cannot identify image file" in error_msg:
            print("O arquivo não é uma imagem válida ou está corrompido")
        elif "truncated" in error_msg:
            print("A imagem está incompleta ou corrompida")
        elif "memory" in error_msg.lower():
            print("Memória insuficiente para processar a imagem")
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

        if message:
            print(f"Mensagem extraída com sucesso: {message}")
            return message, True

        print("Falha ao extrair mensagem da imagem")
        print("Verifique se a imagem foi codificada corretamente e tente novamente")
        return None, False

    except Exception as e:
        error_msg = str(e)
        print(f"Erro durante a decodificação: {error_msg}")
        print("Detalhes técnicos do erro:")
        print("- Verifique se o arquivo é uma imagem válida")
        print("- Certifique-se que a imagem não está corrompida")
        print("- Confirme se a imagem foi codificada usando este mesmo sistema")
        return None, False
