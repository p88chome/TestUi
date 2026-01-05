from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.models.domain import EndpointType, RunStatus

# Component Schemas
class ComponentBase(BaseModel):
    name: str
    description: str
    input_schema: dict
    output_schema: dict
    tags: list[str] = []
    endpoint_type: EndpointType
    active: bool = True

class ComponentCreate(ComponentBase):
    pass

class ComponentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    input_schema: dict | None = None
    output_schema: dict | None = None
    tags: list[str] | None = None
    endpoint_type: EndpointType | None = None
    active: bool | None = None

class ComponentOut(ComponentBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

# Workflow Schemas
class WorkflowStepConfig(BaseModel):
    step_id: int
    component_id: UUID
    config: dict
    input_mapping: dict
    # New: Dynamic Logic
    next_step_id: int | None = None # Explicit next step (overrides default sequence)
    condition: dict | None = None # e.g. {"field": "status", "operator": "==", "value": "check"}

class WorkflowBase(BaseModel):
    name: str
    description: str
    steps: list[WorkflowStepConfig]

class WorkflowCreate(WorkflowBase):
    pass

class WorkflowUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    steps: list[WorkflowStepConfig] | None = None

class WorkflowOut(WorkflowBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

# Run Schemas
class RunExecutionBase(BaseModel):
    workflow_id: UUID
    input_payload: dict
    task_package_id: UUID | None = None # Optional context

class RunExecutionCreate(RunExecutionBase):
    pass

class RunExecutionOut(RunExecutionBase):
    id: UUID
    status: RunStatus
    output_payload: dict | None
    log: list[dict]
    started_at: datetime
    finished_at: datetime | None
    model_config = ConfigDict(from_attributes=True)
