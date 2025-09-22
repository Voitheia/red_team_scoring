from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from fastapi_backend.database.models import Users
from fastapi_backend.utils.auth import get_current_user
from sqlmodel import Session, select
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/details")
async def get_status(current_user: Users = Depends(get_current_user)) -> Dict[str, Any]:
    """Gets details for a specific team"""
    try:
        if (current_user.is_admin):
            # show for all teams
            print("Admin user, showing for all teams")
        elif (current_user.is_blue_team):
            print("User Blueteamer: " + current_user.blue_team_num)
        # Fix HTTPExceptions being eaten elsewhere
    except HTTPException:
        # Rethrow HTTPException without logging as error, just pass through
        raise
    except Exception as e:
        logger.error(f"Failed to get team details: {e}")
        raise HTTPException(status_code=500, detail=str(e))