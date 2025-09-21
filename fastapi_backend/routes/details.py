from fastapi import APIRouter, Depends
from fastapi_backend.database.models import Users
from fastapi_backend.utils.auth import get_current_user

router = APIRouter()

