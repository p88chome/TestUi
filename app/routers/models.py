import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import AIModel, LLMProvider
from app.api import deps
from app.models.user import User
from pydantic import BaseModel, ConfigDict

logger = logging.getLogger(__name__)

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
    is_reasoning_model: bool = False

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
def list_models(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    try:
        return db.query(AIModel).order_by(AIModel.name).all()
    except Exception as e:
        logger.error("Failed to list models", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/", response_model=AIModelOut)
def create_model(
    model: AIModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
):
    if model.is_active:
        db.query(AIModel).update({AIModel.is_active: False})
    db_obj = AIModel(**model.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.put("/{model_id}", response_model=AIModelOut)
def update_model(
    model_id: UUID,
    model: AIModelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
):
    obj = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Model not found")

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
def set_active_model(
    model_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
):
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
def delete_model(
    model_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
):
    obj = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Model not found")

    db.delete(obj)
    db.commit()
    return {"ok": True}
