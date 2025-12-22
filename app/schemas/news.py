from pydantic import BaseModel
from datetime import datetime

class NewsBase(BaseModel):
    title: str
    content: str
    is_published: bool = True

class NewsCreate(NewsBase):
    pass

class NewsOut(NewsBase):
    id: int
    author_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
