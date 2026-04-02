import asyncio
import sys
import os
from unittest.mock import MagicMock, AsyncMock, patch

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.llm_service import call_llm, call_llm_sync
from app.models.domain import AIModel, LLMProvider

async def test_call_llm_google():
    db = MagicMock()
    mock_model = AIModel(
        id="123",
        name="Gemini Test",
        provider=LLMProvider.GOOGLE,
        model_name="gemini-1.5-flash"
    )
    db.query().filter().first.return_value = mock_model
    
    expected_resp = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": "Hello from Gemini!"}]
                }
            }
        ]
    }
    
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=200, json=lambda: expected_resp)
        
        result = await call_llm(db, input_text="Hi")
        print("Gemini Async Result:", result['choices'][0]['message']['content'])
        assert result['choices'][0]['message']['content'] == "Hello from Gemini!"

def test_call_llm_sync_azure():
    db = MagicMock()
    mock_model = AIModel(
        id="456",
        name="Azure Test",
        provider=LLMProvider.AZURE,
        deployment_name="gpt-4",
        api_version="2023-05-15"
    )
    db.query().filter().first.return_value = mock_model
    
    expected_resp = {
        "choices": [
            {
                "message": {"role": "assistant", "content": "Hello from Azure!"}
            }
        ]
    }
    
    with patch("httpx.Client.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=200, json=lambda: expected_resp)
        
        result = call_llm_sync(db, input_text="Hi")
        print("Azure Sync Result:", result['choices'][0]['message']['content'])
        assert result['choices'][0]['message']['content'] == "Hello from Azure!"

if __name__ == "__main__":
    from app.core.config import settings
    settings.GEMINI_API_KEY = "test-key"
    settings.AZURE_OPENAI_API_KEY = "test-key"
    settings.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com/"
    
    print("Running Tests...")
    asyncio.run(test_call_llm_google())
    test_call_llm_sync_azure()
    print("Tests Passed!")
