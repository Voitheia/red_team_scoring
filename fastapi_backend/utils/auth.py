from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from fastapi_backend.database.models import Users
from fastapi_backend.database.db_writer import engine
from fastapi_backend.database.models import Users
import bcrypt

SECRET_KEY = "Sup3rS3cre3tRedTe3333am"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def hash_password(plain_password: str) -> str:
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def add_user(user: Users):
    with Session(engine) as session:
        # Check for existing ID if it's provided, otherwise just insert without it
        if user.user_id is not -1 and session.get(Users, user.user_id):
            raise HTTPException(status_code=400, detail="User ID already exists")

        # Check for existing username
        existing_username = session.exec(
            select(Users).where(Users.username == user.username)
        ).first()
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already exists")

        # hash the password
        hashed_password = hash_password(user.password)

        # Create new user
        if user.user_id:
            new_user = Users(
                user_id=user.user_id,
                username=user.username,
                password=hashed_password,
                is_admin=user.is_admin,
                is_blue_team=user.is_blue_team,
                blue_team_num=user.blue_team_num if user.is_blue_team else None
            )
        else:
            new_user = Users(
                username=user.username,
                password=hashed_password,
                is_admin=user.is_admin,
                is_blue_team=user.is_blue_team,
                blue_team_num=user.blue_team_num if user.is_blue_team else None
            )

        session.add(new_user)
        session.commit()
def get_user_from_token(token: str) -> Users:
    try:
        #print("Raw token received:", token)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        #print("JWT payload:", payload)

        user_id = payload.get("sub")
        #print("Extracted user_id:", user_id)

        with Session(engine) as session:
            user = session.exec(select(Users).where(Users.user_id == user_id)).first()
            #print("Found user in DB:", user)

            if user:
                return user

    except JWTError as e:
        print("JWT Error:", e)
    except Exception as e:
        print("General Error:", e)

    raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(token: str = Depends(oauth2_scheme)) -> Users:
    return get_user_from_token(token)