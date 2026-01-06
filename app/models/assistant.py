from sqlalchemy import Column, String, Text, Table, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid

# Many-to-Many Association Table
assistant_skills = Table(
    "assistant_skills",
    Base.metadata,
    Column("assistant_id", String, ForeignKey("assistants.id"), primary_key=True),
    Column("skill_id", UUID(as_uuid=True), ForeignKey("skills.id"), primary_key=True)
)

class Assistant(Base):
    __tablename__ = "assistants"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    instruction = Column(Text, nullable=True) # System Prompt Override
    avatar = Column(String, nullable=True) # Icon/Image
    
    # Relationships
    skills = relationship("Skill", secondary=assistant_skills, backref="assistants")
