from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class UsageLog(Base):
    __tablename__ = "usage_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    
    # Meta
    app_name: Mapped[str] = mapped_column(String, index=True) # e.g. "Chatbot", "Contract Helper"
    model_name: Mapped[str] = mapped_column(String) # e.g. "gpt-4"
    
    # Token Counts
    tokens_input: Mapped[int] = mapped_column(Integer, default=0)
    tokens_output: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    
    # Cost (Calculated)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0)
    
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
