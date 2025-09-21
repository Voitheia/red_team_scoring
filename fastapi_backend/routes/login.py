from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select
from fastapi_backend.database.db_writer import engine
from fastapi_backend.database.models import Users
from fastapi_backend.utils.auth import get_current_user, SECRET_KEY
from jose import JWTError, jwt

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login_user(data: LoginRequest):
    with Session(engine) as session:
        statement = select(Users).where(
            Users.username == data.username,
            Users.password == data.password  # hash this in production!
        )
        user = session.exec(statement).first()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = jwt.encode({"sub": str(user.user_id)}, SECRET_KEY, algorithm="HS256")

        return {
            "token": token,
            "user_id": user.user_id,
            "username": user.username,
            "admin": user.is_admin
        }

@router.get("/me")
def get_me(current_user: Users = Depends(get_current_user)):
    return {
        "user": {
            "user_id": current_user.user_id,
            "username": current_user.username,
            "admin": current_user.is_admin
        }
    }
