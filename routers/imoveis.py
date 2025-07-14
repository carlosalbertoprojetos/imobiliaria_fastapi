# Importa classes e funções do FastAPI para criar rotas, exceções HTTP, upload de arquivos, etc.
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
# Importa resposta para servir arquivos diretamente
from fastapi.responses import FileResponse
# Importa esquema de autenticação OAuth2
from fastapi.security import OAuth2PasswordBearer
# Importa BaseModel e Field do Pydantic para validação de dados
from pydantic import BaseModel, Field
# Importa tipos para tipagem estática
from typing import List, Optional
# Importa UUID para gerar identificadores únicos
from uuid import UUID, uuid4
# Importa módulos para manipulação de arquivos
import shutil
import os

# Cria um roteador para agrupar rotas relacionadas
router = APIRouter()
# Define o esquema de autenticação OAuth2, usando o endpoint /token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Define o diretório onde os uploads de imagens serão salvos
UPLOAD_DIR = "uploads"

# Modelo base para um imóvel, usado para entrada e saída de dados
class ImovelBase(BaseModel):
    titulo: str = Field(..., example="Apartamento 3 quartos")  # Título do imóvel
    descricao: Optional[str] = Field(None, example="Bem localizado")  # Descrição opcional
    preco: float = Field(..., example=500000.0)  # Preço do imóvel
    endereco: str = Field(..., example="Rua Exemplo, 123")  # Endereço do imóvel
    imagem_url: Optional[str] = Field(None, example="/uploads/nome.jpg")  # URL da imagem

# Modelo completo de imóvel, incluindo id e dono
class Imovel(ImovelBase):
    id: UUID  # Identificador único do imóvel
    dono: str  # Dono do imóvel (identificado pelo token)

# Banco de dados em memória (lista) para armazenar imóveis
imoveis_db: List[Imovel] = []

# Rota para listar todos os imóveis cadastrados
@router.get("/imoveis", response_model=List[Imovel])
def listar_imoveis(token: str = Depends(oauth2_scheme)):
    return imoveis_db  # Retorna todos os imóveis

# Rota para criar um novo imóvel
@router.post("/imoveis", response_model=Imovel, status_code=201)
def criar_imovel(
    titulo: str = Form(...),  # Recebe título via formulário
    descricao: Optional[str] = Form(None),  # Recebe descrição opcional
    preco: float = Form(...),  # Recebe preço via formulário
    endereco: str = Form(...),  # Recebe endereço via formulário
    imagem: Optional[UploadFile] = File(None),  # Recebe arquivo de imagem opcional
    token: str = Depends(oauth2_scheme)  # Recebe token de autenticação
):
    imagem_url = None  # Inicializa URL da imagem
    if imagem:
        # Gera nome único para o arquivo e salva no diretório de uploads
        nome_arquivo = f"{uuid4()}_{imagem.filename}"
        caminho_arquivo = os.path.join(UPLOAD_DIR, nome_arquivo)
        with open(caminho_arquivo, "wb") as buffer:
            shutil.copyfileobj(imagem.file, buffer)
        imagem_url = f"/uploads/{nome_arquivo}"

    # Cria novo objeto Imovel com os dados recebidos
    novo_imovel = Imovel(
        id=uuid4(),  # Gera novo UUID
        titulo=titulo,
        descricao=descricao,
        preco=preco,
        endereco=endereco,
        imagem_url=imagem_url,
        dono=token  # Usa o token como identificador do dono
    )
    imoveis_db.append(novo_imovel)  # Adiciona imóvel ao banco de dados em memória
    return novo_imovel  # Retorna o imóvel criado

# Rota para obter detalhes de um imóvel específico pelo id
@router.get("/imoveis/{imovel_id}", response_model=Imovel)
def obter_imovel(imovel_id: UUID, token: str = Depends(oauth2_scheme)):
    for imovel in imoveis_db:
        if imovel.id == imovel_id:
            return imovel  # Retorna o imóvel se encontrado
    raise HTTPException(status_code=404, detail="Imóvel não encontrado")  # Se não encontrar, retorna erro 404

# Rota para deletar um imóvel pelo id (apenas se o dono for o mesmo do token)
@router.delete("/imoveis/{imovel_id}", status_code=204)
def deletar_imovel(imovel_id: UUID, token: str = Depends(oauth2_scheme)):
    global imoveis_db
    # Remove imóvel apenas se o id e o dono coincidirem
    imoveis_db = [i for i in imoveis_db if i.id != imovel_id or i.dono != token]
    return  # Retorna vazio (status 204)

# Rota para servir arquivos de imagem enviados
@router.get("/uploads/{file_name}")
def get_uploaded_file(file_name: str):
    file_path = os.path.join(UPLOAD_DIR, file_name)  # Monta caminho do arquivo
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Imagem não encontrada")  # Se não existir, retorna erro 404
    return FileResponse(file_path)  # Retorna o arquivo como resposta
