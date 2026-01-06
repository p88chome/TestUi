from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.agent_service import AgentService
from pydantic import BaseModel

from app.api import deps
from app.models.user import User

router = APIRouter(prefix="/agent", tags=["agent"])

class AgentRunRequest(BaseModel):
    query: str
    session_id: str | None = None
    assistant_id: str | None = None

@router.post("/run")
async def run_agent(
    req: AgentRunRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Main entry point for the Agent.
    """
    service = AgentService(db)
    result = await service.run(
        req.query, 
        user_id=current_user.id, 
        session_id=req.session_id,
        assistant_id=req.assistant_id
    )
    return result
