from fastapi import APIRouter, Depends
from fastapi_backend.database.models import Users
from fastapi_backend.utils.auth import get_current_user

router = APIRouter()

@router.get("/me")
def get_me(current_user: Users = Depends(get_current_user)):
    return {
        "user": {
            "user_id": current_user.user_id,
            "username": current_user.username
        }
    }