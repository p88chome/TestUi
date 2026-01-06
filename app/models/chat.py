import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assistant_id = Column(String, ForeignKey("assistants.id"), nullable=True) # Link to specific bot
    title = Column(String, nullable=True)
    tenant_id = Column(String, index=True, default="default")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    trace_id = Column(String, index=True, nullable=True) # Full request trace ID
    tenant_id = Column(String, index=True, default="default")
    role = Column(String, nullable=False) # user, assistant, system, tool
    content = Column(Text, nullable=True)
    tool_calls = Column(JSON, nullable=True) # For storing tool call details
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    session = relationship("ChatSession", back_populates="messages")
