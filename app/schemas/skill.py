from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.models.skill import SkillType

class SkillBase(BaseModel):
    name: str
    description: str
    category: str
    input_schema: dict = {}
    output_schema: dict = {}
    skill_type: SkillType
    configuration: dict = {}
    is_reusable: bool = True
    is_active: bool = True

class SkillCreate(SkillBase):
    pass

class SkillUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    input_schema: dict | None = None
    output_schema: dict | None = None
    skill_type: SkillType | None = None
    configuration: dict | None = None
    is_reusable: bool | None = None
    is_active: bool | None = None

class SkillOut(SkillBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)
