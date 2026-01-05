from app.services.skill_loader import execute_skill
from app.models.skill import Skill, SkillType
from app.core.database import SessionLocal
import pytest
import os
import json

def test_hello_world_skill(db_session):
    # 1. Register Skill
    skill_dir = os.path.join(os.getcwd(), "app", "skills", "hello_world")
    skill = Skill(
        name="hello_world",
        description="Test Skill",
        category="test",
        skill_type=SkillType.PYTHON_FUNC,
        configuration={"folder_path": skill_dir},
        is_active=True
    )
    db_session.add(skill)
    db_session.commit()

    # 2. Execute
    input_data = {"name": "TestUser"}
    result = execute_skill("hello_world", input_data, db_session)

    # 3. Assert
    assert result["status"] == "success"
    assert result["message"] == "Hello, TestUser!"

def test_missing_skill(db_session):
    with pytest.raises(ValueError) as excinfo:
        execute_skill("non_existent_skill", {}, db_session)
    assert "not found" in str(excinfo.value)
