import sys
import os
import importlib.util
import pytest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def load_skill_module(skill_name):
    """
    Helper to load a skill's run.py module directly.
    """
    skills_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "skills")
    run_path = os.path.join(skills_dir, skill_name, "run.py")
    
    spec = importlib.util.spec_from_file_location("skill_module", run_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_hello_world_skill():
    """
    Test the basic Hello World skill.
    """
    module = load_skill_module("hello_world")
    result = module.execute({})
    # Fixed assertion: "Hello, World!" has a comma
    assert "Hello, World!" in result["message"]

@patch("httpx.Client")
def test_sympy_skill_with_mock(mock_client_cls):
    """
    Test SymPy skill by mocking the Azure OpenAI call.
    """
    module = load_skill_module("sympy")
    
    # Setup Mock
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "```json\n{\"summary\": \"Calcs 1+1\", \"code\": \"print(2)\", \"explanation\": \"Simple math\"}\n```"
                }
            }
        ]
    }
    
    mock_client = mock_client_cls.return_value
    mock_client.__enter__.return_value.post.return_value = mock_response

    # Execute
    input_data = {"query": "1+1"} # Correct key is 'query'
    result = module.execute(input_data)
    
    # Assert
    assert result["summary"] == "Calcs 1+1"
    assert result["code"] == "print(2)"
