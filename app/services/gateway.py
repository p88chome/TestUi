from sqlalchemy.orm import Session
from app.services.azure_integration import call_azure_openai

class LLMGateway:
    """
    Central Gateway for AI Model interactions.
    Currently delegates to Azure OpenAI, but designed to support multiple providers (Local, Anthropic, etc.) in the future.
    """
    def __init__(self, db: Session):
        self.db = db

    async def chat(self, messages: list[dict], temperature: float = 0.7, model_id: str = None) -> dict:
        """
        Unified Chat Interface.
        
        Args:
            messages: List of message dicts [{"role": "user", "content": "..."}]
            temperature: Randomness (0.0 to 1.0)
            model_id: Optional ID to select specific model config from DB
            
        Returns:
            Dict containing 'choices', 'usage', etc. (Standard OpenAI format)
        """
        # In the future, logic here can check:
        # if settings.AI_PROVIDER == "ollama": return await call_ollama(...)
        
        return await call_azure_openai(
            db=self.db,
            input_text="", # Legacy param, ignored by call_azure_openai when messages is provided
            messages=messages,
            model_id=model_id,
            temperature=temperature
        )
