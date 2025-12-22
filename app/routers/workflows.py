from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import Workflow, RunExecution
from app.schemas.all import WorkflowCreate, WorkflowOut, WorkflowUpdate, RunExecutionOut, RunExecutionCreate
from app.services.workflow_engine import WorkflowEngine, get_workflow_engine

router = APIRouter(prefix="/workflows", tags=["workflows"])

@router.get("/", response_model=list[WorkflowOut])
def list_workflows(db: Session = Depends(get_db)):
    return db.query(Workflow).all()

@router.post("/", response_model=WorkflowOut)
def create_workflow(workflow: WorkflowCreate, db: Session = Depends(get_db)):
    # Convert pydantic models to JSON-serializable dict (convert UUID to str)
    steps_data = [step.model_dump(mode='json') for step in workflow.steps]
    db_obj = Workflow(
        name=workflow.name, 
        description=workflow.description, 
        steps=steps_data
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/{workflow_id}", response_model=WorkflowOut)
def get_workflow(workflow_id: UUID, db: Session = Depends(get_db)):
    obj = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return obj

@router.put("/{workflow_id}", response_model=WorkflowOut)
def update_workflow(workflow_id: UUID, workflow: WorkflowUpdate, db: Session = Depends(get_db)):
    obj = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    if workflow.name: obj.name = workflow.name
    if workflow.description: obj.description = workflow.description
    if workflow.steps is not None:
        obj.steps = [step.model_dump(mode='json') for step in workflow.steps]
    
    db.add(obj)
    db.commit()
    db.refresh(obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{workflow_id}")
def delete_workflow(workflow_id: UUID, db: Session = Depends(get_db)):
    obj = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Manually delete runs because FK ondelete="CASCADE" is not set in DB schema
    db.query(RunExecution).filter(RunExecution.workflow_id == workflow_id).delete()
    
    db.delete(obj)
    db.commit()
    return {"ok": True}

from app.api import deps
from app.models.user import User

@router.post("/{workflow_id}/run", response_model=RunExecutionOut)
def run_workflow(
    workflow_id: UUID, 
    run_req: RunExecutionCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    engine = WorkflowEngine(db)
    try:
        # Use run_req.input_payload instead of raw dict
        result = engine.run_workflow(workflow_id, run_req.input_payload, user_id=current_user.id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
