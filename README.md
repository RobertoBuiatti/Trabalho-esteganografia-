# Plataforma de Esteganografia em Imagens

Plataforma web para ocultar e extrair mensagens secretas em imagens usando a técnica LSB (Least Significant Bit).

## 🚀 Funcionalidades

- Upload de imagens PNG, JPG e BMP
- Codificação de mensagens secretas em imagens
- Decodificação de mensagens ocultas
- Interface amigável com drag & drop
- Preview de imagens em tempo real
- Design responsivo

## 🛠️ Tecnologias

- Frontend:
  - HTML5
  - CSS3 com variáveis e design responsivo
  - JavaScript ES6+ com módulos
- Backend:
  - Python 3.8+
  - Flask
  - Pillow (PIL)
  - Flask-CORS
  - Gunicorn

## 📦 Instalação Local

### Backend

1. Navegue até a pasta do backend:
```bash
cd backend
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
```

3. Ative o ambiente virtual:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/macOS:
```bash
source venv/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

5. Execute o servidor:
```bash
python app.py
```

O backend estará rodando em `http://localhost:5000`

### Frontend

1. O frontend é estático e pode ser servido por qualquer servidor HTTP
2. Para desenvolvimento, você pode usar o módulo `http-server` do Node.js:

```bash
npx http-server frontend
```

O frontend estará disponível em `http://localhost:8080`

## 🚀 Deploy no Render

### Backend

1. Crie uma nova conta no [Render](https://render.com/)

2. Clique em "New +" e selecione "Web Service"

3. Conecte seu repositório GitHub

4. Configure o serviço:
   - Nome: `steganografia-api`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Diretório: `backend`

5. Configure as variáveis de ambiente:
   - `PYTHON_VERSION`: `3.9.12`
   - `FLASK_ENV`: `production`

6. Clique em "Create Web Service"

### Frontend

1. No Render, clique em "New +" e selecione "Static Site"

2. Conecte seu repositório GitHub

3. Configure o site:
   - Nome: `steganografia`
   - Branch: `main`
   - Diretório: `frontend`
   - Build Command: deixe em branco
   - Publish Directory: `.`

4. Clique em "Create Static Site"

5. Após o deploy, atualize a URL da API no arquivo `frontend/scripts/config.js` com a URL do seu backend no Render

## 📝 Uso

1. **Codificar Mensagem**:
   - Arraste ou selecione uma imagem
   - Digite sua mensagem secreta
   - Clique em "Codificar Mensagem"
   - Faça o download da imagem com a mensagem oculta

2. **Decodificar Mensagem**:
   - Arraste ou selecione uma imagem com mensagem oculta
   - Clique em "Extrair Mensagem"
   - A mensagem será exibida na tela

## ⚠️ Limitações

- Tamanho máximo de arquivo: 16MB
- Formatos suportados: PNG, JPG, BMP
- A mensagem deve conter apenas caracteres ASCII imprimíveis
- O tamanho máximo da mensagem depende do tamanho da imagem

## 🤝 Contribuindo

1. Faça o fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
