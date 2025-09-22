from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from sqlmodel import Session, select
from fastapi_backend.database.db_writer import engine
from fastapi_backend.database.models import BlueTeams, CheckInstance
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/scoreboard", response_model=Dict[str, Any])
async def get_scoreboard():
    try:
        with Session(engine) as session:
            # Query all scoreboard entries ordered by timestamp ascending, then team_num
            statement = select(BlueTeams,CheckInstance).join(CheckInstance, BlueTeams.last_check_id == CheckInstance.check_id).order_by(CheckInstance.timestamp.asc(), BlueTeams.team_num.asc())
            results = session.exec(statement).all()
            if not results:
                return {"time": []}  # no data
            print(f"{results}")
            # Extract unique timestamps sorted
            timestamps = sorted(set(r[1].timestamp for r in results))
            # Format times as HH:mm
            time_strs = [ts.strftime("%H:%M") for ts in timestamps]

            # Extract unique team numbers
            team_nums = sorted(set(r[0].team_num for r in results))

            # Prepare empty data dict
            data = {"time": time_strs}
            for team_num in team_nums:
                data[f"team{team_num}"] = [0] * len(timestamps)

            # Fill in scores
            # Create a mapping from timestamp to index for quick lookup
            ts_index = {ts: i for i, ts in enumerate(timestamps)}

            for blue_team, check_instance in results:
                idx = ts_index[check_instance.timestamp]
                key = f"team{blue_team.team_num}"
                data[key][idx] = blue_team.total_score


            return data

    except Exception as e:
        logger.error(f"Failed to fetch scoreboard data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch scoreboard data")
