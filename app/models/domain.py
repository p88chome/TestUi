import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import String, Boolean, ForeignKey, JSON, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from app.models.skill import Skill

class EndpointType(str, Enum):
    CLOUD_LLM = "cloud_llm"
    ON_PREM_LLM = "on_prem_llm"
    RULE_ENGINE = "rule_engine"
    ETL_ADAPTER = "etl_adapter"

class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"

class Component(Base):
    __tablename__ = "components"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(String)
    input_schema: Mapped[dict] = mapped_column(JSON)
    output_schema: Mapped[dict] = mapped_column(JSON)
    tags: Mapped[list[str]] = mapped_column(JSON)  # Simple list of strings stored as JSON
    endpoint_type: Mapped[EndpointType] = mapped_column(SQLEnum(EndpointType))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    configuration: Mapped[dict] = mapped_column(JSON, default={})
    
    # New Link to Skill
    skill_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("skills.id"), nullable=True)
    skill = relationship("Skill")

class Workflow(Base):
    __tablename__ = "workflows"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(String)
    # Storing steps as JSONB for v1 MVP as requested
    # Schema: list[dict] where each dict is a WorkflowStep (step_id, component_id, config, input_mapping)
    steps: Mapped[list[dict]] = mapped_column(JSON, default=[])

    runs = relationship("RunExecution", back_populates="workflow")

class RunExecution(Base):
    __tablename__ = "run_executions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workflows.id"))
    status: Mapped[RunStatus] = mapped_column(SQLEnum(RunStatus), default=RunStatus.PENDING)
    input_payload: Mapped[dict] = mapped_column(JSON)
    output_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    log: Mapped[list[dict]] = mapped_column(JSON, default=[]) # List of execution logs per step
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    workflow = relationship("Workflow", back_populates="runs")

class AIModel(Base):
    __tablename__ = "ai_models"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, unique=True, index=True) # e.g., "GPT-4 Production"
    deployment_name: Mapped[str] = mapped_column(String) # e.g., "gpt-4-prod" (Azure Deployment Name)
    api_version: Mapped[str] = mapped_column(String) # e.g., "2023-05-15"
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False) # Can be used to highlight default model
