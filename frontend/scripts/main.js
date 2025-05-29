import { UI } from './ui.js';
import { SteganographyAPI } from './api.js';

class App {
    constructor() {
        this.ui = new UI();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Evento de codificação
        this.ui.elements.encodeButton.addEventListener('click', async () => {
            if (!this.ui.state.encodeFile) {
                this.ui.updateStatus(this.ui.elements.encodeStatus, 'Por favor, selecione uma imagem.', true);
                return;
            }

            try {
                this.ui.showLoading('Codificando mensagem na imagem...');
                const blob = await SteganographyAPI.encodeMessage(
                    this.ui.state.encodeFile,
                    this.ui.elements.messageInput.value
                );

                this.ui.downloadFile(
                    blob,
                    'imagem_codificada.' + this.ui.state.encodeFile.name.split('.').pop()
                );

                this.ui.updateStatus(this.ui.elements.encodeStatus, 'Mensagem codificada com sucesso!');
                this.ui.resetEncodeForm();

            } catch (error) {
                console.error('Erro durante a codificação:', error);
                let errorMessage = error.message;
                
                // Tratamento específico de erros
                if (errorMessage.includes('FILE_TOO_LARGE')) {
                    errorMessage = 'O arquivo é muito grande. O tamanho máximo permitido é 50MB.';
                } else if (errorMessage.includes('UNSUPPORTED_FORMAT')) {
                    errorMessage = 'Formato de imagem não suportado. Use PNG, JPG, JPEG ou BMP.';
                } else if (errorMessage.includes('ENCODE_FAILED')) {
                    errorMessage = 'Não foi possível codificar a mensagem. A imagem pode ser muito pequena para a mensagem.';
                }
                
                this.ui.updateStatus(this.ui.elements.encodeStatus, errorMessage, true);
            } finally {
                this.ui.hideLoading();
            }
        });

        // Evento de decodificação
        this.ui.elements.decodeButton.addEventListener('click', async () => {
            if (!this.ui.state.decodeFile) {
                this.ui.updateStatus(this.ui.elements.decodeStatus, 'Por favor, selecione uma imagem.', true);
                return;
            }

            try {
                this.ui.showLoading('Extraindo mensagem da imagem...');
                const message = await SteganographyAPI.decodeMessage(this.ui.state.decodeFile);

                if (message === null) {
                    this.ui.elements.decodedMessage.textContent = '';
                    this.ui.updateStatus(
                        this.ui.elements.decodeStatus,
                        'Nenhuma mensagem encontrada na imagem',
                        true
                    );
                } else {
                    this.ui.elements.decodedMessage.textContent = message;
                    this.ui.updateStatus(
                        this.ui.elements.decodeStatus,
                        'Mensagem extraída com sucesso!'
                    );
                }

                this.ui.resetDecodeForm();

            } catch (error) {
                console.error('Erro durante a decodificação:', error);
                this.ui.elements.decodedMessage.textContent = '';
                
                let errorMessage = error.message;
                
                // Tratamento específico de erros
                if (error.response?.status === 404) {
                    errorMessage = 'Nenhuma mensagem encontrada nesta imagem. Verifique se a imagem foi codificada corretamente.';
                } else if (errorMessage.includes('UNSUPPORTED_FORMAT')) {
                    errorMessage = 'Formato de imagem não suportado. Use PNG, JPG, JPEG ou BMP.';
                } else if (errorMessage.includes('FILE_TOO_LARGE')) {
                    errorMessage = 'O arquivo é muito grande. O tamanho máximo permitido é 50MB.';
                } else if (errorMessage.includes('cannot identify image file')) {
                    errorMessage = 'O arquivo não é uma imagem válida ou está corrompido.';
                }
                
                this.ui.updateStatus(this.ui.elements.decodeStatus, errorMessage, true);
            } finally {
                this.ui.hideLoading();
            }
        });
    }
}

// Inicializa a aplicação
window.addEventListener('DOMContentLoaded', () => {
    new App();
    console.log('Aplicação inicializada');
});
