import { ALLOWED_IMAGE_TYPES, MAX_FILE_SIZE } from './config.js';

/**
 * Classe responsável por gerenciar a interface do usuário
 */
export class UI {
    constructor() {
        this.elements = {
            encodeDropArea: document.getElementById('encode-drop-area'),
            decodeDropArea: document.getElementById('decode-drop-area'),
            encodeFileInput: document.getElementById('encode-file-input'),
            decodeFileInput: document.getElementById('decode-file-input'),
            encodePreview: document.getElementById('encode-preview'),
            decodePreview: document.getElementById('decode-preview'),
            messageInput: document.getElementById('message-input'),
            encodeButton: document.getElementById('encode-button'),
            decodeButton: document.getElementById('decode-button'),
            encodeStatus: document.getElementById('encode-status'),
            decodeStatus: document.getElementById('decode-status'),
            decodedMessage: document.getElementById('decoded-message'),
            loadingOverlay: document.getElementById('loading-overlay')
        };

        this.state = {
            encodeFile: null,
            decodeFile: null
        };

        this.setupEventListeners();
    }

    /**
     * Configura os event listeners para drag and drop e seleção de arquivo
     */
    setupEventListeners() {
        this.setupDragAndDrop(
            this.elements.encodeDropArea,
            this.elements.encodeFileInput,
            this.elements.encodePreview,
            'encode'
        );

        this.setupDragAndDrop(
            this.elements.decodeDropArea,
            this.elements.decodeFileInput,
            this.elements.decodePreview,
            'decode'
        );

        this.elements.messageInput.addEventListener('input', () => {
            this.elements.encodeButton.disabled = !this.elements.messageInput.value || !this.state.encodeFile;
        });
    }

    /**
     * Configura os eventos de drag and drop para uma área específica
     */
    setupDragAndDrop(dropArea, fileInput, previewImg, type) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, (e) => this.preventDefaults(e));
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, () => this.highlight(dropArea));
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, () => this.unhighlight(dropArea));
        });

        dropArea.addEventListener('drop', (e) => {
            const file = e.dataTransfer.files[0];
            this.handleFile(file, previewImg, type);
        });

        dropArea.addEventListener('click', () => fileInput.click());

        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            this.handleFile(file, previewImg, type);
        });
    }

    /**
     * Previne comportamentos padrão de eventos
     */
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    /**
     * Destaca a área de drop quando um arquivo está sendo arrastado sobre ela
     */
    highlight(element) {
        element.style.borderColor = '#2563eb';
        element.style.backgroundColor = 'rgba(37, 99, 235, 0.1)';
    }

    /**
     * Remove o destaque da área de drop
     */
    unhighlight(element) {
        element.style.borderColor = '';
        element.style.backgroundColor = '';
    }

    /**
     * Processa o arquivo selecionado
     */
    handleFile(file, previewImg, type) {
        if (!file) {
            console.log('Nenhum arquivo selecionado');
            return;
        }

        if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
            this.updateStatus(
                type === 'encode' ? this.elements.encodeStatus : this.elements.decodeStatus,
                'Por favor, selecione um arquivo de imagem válido (PNG, JPG ou BMP).',
                true
            );
            return;
        }

        if (file.size > MAX_FILE_SIZE) {
            this.updateStatus(
                type === 'encode' ? this.elements.encodeStatus : this.elements.decodeStatus,
                'O arquivo é muito grande. O tamanho máximo é 16MB.',
                true
            );
            return;
        }

        // Armazena o arquivo no estado
        if (type === 'encode') {
            this.state.encodeFile = file;
            this.elements.encodeButton.disabled = !this.elements.messageInput.value;
        } else {
            this.state.decodeFile = file;
            this.elements.decodeButton.disabled = false;
        }

        // Mostra preview
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImg.src = e.target.result;
            previewImg.hidden = false;
        };
        reader.readAsDataURL(file);
    }

    /**
     * Atualiza a mensagem de status
     */
    updateStatus(element, message, isError = false) {
        element.textContent = message;
        element.className = 'status-message ' + (isError ? 'error' : 'success');
    }

    /**
     * Mostra o overlay de loading
     */
    showLoading(message = 'Processando...') {
        const loadingText = this.elements.loadingOverlay.querySelector('p');
        if (loadingText) {
            loadingText.textContent = message;
        }
        this.elements.loadingOverlay.hidden = false;
    }

    /**
     * Esconde o overlay de loading
     */
    hideLoading() {
        this.elements.loadingOverlay.hidden = true;
    }

    /**
     * Limpa o formulário de codificação
     */
    resetEncodeForm() {
        this.elements.encodeFileInput.value = '';
        this.elements.messageInput.value = '';
        this.elements.encodePreview.hidden = true;
        this.elements.encodeButton.disabled = true;
        this.state.encodeFile = null;
    }

    /**
     * Limpa o formulário de decodificação
     */
    resetDecodeForm() {
        this.elements.decodeFileInput.value = '';
        this.elements.decodePreview.hidden = true;
        this.elements.decodeButton.disabled = true;
        this.state.decodeFile = null;
    }

    /**
     * Cria e dispara o download de um arquivo
     */
    downloadFile(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}
