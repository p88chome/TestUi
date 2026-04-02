from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import AIModel, LLMProvider
from pydantic import BaseModel, ConfigDict

router = APIRouter(prefix="/models", tags=["models"])

# Schemas
class AIModelBase(BaseModel):
    name: str
    provider: LLMProvider = LLMProvider.AZURE
    model_name: str | None = None
    deployment_name: str | None = None
    api_version: str | None = None
    description: str | None = None
    is_active: bool = False
    is_reasoning_model: bool = False  # True for o1/o3/o4-mini → uses max_completion_tokens

class AIModelCreate(AIModelBase):
    pass

class AIModelUpdate(BaseModel):
    name: str | None = None
    provider: LLMProvider | None = None
    model_name: str | None = None
    deployment_name: str | None = None
    api_version: str | None = None
    description: str | None = None
    is_active: bool | None = None
    is_reasoning_model: bool | None = None

class AIModelOut(AIModelBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

# Endpoints
@router.get("/", response_model=list[AIModelOut])
def list_models(db: Session = Depends(get_db)):
    try:
        models = db.query(AIModel).order_by(AIModel.name).all()
        return models
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Database Error in /models/: {str(e)}\nTraceback: {error_detail}")


@router.post("/", response_model=AIModelOut)
def create_model(model: AIModelCreate, db: Session = Depends(get_db)):
    # If creating as active, deactivate all others first
    if model.is_active:
        db.query(AIModel).update({AIModel.is_active: False})
    db_obj = AIModel(**model.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.put("/{model_id}", response_model=AIModelOut)
def update_model(model_id: UUID, model: AIModelUpdate, db: Session = Depends(get_db)):
    obj = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Model not found")

    # If activating this model, deactivate all others first
    if model.is_active is True:
        db.query(AIModel).filter(AIModel.id != model_id).update({AIModel.is_active: False})

    update_data = model.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(obj, key, value)

    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.post("/{model_id}/set-active", response_model=AIModelOut)
def set_active_model(model_id: UUID, db: Session = Depends(get_db)):
    """Atomically sets one model as active and deactivates all others."""
    obj = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Model not found")

    db.query(AIModel).update({AIModel.is_active: False})
    obj.is_active = True
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{model_id}")
def delete_model(model_id: UUID, db: Session = Depends(get_db)):
    obj = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Model not found")

    db.delete(obj)
    db.commit()
    return {"ok": True}
