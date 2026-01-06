from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    tenant_id = Column(String, index=True, default="default") # Multi-tenancy support
    
    # Subscription Plan
    plan_name = Column(String, default="Starter")
    # chat_histories = relationship("ChatHistory", back_populates="user")
    
    # New relationships
    feedbacks = relationship("Feedback", back_populates="user")
    plan_expiry = Column(String, nullable=True) # ISO Date String
