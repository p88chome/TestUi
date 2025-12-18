from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import Component
from app.schemas.all import ComponentCreate, ComponentOut, ComponentUpdate

router = APIRouter(prefix="/components", tags=["components"])

@router.get("/", response_model=list[ComponentOut])
def list_components(tag: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Component).filter(Component.active == True)
    if tag:
        # Simple JSON search. Ideally use Postgres array operators like @> but JSON is generic
        # For sqlite/mock usage it's harder, but here we assume Postgres.
        # However, to be safe and simple for MVP without specific PG operators in python:
        # We will filter in python if the dataset is small, or use simple string check if structure allows.
        # Correct way for JSONB list of strings:
        # query = query.filter(Component.tags.op("@>")(cast([tag], JSONB)))
        # For now, let's just return all and filter in python for MVP simplicity or implement exact tag match later
        pass
    
    components = query.all()
    if tag:
        components = [c for c in components if tag in c.tags]
    return components

@router.post("/", response_model=ComponentOut)
def create_component(component: ComponentCreate, db: Session = Depends(get_db)):
    db_obj = Component(**component.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/{component_id}", response_model=ComponentOut)
def get_component(component_id: UUID, db: Session = Depends(get_db)):
    obj = db.query(Component).filter(Component.id == component_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Component not found")
    return obj

@router.put("/{component_id}", response_model=ComponentOut)
def update_component(component_id: UUID, component: ComponentUpdate, db: Session = Depends(get_db)):
    obj = db.query(Component).filter(Component.id == component_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Component not found")
    
    update_data = component.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(obj, key, value)
    
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{component_id}")
def delete_component(component_id: UUID, db: Session = Depends(get_db)):
    obj = db.query(Component).filter(Component.id == component_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Component not found")
    
    obj.active = False # Soft delete
    db.add(obj)
    db.commit()
    return {"ok": True}
