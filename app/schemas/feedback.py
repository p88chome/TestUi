from pydantic import BaseModel
from datetime import datetime

class FeedbackCreate(BaseModel):
    content: str

class FeedbackOut(BaseModel):
    id: int
    user_id: int
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True
