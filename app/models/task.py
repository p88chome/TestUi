import uuid
from sqlalchemy import String, Boolean, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class TaskPackage(Base):
    __tablename__ = "task_packages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    description: Mapped[str] = mapped_column(String)
    
    # Business Context
    department: Mapped[str] = mapped_column(String, index=True) # e.g., "legal", "finance"
    
    # The Core "Manual"
    manual_content: Mapped[str] = mapped_column(String, nullable=True) # The SOP/Text injected into context
    
    # Execution Definition
    # For now, a TaskPackage wraps a Workflow (sequence of skills)
    workflow_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("workflows.id"), nullable=True)
    workflow = relationship("app.models.domain.Workflow")
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
