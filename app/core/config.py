import os
import warnings
from enum import Enum
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator

class ExecutionMode(str, Enum):
    MOCK = "mock"
    AZURE = "azure"
    ON_PREM = "on_prem"

class EmailProvider(str, Enum):
    SMTP = "smtp"
    AZURE_ACS = "azure_acs"
    NONE = "none"  # Disable email (dev/test mode)

# Default key for development only
_DEFAULT_SECRET_KEY = "your-super-secret-key-change-it"

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Component Platform"
    
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "ai_platform")
    
    # Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", _DEFAULT_SECRET_KEY)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week
    
    @model_validator(mode='after')
    def validate_secret_key(self) -> 'Settings':
        """Warn if using default SECRET_KEY (insecure for production)"""
        if self.SECRET_KEY == _DEFAULT_SECRET_KEY:
            warnings.warn(
                "\n⚠️  WARNING: Using default SECRET_KEY! "
                "This is insecure for production.\n"
                "Generate a secure key: python -c \"import secrets; print(secrets.token_urlsafe(64))\"\n"
                "Then set it in your .env file: SECRET_KEY=<your-secure-key>",
                UserWarning,
                stacklevel=2
            )
        return self

    # Environment: "development" or "production"
    ENV: str = os.getenv("ENV", "development")
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

    # ── Email Service ──────────────────────────────────────────────────────
    # Set EMAIL_PROVIDER to "smtp", "azure_acs", or "none" (disable)
    EMAIL_PROVIDER: EmailProvider = EmailProvider.NONE

    # SMTP (Gmail / Outlook / company SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "no-reply@example.com"
    EMAIL_FROM_NAME: str = "AI Platform"

    # Azure Communication Services Email
    ACS_CONNECTION_STRING: Optional[str] = None
    ACS_SENDER_ADDRESS: Optional[str] = None
    # ───────────────────────────────────────────────────────────────────────

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

settings = Settings()
