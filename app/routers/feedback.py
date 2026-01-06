from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.api import deps
from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate, FeedbackOut

router = APIRouter()

@router.post("/feedback", response_model=FeedbackOut)
def create_feedback(
    feedback_in: FeedbackCreate, 
    db: Session = Depends(get_db), 
    current_user = Depends(deps.get_current_user)
):
    db_feedback = Feedback(user_id=current_user.id, content=feedback_in.content)
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

@router.get("/feedback", response_model=list[FeedbackOut])
def get_feedbacks(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user = Depends(deps.get_current_active_superuser)
):
    return db.query(Feedback).options(joinedload(Feedback.user)).offset(skip).limit(limit).all()

@router.delete("/feedback/{feedback_id}", status_code=204)
def delete_feedback(
    feedback_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(deps.get_current_active_superuser)
):
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    db.delete(feedback)
    db.commit()
    return None
