from fastapi import APIRouter, HTTPException, Depends, Body, Query
from typing import Dict, Any, Optional
from sqlmodel import Session, select
import logging
from fastapi_backend.database.models import Users
from fastapi_backend.database.db_writer import engine
from fastapi_backend.utils.auth import Users, get_current_user, SECRET_KEY, hash_password
from pydantic import BaseModel
from fastapi_backend.core.competition_state import CompetitionStatus
import bcrypt

router = APIRouter(prefix="/admin", tags=["admin"])
logger = logging.getLogger(__name__)

class DelUserRequest(BaseModel):
    user_id: int

class AddUserRequest(BaseModel):
    user_id: int
    username: str
    password: str
    is_admin: bool
    is_blue_team: bool
    blue_team_num: Optional[int] = None

class ChangePasswordRequest(BaseModel):
    user_id: int
    password: str


def get_orchestrator():
    """Dependency to get orchestrator instance"""
    from fastapi_backend.main import orchestrator
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    return orchestrator

async def check_admin(current_user: Users):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail=f"Account accessing is not an administrator."
        )
    return


@router.get("/get_users")
async def get_users(
    current_user: Users = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Returns a list of all users with relevant info. Admin-only.
    """
    await check_admin(current_user)

    try:
        with Session(engine) as session:
            statement = select(Users).order_by(Users.user_id)
            results = session.exec(statement).all()

        users_data = [
            {
                "user_id": user.user_id,
                "username": user.username,
                "is_admin": user.is_admin,
                "is_blue_team": user.is_blue_team,
                "blue_team_num": user.blue_team_num,
            }
            for user in results
        ]

        return {
            "status": "success",
            "users": users_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve users: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch users")


from fastapi import Body

@router.delete("/remove_user")
async def remove_user(
    user_req: DelUserRequest = Body(...),
    current_user: Users = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Remove a user by user_id. Admin-only.
    """
    await check_admin(current_user)

    try:
        if current_user.user_id == user_req.user_id:
            raise HTTPException(status_code=400, detail="You cannot remove yourself.")

        with Session(engine) as session:
            target_user = session.get(Users, user_req.user_id)
            if not target_user:
                raise HTTPException(status_code=404, detail="User not found")

            session.delete(target_user)
            session.commit()

        return {
            "status": "success",
            "message": f"User ID {user_req.user_id} deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete user {user_req.user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/add_user")
async def add_user(user: AddUserRequest, current_user: Users = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Add a new user. Admin-only.
    """
    await check_admin(current_user)

    try:
        with Session(engine) as session:
            # Check for existing ID
            if session.get(Users, user.user_id):
                raise HTTPException(status_code=400, detail="User ID already exists")

            # Check for existing username
            existing_username = session.exec(
                select(Users).where(Users.username == user.username)
            ).first()
            if existing_username:
                raise HTTPException(status_code=400, detail="Username already exists")

            # hash alert
            hashed_password = hash_password(user.password)

            # Create new user
            new_user = Users(
                user_id=user.user_id,
                username=user.username,
                password=hashed_password,
                is_admin=user.is_admin,
                is_blue_team=user.is_blue_team,
                blue_team_num=user.blue_team_num if user.is_blue_team else None
            )

            session.add(new_user)
            session.commit()

        return {
            "status": "success",
            "message": f"User '{user.username}' added successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add user: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/change_password")
def change_password(user: ChangePasswordRequest, current_user: Users = Depends(get_current_user)):
    """
    Change the password for a user.
    """
    # Check if the current user is admin or the user themselves
    if not current_user.is_admin and current_user.user_id != user.user_id:
        raise HTTPException(status_code=403, detail="Permission denied")

    # Hash the new password
    hashed_password = hash_password(user.password)

    # Update the password in the database
    with Session(engine) as session:
        user = session.get(Users, user.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.password = hashed_password
        session.commit()

    return {"status": "success", "message": "Password changed successfully"}

@router.post("/deploy_iocs")
async def deploy_iocs(current_user: Users = Depends(get_current_user), orch=Depends(get_orchestrator)) -> Dict[str, Any]:
    """Deploy IOCs to all target systems"""
    try:
        await check_admin(current_user)
        if orch.state.status != CompetitionStatus.NOT_STARTED:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot deploy IOCs in state: {orch.state.status.value}"
            )

        results = await orch.deploy_iocs()
        return {
            "status": "success",
            "message": "IOCs deployment initiated",
            "results": results
        }
    # Fix HTTPExceptions being eaten elsewhere
    except HTTPException:
        # Rethrow HTTPException without logging as error, just pass through
        raise
    except Exception as e:
        logger.error(f"Failed to deploy IOCs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run_checks")
async def run_checks(current_user: Users = Depends(get_current_user),orch=Depends(get_orchestrator)) -> Dict[str, Any]:
    """Manually trigger a check cycle"""
    try:
        await check_admin(current_user)
        if not orch.state.can_run_checks():
            raise HTTPException(
                status_code=400,
                detail=f"Cannot run checks in state: {orch.state.status.value}"
            )

        await orch.run_checks()
        return {
            "status": "success",
            "message": "Check cycle initiated",
            "details": {
                "total_checks": orch.state.total_checks_run,
                "last_check": orch.state.last_check_time.isoformat() if orch.state.last_check_time else None
            }
        }
    # Fix HTTPExceptions being eaten elsewhere
    except HTTPException:
        # Rethrow HTTPException without logging as error, just pass through
        raise
    except Exception as e:
        logger.error(f"Failed to run checks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start_comp")
async def start_competition(current_user: Users = Depends(get_current_user),orch=Depends(get_orchestrator)) -> Dict[str, Any]:
    """Start the competition"""
    try:
        await check_admin(current_user)
        await orch.start_competition()
        return {
            "status": "success",
            "message": "Competition started",
            "details": orch.state.get_status_info()
        }
    # Fix HTTPExceptions being eaten elsewhere
    except HTTPException:
        # Rethrow HTTPException without logging as error, just pass through
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to start competition: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop_comp")
async def stop_competition(current_user: Users = Depends(get_current_user),orch=Depends(get_orchestrator)) -> Dict[str, Any]:
    """Stop the competition"""
    try:
        await check_admin(current_user)
        await orch.stop_competition()
        return {
            "status": "success",
            "message": "Competition stopped",
            "details": orch.state.get_status_info()
        }
    # Fix HTTPExceptions being eaten elsewhere
    except HTTPException:
        # Rethrow HTTPException without logging as error, just pass through
        raise
    except Exception as e:
        logger.error(f"Failed to stop competition: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_status(current_user: Users = Depends(get_current_user),orch=Depends(get_orchestrator)) -> Dict[str, Any]:
    """Get comprehensive system status"""
    try:
        await check_admin(current_user)
        return orch.get_status()
        # Fix HTTPExceptions being eaten elsewhere
    except HTTPException:
        # Rethrow HTTPException without logging as error, just pass through
        raise
    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset_data")
async def reset_data(current_user: Users = Depends(get_current_user),orch=Depends(get_orchestrator)) -> Dict[str, Any]:
    """Reset competition data (clear scores and checks)"""
    try:
        await check_admin(current_user)
        active = orch.state.is_active()
        if active:
            raise HTTPException(
                status_code=400,
                detail="Cannot reset data while competition is running"
            )


        # Reset state
        orch.state.reset()

        # Clear database (keeping teams and users)
        from sqlmodel import Session, delete
        from fastapi_backend.database.db_writer import engine
        from fastapi_backend.database.models import CheckInstance, IOCCheckResult

        with Session(engine) as session:
            # Delete all check results
            session.exec(delete(IOCCheckResult))
            session.exec(delete(CheckInstance))
            session.commit()

        return {
            "status": "success",
            "message": "Competition data reset successfully"
        }
    
    # Fix HTTPExceptions being eaten elsewhere
    except HTTPException:
        # Rethrow HTTPException without logging as error, just pass through
        raise

    except Exception as e:
        logger.error(f"Failed to reset data: {e}")
        raise HTTPException(status_code=500, detail=str(e))