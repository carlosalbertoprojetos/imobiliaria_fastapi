# main.py
from fastapi import FastAPI
from routers import imoveis, auth
from models.database import create_db_and_tables
import os

app = FastAPI(title="Sistema de Gestão Imobiliária - API SaaS")

os.makedirs("uploads", exist_ok=True)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(auth.router)
app.include_router(imoveis.router)
