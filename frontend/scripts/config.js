// Configuração da API
export const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://127.0.0.1:5000'
    : 'https://steganografia-api.onrender.com'; // Substitua com sua URL do Render

export const ALLOWED_IMAGE_TYPES = ['image/png', 'image/jpeg', 'image/bmp'];
export const MAX_FILE_SIZE = 16 * 1024 * 1024; // 16MB
