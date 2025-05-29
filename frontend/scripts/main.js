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
                this.ui.updateStatus(this.ui.elements.encodeStatus, error.message, true);
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

                this.ui.elements.decodedMessage.textContent = message;
                this.ui.updateStatus(
                    this.ui.elements.decodeStatus,
                    message === 'Nenhuma mensagem encontrada'
                        ? 'Nenhuma mensagem encontrada na imagem'
                        : 'Mensagem extraída com sucesso!'
                );

                this.ui.resetDecodeForm();

            } catch (error) {
                console.error('Erro durante a decodificação:', error);
                this.ui.elements.decodedMessage.textContent = '';
                this.ui.updateStatus(this.ui.elements.decodeStatus, error.message, true);
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
