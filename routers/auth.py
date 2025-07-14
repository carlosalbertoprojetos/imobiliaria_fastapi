from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

fake_users_db = {
    "admin@example.com": {
        "username": "admin@example.com",
        "full_name": "Admin Imobiliária",
        "hashed_password": "fakehashed123",
    }
}

def fake_hash_password(password: str):
    return "fakehashed" + password

@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or fake_hash_password(form_data.password) != user["hashed_password"]:
        raise HTTPException(status_code=400, detail="Credenciais inválidas")
    return {"access_token": user["username"], "token_type": "bearer"}
