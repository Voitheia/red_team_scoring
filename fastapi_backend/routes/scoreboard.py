from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from sqlmodel import Session, select
from fastapi_backend.database.db_writer import engine
from fastapi_backend.database.models import BlueTeams, CheckInstance, BlueTeamsScoreboard
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/scoreboard", response_model=Dict[str, Any])
async def get_scoreboard():
    try:
        with Session(engine) as session:
            statement = select(BlueTeamsScoreboard).order_by(BlueTeamsScoreboard.team_num.asc())
            results = session.exec(statement).all()
            if not results:
                return {"teams": []}

            # Build the response
            data = {
                "teams": [
                    {
                        "team_num": r.team_num,
                        "total_score": r.total_score,
                        "last_check_score": r.last_check_score,
                        "last_check_time": r.last_check_time.isoformat() if r.last_check_time else None,
                    }
                    for r in results
                ]
            }
            return data

    except Exception as e:
        logger.error(f"Failed to fetch scoreboard data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch scoreboard data")
