import pytest
import sys
import os

# Ensure app module is found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.skill import Skill
from app.models.skill import SkillType
import os

# Use a test database or SQLite in-memory
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """
    Creates a fresh database session for a test.
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def mock_skill(db_session):
    """
    Creates a mock skill for testing.
    """
    skill = Skill(
        name="test_skill",
        description="A skill for testing",
        category="test",
        skill_type=SkillType.PYTHON_FUNC,
        configuration={"folder_path": "tests/mock_skills/test_skill"},
        is_active=True
    )
    db_session.add(skill)
    db_session.commit()
    return skill
