import { API_URL } from './config.js';

/**
 * Classe responsável por gerenciar as chamadas à API
 */
export class SteganographyAPI {
    /**
     * Codifica uma mensagem em uma imagem
     * @param {File} image - Arquivo de imagem
     * @param {string} message - Mensagem a ser codificada
     * @returns {Promise<Blob>} Blob da imagem com a mensagem codificada
     */
    static async encodeMessage(image, message) {
        try {
            const formData = new FormData();
            formData.append('image', image);
            formData.append('message', message);

            const response = await fetch(`${API_URL}/encode`, {
                method: 'POST',
                body: formData,
                mode: 'cors',
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Erro ao codificar mensagem');
            }

            return await response.blob();
        } catch (error) {
            console.error('Erro na codificação:', error);
            throw error;
        }
    }

    /**
     * Decodifica uma mensagem de uma imagem
     * @param {File} image - Arquivo de imagem
     * @returns {Promise<string>} Mensagem decodificada
     */
    static async decodeMessage(image) {
        try {
            const formData = new FormData();
            formData.append('image', image);

            const response = await fetch(`${API_URL}/decode`, {
                method: 'POST',
                body: formData,
                mode: 'cors',
                headers: {
                    'Accept': 'application/json'
                }
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Erro na decodificação');
            }

            if (data.error) {
                return null;
            }

            return data.message;
        } catch (error) {
            console.error('Erro na decodificação:', error);
            throw error;
        }
    }
}
