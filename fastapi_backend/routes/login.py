from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select
from fastapi_backend.database.db_writer import engine
from fastapi_backend.database.models import Users

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login_user(data: LoginRequest):
    with Session(engine) as session:
        statement = select(Users).where(
            Users.username == data.username,
            Users.password == data.password  # Probably should be hashing this lol
        )
        user = session.exec(statement).first()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        return {"detail": "Login successful", "user_id": user.user_id}