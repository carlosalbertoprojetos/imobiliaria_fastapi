from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID, uuid4

class Imovel(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    titulo: str
    descricao: Optional[str] = None
    preco: float
    endereco: str
    imagem_url: Optional[str] = None
    dono: str
