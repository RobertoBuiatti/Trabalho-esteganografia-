# Aplicação de Esteganografia em Imagens

Esta aplicação permite ocultar e recuperar mensagens secretas em imagens utilizando a técnica LSB (Least Significant Bit). O projeto é composto por um backend em Python/Flask e um frontend em HTML/CSS/JavaScript.

## 🚀 Funcionalidades

- Ocultar mensagens em imagens (PNG, JPG, JPEG)
- Extrair mensagens ocultas de imagens
- Interface intuitiva com suporte a drag-and-drop
- Feedback visual do processo
- Preview das imagens selecionadas

## 🛠️ Tecnologias Utilizadas

### Backend
- Python 3.x
- Flask 2.3.3
- Pillow 10.0.0 (Processamento de imagens)
- Flask-CORS 4.0.0 (Suporte a requisições cross-origin)
- Gunicorn 21.2.0 (Servidor WSGI para produção)

### Frontend
- HTML5
- CSS3
- JavaScript (ES6+)
- Arquitetura modular de CSS
- Design responsivo

## 📁 Estrutura do Projeto

```
.
├── backend/
│   ├── app.py          # Aplicação Flask
│   └── requirements.txt # Dependências Python
└── frontend/
    ├── index.html      # Página principal
    ├── scripts/
    │   └── main.js     # Lógica do frontend
    └── styles/         # Arquivos CSS modulares
        ├── animations.css
        ├── base.css
        ├── components.css
        ├── layout.css
        ├── main.css
        └── variables.css
```

## 💻 Como Executar

### Backend

1. Instale as dependências:
```bash
cd backend
pip install -r requirements.txt
```

2. Execute o servidor:
```bash
python app.py
```
O servidor estará disponível em `http://localhost:5000`

### Frontend

1. Abra o arquivo `frontend/index.html` em um navegador web
2. Ou sirva os arquivos usando um servidor HTTP simples

## 🔒 Funcionamento da Esteganografia

### Processo de Ocultação
1. A imagem é convertida para o formato RGB
2. O texto é convertido em binário
3. Cada bit do texto é armazenado no bit menos significativo de cada canal de cor (R,G,B)
4. Um delimitador é adicionado ao final do texto para marcação
5. A imagem processada é salva mantendo sua qualidade visual

### Processo de Extração
1. A imagem é lida e convertida para RGB
2. Os bits menos significativos são extraídos
3. Os bits são convertidos de volta para texto
4. O texto é extraído até encontrar o delimitador

## 🔍 API Endpoints

### POST /api/hide
Oculta uma mensagem em uma imagem.
- Body: FormData com `image` (arquivo) e `text` (mensagem)
- Retorna: Imagem processada

### POST /api/extract
Extrai uma mensagem de uma imagem.
- Body: FormData com `image` (arquivo)
- Retorna: JSON com a mensagem extraída

## ⚠️ Limitações

- Suporte apenas para imagens PNG e JPEG
- Tamanho máximo de arquivo: 16MB
- O tamanho da mensagem é limitado pela resolução da imagem
- A imagem de saída mantém o formato da imagem de entrada

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## ✨ Boas Práticas Implementadas

- Código modular e organizado
- Tratamento de erros robusto
- Feedback visual para o usuário
- Validação de entrada de arquivos
- Documentação clara e organizada
- Acessibilidade básica implementada
- Arquivos CSS modulares para melhor manutenção
