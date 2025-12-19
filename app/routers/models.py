from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import AIModel
from pydantic import BaseModel, ConfigDict

router = APIRouter(prefix="/models", tags=["models"])

# Schemas
class AIModelBase(BaseModel):
    name: str
    deployment_name: str
    api_version: str
    description: str | None = None
    is_active: bool = False

class AIModelCreate(AIModelBase):
    pass

class AIModelUpdate(BaseModel):
    name: str | None = None
    deployment_name: str | None = None
    api_version: str | None = None
    description: str | None = None
    is_active: bool | None = None

class AIModelOut(AIModelBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

# Endpoints
@router.get("/", response_model=list[AIModelOut])
def list_models(db: Session = Depends(get_db)):
    return db.query(AIModel).order_by(AIModel.name).all()

@router.post("/", response_model=AIModelOut)
def create_model(model: AIModelCreate, db: Session = Depends(get_db)):
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
    
    update_data = model.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(obj, key, value)
    
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
