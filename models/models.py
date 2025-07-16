from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import uuid4
import os

class Imovel(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True, index=True)
    titulo: str
    descricao: Optional[str] = None
    preco: float
    endereco: str
    imagem_url: Optional[str] = None
    dono: str
