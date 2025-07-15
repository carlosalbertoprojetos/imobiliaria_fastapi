# Importa módulos necessários para manipulação de arquivos, testes e o app FastAPI
import os
import shutil
import uuid
import pytest
from fastapi.testclient import TestClient
from main import app

# Define o diretório de uploads usado nos testes
UPLOAD_DIR = "uploads"

# Fixture que limpa o diretório de uploads e o banco de dados em memória antes e depois de cada teste
def clean_uploads_and_db(monkeypatch):
    # Remove o diretório de uploads se existir
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)
    os.makedirs(UPLOAD_DIR)
    # Limpa o banco de dados em memória
    from routers import imoveis
    imoveis.imoveis_db.clear()
    yield
    # Limpa após o teste
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)

# Aplica a fixture automaticamente em todos os testes
@pytest.fixture(autouse=True)
def auto_clean_uploads_and_db(monkeypatch):
    yield from clean_uploads_and_db(monkeypatch)

# Fixture para criar um cliente de teste do FastAPI
def client():
    return TestClient(app)
@pytest.fixture
def client():
    return TestClient(app)

# Token fake para simular autenticação
FAKE_TOKEN = "usuario_teste"

# Função auxiliar para gerar o header de autenticação
def auth_header():
    return {"Authorization": f"Bearer {FAKE_TOKEN}"}

# Testa a listagem de imóveis quando o banco está vazio
def test_listar_imoveis_vazio(client):
    resp = client.get("/imoveis", headers=auth_header())
    assert resp.status_code == 200
    assert resp.json() == []

# Testa a criação de imóvel sem imagem
def test_criar_imovel_sem_imagem(client):
    data = {
        "titulo": "Casa Teste",
        "descricao": "Casa de teste",
        "preco": 123456.78,
        "endereco": "Rua Teste, 1"
    }
    resp = client.post("/imoveis", data=data, headers=auth_header())
    assert resp.status_code == 201
    body = resp.json()
    assert body["titulo"] == data["titulo"]
    assert body["descricao"] == data["descricao"]
    assert body["preco"] == data["preco"]
    assert body["endereco"] == data["endereco"]
    assert body["imagem_url"] is None
    assert body["dono"] == FAKE_TOKEN

# Testa a criação de imóvel com imagem
def test_criar_imovel_com_imagem(client):
    data = {
        "titulo": "Apto com Imagem",
        "descricao": "Apto com foto",
        "preco": 500000,
        "endereco": "Rua Foto, 2"
    }
    file_content = b"fake image data"
    files = {"imagem": ("foto.jpg", file_content, "image/jpeg")}
    resp = client.post("/imoveis", data=data, files=files, headers=auth_header())
    assert resp.status_code == 201
    body = resp.json()
    assert body["imagem_url"] is not None
    # Verifica se o arquivo foi salvo
    file_path = body["imagem_url"].replace("/uploads/", f"{UPLOAD_DIR}/")
    assert os.path.exists(file_path)

# Testa obter imóvel por id
def test_obter_imovel_por_id(client):
    # Cria imóvel
    data = {
        "titulo": "Imóvel Único",
        "descricao": "Teste único",
        "preco": 1000,
        "endereco": "Rua Única, 3"
    }
    resp = client.post("/imoveis", data=data, headers=auth_header())
    imovel = resp.json()
    imovel_id = imovel["id"]
    # Busca pelo id
    resp2 = client.get(f"/imoveis/{imovel_id}", headers=auth_header())
    assert resp2.status_code == 200
    assert resp2.json()["id"] == imovel_id

# Testa deletar imóvel
def test_deletar_imovel(client):
    # Cria imóvel
    data = {
        "titulo": "Para Deletar",
        "descricao": "Será deletado",
        "preco": 2000,
        "endereco": "Rua Delete, 4"
    }
    resp = client.post("/imoveis", data=data, headers=auth_header())
    imovel_id = resp.json()["id"]
    # Deleta
    resp2 = client.delete(f"/imoveis/{imovel_id}", headers=auth_header())
    assert resp2.status_code == 204
    # Verifica que não existe mais
    resp3 = client.get(f"/imoveis/{imovel_id}", headers=auth_header())
    assert resp3.status_code == 404

# Testa o endpoint de upload de imagem
def test_upload_imagem_endpoint(client):
    # Cria arquivo
    file_content = b"imagem para upload"
    file_name = f"{uuid.uuid4()}_foto.jpg"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    with open(file_path, "wb") as f:
        f.write(file_content)
    # Busca via endpoint
    resp = client.get(f"/uploads/{file_name}")
    assert resp.status_code == 200
    assert resp.content == file_content

# Testa a listagem de vários imóveis
def test_listar_varios_imoveis(client):
    for i in range(3):
        data = {
            "titulo": f"Imóvel {i}",
            "descricao": f"Desc {i}",
            "preco": 1000 + i,
            "endereco": f"Rua {i}"
        }
        client.post("/imoveis", data=data, headers=auth_header())
    resp = client.get("/imoveis", headers=auth_header())
    assert resp.status_code == 200
    assert len(resp.json()) == 3

# Testa erro ao buscar imóvel inexistente
def test_obter_imovel_inexistente(client):
    fake_id = str(uuid.uuid4())
    resp = client.get(f"/imoveis/{fake_id}", headers=auth_header())
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Imóvel não encontrado"

# Testa erro ao deletar imóvel inexistente
def test_deletar_imovel_inexistente(client):
    fake_id = str(uuid.uuid4())
    resp = client.delete(f"/imoveis/{fake_id}", headers=auth_header())
    # Mesmo que não exista, retorna 204 (idempotente)
    assert resp.status_code == 204

# Testa erro de autenticação ao acessar endpoints protegidos
def test_sem_token(client):
    # Listar imóveis sem token
    resp = client.get("/imoveis")
    assert resp.status_code == 401
    # Criar imóvel sem token
    data = {
        "titulo": "Sem Token",
        "descricao": "Teste",
        "preco": 1,
        "endereco": "Rua"
    }
    resp2 = client.post("/imoveis", data=data)
    assert resp2.status_code == 401
    # Deletar imóvel sem token
    resp3 = client.delete("/imoveis/123")
    assert resp3.status_code == 401 