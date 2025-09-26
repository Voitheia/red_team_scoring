from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from sqlmodel import Session, select
from fastapi_backend.database.models import Users, TeamLatestIocDetails
from fastapi_backend.utils.auth import get_current_user
from fastapi_backend.database.db_writer import engine
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/details", response_model=Dict[str, Any])
async def get_status(current_user: Users = Depends(get_current_user)) -> Dict[str, Any]:
    """Gets IOC details for a specific team or all teams (if admin)"""
    try:
        with Session(engine) as session:
            query = select(TeamLatestIocDetails)

            if current_user.is_admin:
                # Admin sees all teams
                pass
            elif current_user.is_blue_team:
                # Restrict to this user's team
                query = query.where(TeamLatestIocDetails.team_num == current_user.blue_team_num)
            else:
                raise HTTPException(status_code=403, detail="Unauthorized to view details")

            results = session.exec(query).all()

            return {
                "details": [
                    {
                        "team_num": r.team_num,
                        "box_ip": r.box_ip,
                        "ioc_name": r.ioc_name,
                        "difficulty": r.difficulty,
                        "status": r.status,
                        "error": r.error,
                        "points": r.points,
                    }
                    for r in results
                ]
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get team details: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch team details")
