import os
from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict

class ExecutionMode(str, Enum):
    MOCK = "mock"
    AZURE = "azure"
    ON_PREM = "on_prem"

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Component Platform"
    
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "ai_platform")
    
    # Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-it")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week

    CLIENT_ORIGIN: str = os.getenv("CLIENT_ORIGIN", "http://localhost:5173")
    
    DATABASE_URL: str
    EXECUTION_MODE: ExecutionMode = ExecutionMode.MOCK
    
    AZURE_OPENAI_ENDPOINT: str | None = None
    AZURE_OPENAI_API_KEY: str | None = None # Matches common naming
    AZURE_OPENAI_KEY: str | None = None     # Matches what might be there locally
    
    AZURE_OPENAI_DEPLOYMENT_NAME: str | None = None
    AZURE_OPENAI_API_VERSION: str = "2024-12-01-preview"

    # Azure Computer Vision
    AZURE_VISION_ENDPOINT: str | None = None
    AZURE_VISION_KEY: str | None = None

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

settings = Settings()
