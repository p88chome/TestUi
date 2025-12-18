from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import RunExecution
from app.schemas.all import RunExecutionOut

router = APIRouter(prefix="/runs", tags=["runs"])

@router.get("/{run_id}", response_model=RunExecutionOut)
def get_run(run_id: UUID, db: Session = Depends(get_db)):
    obj = db.query(RunExecution).filter(RunExecution.id == run_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Run not found")
    return obj
