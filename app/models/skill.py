import uuid
from enum import Enum
from sqlalchemy import String, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class SkillType(str, Enum):
    LLM_PROMPT = "llm_prompt"   # Uses an LLM with a specific prompt
    PYTHON_FUNC = "python_func" # Executes a registered local Python function
    API_CALL = "api_call"       # Makes a generic API call
    RULE_ENGINE = "rule_engine" # Simple conditional logic

class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    description: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String, index=True) # e.g., "communication", "data_processing"
    
    # Schema Definition
    input_schema: Mapped[dict] = mapped_column(JSON, default={})
    output_schema: Mapped[dict] = mapped_column(JSON, default={})
    
    # Implementation Details
    skill_type: Mapped[SkillType] = mapped_column(SQLEnum(SkillType))
    configuration: Mapped[dict] = mapped_column(JSON, default={}) 
    # config examples:
    # LLM_PROMPT: {"system_template": "...", "model_name": "gpt-4"}
    # PYTHON_FUNC: {"module": "app.skills.common", "function": "send_email"}
    # API_CALL: {"url": "...", "method": "POST"}

    is_reusable: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class SkillExecution(Base):
    __tablename__ = "skill_executions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trace_id: Mapped[str] = mapped_column(String, index=True, nullable=True) # Full request trace ID
    skill_name: Mapped[str] = mapped_column(String, index=True)
    tenant_id: Mapped[str] = mapped_column(String, index=True, default="default")
    input_data: Mapped[dict] = mapped_column(JSON)
    output_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String, default="PENDING") # PENDING, SUCCESS, ERROR
    logs: Mapped[str] = mapped_column(String, nullable=True)
    from sqlalchemy import Integer
    execution_time_ms: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # Ideally link to User but for now optional
    # user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    from sqlalchemy import DateTime, func
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

