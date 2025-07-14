# models/database.py
from sqlmodel import SQLModel, create_engine

DATABASE_URL = "sqlite:///./imobiliaria.db"
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    from models.models import Imovel
    SQLModel.metadata.create_all(engine)
