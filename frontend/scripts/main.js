// Configuração da API
const API_URL = 'https://steganografia-api.onrender.com';

// Elementos do DOM
const elements = {
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

// Estado da aplicação
let encodeFile = null;
let decodeFile = null;

// Funções utilitárias
const showLoading = () => elements.loadingOverlay.hidden = false;
const hideLoading = () => elements.loadingOverlay.hidden = true;

function showStatus(element, message, isError = false) {
    element.textContent = message;
    element.className = `status-message ${isError ? 'error' : 'success'}`;
    setTimeout(() => {
        element.textContent = '';
        element.className = 'status-message';
    }, 5000);
}

// Manipulação da área de arrastar e soltar
function setupDropArea(dropArea, fileInput, previewElement, fileStorage) {
    const handleDragEvent = (e) => {
        e.preventDefault();
        e.stopPropagation();
    };

    const highlightDropArea = () => dropArea.classList.add('highlight');
    const unhighlightDropArea = () => dropArea.classList.remove('highlight');

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, handleDragEvent);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlightDropArea);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlightDropArea);
    });

    dropArea.addEventListener('drop', (e) => {
        handleFile(e.dataTransfer.files[0], previewElement, fileStorage);
    });

    dropArea.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', () => {
        handleFile(fileInput.files[0], previewElement, fileStorage);
    });
}

// Manipulação de arquivos
function handleFile(file, previewElement, fileStorage) {
    if (!file || !file.type.match(/^image\/(jpeg|png|bmp)$/)) {
        showStatus(
            fileStorage === 'encode' ? elements.encodeStatus : elements.decodeStatus,
            'Por favor, selecione uma imagem válida (PNG, JPG, ou BMP)',
            true
        );
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        previewElement.src = e.target.result;
        previewElement.hidden = false;
        
        if (fileStorage === 'encode') {
            encodeFile = file;
            elements.encodeButton.disabled = !elements.messageInput.value;
        } else {
            decodeFile = file;
            elements.decodeButton.disabled = false;
        }
    };
    reader.readAsDataURL(file);
}

// Funções de codificação e decodificação
async function encodeMessage() {
    if (!encodeFile || !elements.messageInput.value) return;

    showLoading();
    const formData = new FormData();
    formData.append('image', encodeFile);
    formData.append('text', elements.messageInput.value);

    try {
        const response = await fetch(`${API_URL}/api/hide`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erro ao processar a imagem');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `esteganografia_${encodeFile.name}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        showStatus(elements.encodeStatus, 'Mensagem ocultada com sucesso!');
        elements.messageInput.value = '';
        elements.encodePreview.hidden = true;
        elements.encodeButton.disabled = true;
        encodeFile = null;
    } catch (error) {
        showStatus(elements.encodeStatus, error.message, true);
    } finally {
        hideLoading();
    }
}

async function decodeMessage() {
    if (!decodeFile) return;

    showLoading();
    const formData = new FormData();
    formData.append('image', decodeFile);

    try {
        const response = await fetch(`${API_URL}/api/extract`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erro ao extrair a mensagem');
        }

        const data = await response.json();
        if (!data.text) {
            throw new Error('Nenhuma mensagem encontrada na imagem');
        }

        elements.decodedMessage.textContent = data.text;
        showStatus(elements.decodeStatus, 'Mensagem extraída com sucesso!');
    } catch (error) {
        showStatus(elements.decodeStatus, error.message, true);
        elements.decodedMessage.textContent = '';
    } finally {
        hideLoading();
    }
}

// Inicialização
function init() {
    // Configurar áreas de arrastar e soltar
    setupDropArea(elements.encodeDropArea, elements.encodeFileInput, elements.encodePreview, 'encode');
    setupDropArea(elements.decodeDropArea, elements.decodeFileInput, elements.decodePreview, 'decode');

    // Configurar eventos
    elements.messageInput.addEventListener('input', () => {
        elements.encodeButton.disabled = !elements.messageInput.value || !encodeFile;
    });

    elements.encodeButton.addEventListener('click', encodeMessage);
    elements.decodeButton.addEventListener('click', decodeMessage);

    // Desabilitar botões inicialmente
    elements.encodeButton.disabled = true;
    elements.decodeButton.disabled = true;
}

// Iniciar aplicação quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', init);
