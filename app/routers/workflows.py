from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import Workflow, RunExecution
from app.schemas.all import WorkflowCreate, WorkflowOut, WorkflowUpdate, RunExecutionOut
from app.services.workflow_engine import WorkflowEngine, get_workflow_engine

router = APIRouter(prefix="/workflows", tags=["workflows"])

@router.get("/", response_model=list[WorkflowOut])
def list_workflows(db: Session = Depends(get_db)):
    return db.query(Workflow).all()

@router.post("/", response_model=WorkflowOut)
def create_workflow(workflow: WorkflowCreate, db: Session = Depends(get_db)):
    # Convert pydantic models to dict for JSONB storage
    steps_data = [step.model_dump() for step in workflow.steps]
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
        obj.steps = [step.model_dump() for step in workflow.steps]
    
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.post("/{workflow_id}/run", response_model=RunExecutionOut)
def run_workflow(
    workflow_id: UUID, 
    input_payload: dict, # Expecting raw dict in body
    db: Session = Depends(get_db),
    # engine: WorkflowEngine = Depends(get_workflow_engine) # In simpler deps, initializing here
):
    engine = WorkflowEngine(db)
    try:
        # Run synchronously for MVP simplicity, usually this should be background task (Celery/RQ)
        # But user spec asked explicitly for "run_workflow" returning RunExecution id.
        # We'll execute it and return the result immediately since it's mock and fast.
        # If it was slow, we'd create the record first and return PENDING, then run in background.
        # Let's do the proper pattern: Create PENDING record, return it.
        # However, the WorkflowEngine.run_workflow in previous step executes it fully.
        # Let's use that.
        result = engine.run_workflow(workflow_id, input_payload)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
