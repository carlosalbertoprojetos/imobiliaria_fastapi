# Importa classes e funções do FastAPI para criar rotas, exceções HTTP, upload de arquivos, etc.
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
# Importa resposta para servir arquivos diretamente
from fastapi.responses import FileResponse
# Importa esquema de autenticação OAuth2
from fastapi.security import OAuth2PasswordBearer
# Importa tipos para tipagem estática
from typing import List, Optional
# Importa UUID para gerar identificadores únicos
from uuid import uuid4, UUID
# Importa módulos para manipulação de arquivos
import shutil
import os
# Importa SQLModel e sessão do banco
from sqlmodel import Session, select
from models.models import Imovel
from models.database import engine
from sqlalchemy.orm import sessionmaker

# Supondo que você já tenha o engine definido
# engine = create_engine(...)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

UPLOAD_DIR = "uploads"
# Garante que o diretório de uploads existe
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Rota para listar todos os imóveis cadastrados
@router.get("/imoveis", response_model=List[Imovel])
def listar_imoveis(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    imoveis = db.query(Imovel).all()
    return imoveis

# Rota para criar um novo imóvel
@router.post("/imoveis", response_model=Imovel, status_code=201)
def criar_imovel(
    titulo: str = Form(...),
    descricao: Optional[str] = Form(None),
    preco: float = Form(...),
    endereco: str = Form(...),
    imagem: Optional[UploadFile] = File(None),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    imagem_url = None
    if imagem:
        nome_arquivo = f"{uuid4()}_{imagem.filename}"
        caminho_arquivo = os.path.join(UPLOAD_DIR, nome_arquivo)
        with open(caminho_arquivo, "wb") as buffer:
            shutil.copyfileobj(imagem.file, buffer)
        imagem_url = f"/uploads/{nome_arquivo}"

    novo_imovel = Imovel(
        titulo=titulo,
        descricao=descricao,
        preco=preco,
        endereco=endereco,
        imagem_url=imagem_url,
        dono=token
    )
    db.add(novo_imovel)
    db.commit()
    db.refresh(novo_imovel)
    return novo_imovel

# Rota para obter detalhes de um imóvel específico pelo id
@router.get("/imoveis/{id}", response_model=Imovel)
def get_imovel(id: str, db: Session = Depends(get_db)):
    # Se o id for passado como UUID, converta para string
    # id = str(id)  # Se o parâmetro já for string, não precisa dessa linha
    imovel = db.query(Imovel).filter(Imovel.id == id).first()
    if not imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    return imovel

# Rota para deletar um imóvel pelo id (apenas se o dono for o mesmo do token)
@router.delete("/imoveis/{imovel_id}", status_code=204)
def deletar_imovel(imovel_id: str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    imovel = db.query(Imovel).filter(Imovel.id == imovel_id).first()
    if not imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    if imovel.dono != token:
        raise HTTPException(status_code=403, detail="Você não tem permissão para deletar este imóvel")
    db.delete(imovel)
    db.commit()
    return

# Rota para servir arquivos de imagem enviados
@router.get("/uploads/{file_name}")
def get_uploaded_file(file_name: str):
    file_path = os.path.join(UPLOAD_DIR, file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    return FileResponse(file_path)

# Endpoint para editar imóvel (PUT)
@router.put("/imoveis/{id}", response_model=Imovel)
async def editar_imovel(
    id: str,
    titulo: Optional[str] = Form(None),
    descricao: Optional[str] = Form(None),
    preco: Optional[float] = Form(None),
    endereco: Optional[str] = Form(None),
    imagem: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    imovel = db.query(Imovel).filter(Imovel.id == id).first()
    if not imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")

    if titulo is not None:
        imovel.titulo = titulo
    if descricao is not None:
        imovel.descricao = descricao
    if preco is not None:
        imovel.preco = preco
    if endereco is not None:
        imovel.endereco = endereco

    if imagem:
        # Remove imagem antiga se existir
        if imovel.imagem_url:
            caminho_antigo = "." + imovel.imagem_url
            if os.path.exists(caminho_antigo):
                os.remove(caminho_antigo)
        # Salva nova imagem
        nome_arquivo = f"{id}_{imagem.filename}"
        caminho = os.path.join(UPLOAD_DIR, nome_arquivo)
        with open(caminho, "wb") as buffer:
            shutil.copyfileobj(imagem.file, buffer)
        imovel.imagem_url = f"/uploads/{nome_arquivo}"

    db.commit()
    db.refresh(imovel)
    return imovel

