# Sistema de Gestão Imobiliária - API SaaS

API simples e moderna para cadastro e gerenciamento de imóveis em SaaS, agora com persistência real em banco de dados SQLite.

---

## Tecnologias Utilizadas

- Python 3.10+
- FastAPI
- SQLModel
- SQLite
- Uvicorn
- Pydantic
- UUID (identificador único para imóveis)

---

## Instalação

```bash
# Clone o repositório
git clone https://github.com/carlosalbertoprojetos/imobiliaria_fastapi
cd imobiliaria-api

# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt
```

---

## ▶Executar o Sistema

```bash
uvicorn main:app --reload
```

Acesse o navegador:

🔗 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Explicações Técnicas

- **FastAPI:** Framework moderno, rápido e assíncrono com documentação automática.
- **SQLModel:** Biblioteca de ORM moderna baseada em Pydantic + SQLAlchemy.
- **SQLite:** Banco de dados local leve e embutido.
- **UUID:** Garante que cada imóvel tenha um identificador único e seguro.

---

## 🗂 Estrutura do Projeto

```
imobiliaria-api/
├── main.py                 # Ponto de entrada da aplicação
├── routers/                # Rotas da aplicação
│   ├── auth.py             # Login e segurança
│   └── imoveis.py          # CRUD de imóveis com banco
├── models/                 # Modelos SQLModel usados no SQLite
│   └── models.py
├── uploads/                # Onde as imagens são salvas
├── requirements.txt        # Dependências do projeto
├── .gitignore
└── README.md
```

---

# 👤 Guia do Usuário: Como Usar o Sistema de Gestão Imobiliária

Este sistema permite que você **cadastre, visualize e remova imóveis**, diretamente do navegador.

---

## 1. Acesse a interface no navegador

Após iniciar o sistema, abra:

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 2. Login no sistema

Antes de cadastrar imóveis, você precisa se autenticar:

- Vá na rota: `POST /token`
- Preencha:
  - `username`: `admin@example.com`
  - `password`: `123`
- Clique em `Execute` e copie o `access_token` retornado

---

## 3. Autorize seu acesso

- Clique em `Authorize` no topo direito
- Cole o token no formato:
```
Bearer admin@example.com
```
- Clique em `Authorize` e depois em `Close`

---

## 4. Cadastrar imóvel

- Acesse a rota: `POST /imoveis`
- Preencha os campos do formulário:
  - `titulo`
  - `descricao`
  - `preco`
  - `endereco`
  - `imagem` (opcional)
- Clique em `Execute`

---

## 5. Listar todos os imóveis

- Rota: `GET /imoveis`
- Clique em `Try it out` e `Execute` para ver os imóveis cadastrados.

---

## 6. Detalhar imóvel específico

- Rota: `GET /imoveis/{imovel_id}`
- Informe o ID retornado na listagem

---

## 7. Remover imóvel

- Rota: `DELETE /imoveis/{imovel_id}`
- O imóvel será removido apenas se for do usuário logado.

---

## 8. Ver imagem do imóvel

Abra no navegador:

```
http://127.0.0.1:8000/uploads/NOME_DA_IMAGEM.jpg
```

---

## Sempre que reiniciar o computador

Ative o ambiente virtual novamente e rode o servidor com:

```bash
uvicorn main:app --reload
```

---

## Pronto!

Você agora tem um sistema imobiliário simples, funcional e com dados reais armazenados localmente via SQLite!