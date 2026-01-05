import pytest
from unittest.mock import AsyncMock, patch
from app.services.agent_service import AgentService
from app.models.skill import Skill, SkillType

@pytest.mark.asyncio
async def test_agent_run_hello_world(db_session):
    # 1. Setup Data
    skill = Skill(
        name="hello_world",
        description="Say Hello",
        category="test",
        skill_type=SkillType.PYTHON_FUNC,
        configuration={"folder_path": "tests/mock_skills/hello_world"}, # Mock path, won't be used if we mock execute_skill
        is_active=True
    )
    db_session.add(skill)
    db_session.commit()

    # 2. Mock LLM and Execute
    # We mock call_azure_openai to return a specific JSON decision
    # We mock execute_skill to avoid actual file system running
    
    mock_llm_response = {
        "content": '```json\n{"thought": "User wants a greeting", "tool": "hello_world", "args": {"name": "Tester"}}\n```'
    }

    with patch("app.services.agent_service.call_azure_openai", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = mock_llm_response
        
        with patch("app.services.agent_service.execute_skill") as mock_exec:
            mock_exec.return_value = {"message": "Hello, Tester!"}
            
            service = AgentService(db_session)
            result = await service.run("Say hello to Tester")
            
            # 3. Verify
            assert result["tool_used"] == "hello_world"
            assert result["tool_result"]["message"] == "Hello, Tester!"
            assert "thought" in str(result)

@pytest.mark.asyncio
async def test_agent_no_tool(db_session):
    # Mock LLM returning "none"
    mock_llm_response = {
        "content": '{"thought": "No tool needed", "tool": "none", "args": {}}'
    }

    with patch("app.services.agent_service.call_azure_openai", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = mock_llm_response
        
        service = AgentService(db_session)
        result = await service.run("What is the meaning of life?")
        
        assert "response" in result
        assert "tool_used" not in result or result.get("tool_used") == "none"
