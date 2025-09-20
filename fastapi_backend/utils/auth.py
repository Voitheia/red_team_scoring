from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from fastapi_backend.database.models import Users
from fastapi_backend.database.db_writer import engine

SECRET_KEY = "Sup3rS3cre3tRedTe3333am"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_user_from_token(token: str) -> Users:
    try:
        print("🔐 Raw token received:", token)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("✅ JWT payload:", payload)

        user_id = payload.get("sub")
        print("👤 Extracted user_id:", user_id)

        with Session(engine) as session:
            user = session.exec(select(Users).where(Users.user_id == user_id)).first()
            print("📦 Found user in DB:", user)

            if user:
                return user

    except JWTError as e:
        print("❌ JWT Error:", e)
    except Exception as e:
        print("❌ General Error:", e)

    raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(token: str = Depends(oauth2_scheme)) -> Users:
    return get_user_from_token(token)