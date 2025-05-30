import { API_URL } from './config.js';

/**
 * Classe responsável por gerenciar as chamadas à API de esteganografia
 */
export class SteganographyAPI {
    /**
     * Configuração padrão para as requisições fetch
     * @private
     */
    static #defaultConfig = {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    };

    /**
     * Processa a resposta da API e trata erros
     * @private
     * @param {Response} response - Resposta da requisição fetch
     * @returns {Promise<any>} Dados da resposta processados
     * @throws {Error} Erro com mensagem apropriada
     */
    static async #handleResponse(response) {
        const data = await response.json();
        
        if (!response.ok || data.error) {
            throw new Error(data.error || 'Erro na operação');
        }
        
        return data;
    }

    /**
     * Codifica uma mensagem em uma imagem
     * @param {File} image - Arquivo de imagem
     * @param {string} message - Mensagem a ser codificada
     * @returns {Promise<Blob>} Blob da imagem com a mensagem codificada
     * @throws {Error} Erro durante o processo de codificação
     */
    static async encodeMessage(image, message) {
        try {
            const formData = new FormData();
            formData.append('image', image);
            formData.append('message', message);

            const response = await fetch(
                `${API_URL}/encode`,
                {
                    ...this.#defaultConfig,
                    body: formData
                }
            );

            await this.#handleResponse(response);
            return await response.blob();
        } catch (error) {
            console.error('Erro na codificação:', error);
            throw error;
        }
    }

    /**
     * Decodifica uma mensagem de uma imagem
     * @param {File} image - Arquivo de imagem
     * @returns {Promise<string|null>} Mensagem decodificada ou null se não houver mensagem
     * @throws {Error} Erro durante o processo de decodificação
     */
    static async decodeMessage(image) {
        try {
            const formData = new FormData();
            formData.append('image', image);

            const response = await fetch(
                `${API_URL}/decode`,
                {
                    ...this.#defaultConfig,
                    body: formData
                }
            );

            const data = await this.#handleResponse(response);
            return data.message || null;
        } catch (error) {
            console.error('Erro na decodificação:', error);
            throw error;
        }
    }
}
