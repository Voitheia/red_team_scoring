from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging
from fastapi_backend.database.models import Users
from fastapi_backend.utils.auth import get_current_user, SECRET_KEY

from fastapi_backend.core.competition_state import CompetitionStatus

router = APIRouter(prefix="/admin", tags=["admin"])
logger = logging.getLogger(__name__)

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

@router.post("/deploy_iocs")
async def deploy_iocs(current_user: Users = Depends(get_current_user), orch=Depends(get_orchestrator)) -> Dict[str, Any]:
    """Deploy IOCs to all target systems"""
    try:
        check_admin(current_user)
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
        check_admin(current_user)
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
        check_admin(current_user)
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
        check_admin(current_user)
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
        check_admin(current_user)
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
        check_admin(current_user)
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