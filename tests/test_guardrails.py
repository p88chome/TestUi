import sys
import os
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.services.skill_loader import execute_skill
from app.models.skill import Skill

@patch("app.services.skill_loader.importlib.util")
def test_execute_skill_returns_structured_error_on_exception(mock_importlib):
    """
    Test that execute_skill catches exceptions and returns the standard error JSON.
    """
    # Setup Mocks
    mock_db = MagicMock(spec=Session)
    
    # Mock Skill Object
    mock_skill = MagicMock(spec=Skill)
    mock_skill.name = "failing_skill"
    mock_skill.is_active = True
    mock_skill.configuration = {"folder_path": "/tmp/fake"}
    
    mock_db.query.return_value.filter.return_value.first.return_value = mock_skill
    
    # Mock Module Execution to Raise Exception
    mock_spec = MagicMock()
    mock_module = MagicMock()
    # When module.execute() is called, raise an error
    mock_module.execute.side_effect = Exception("Such failure!")
    
    mock_importlib.spec_from_file_location.return_value = mock_spec
    mock_importlib.module_from_spec.return_value = mock_module
    
    # Mock os.path.exists to pass validation
    with patch("os.path.exists", return_value=True):
        input_data = {}
        result = execute_skill("failing_skill", input_data, mock_db, trace_id="test-trace")
        
    print(f"DEBUG Result: {result}")
    
    # Assertions
    assert result["status"] == "error"
    assert result["error_code"] == "SKILL_EXECUTION_FAILED"
    assert "Such failure!" in result["message"]
    assert result["details"]["trace_id"] == "test-trace"
    
    # Verify DB Logging Attempted
    # execute_skill logic: Add Execution -> Commit -> (Exec) -> Add Execution (Update) -> Commit
    assert mock_db.commit.call_count >= 1
