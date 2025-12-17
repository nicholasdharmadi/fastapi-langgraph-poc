"""Application configuration."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/langgraph_poc"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # OpenAI
    OPENAI_API_KEY: str
    
    # LangSmith (Optional)
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "fastapi-langgraph-poc"
    
    # SMS Service
    SMS_PROVIDER: str = "twilio"  # mock, twilio
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    # Working Hours Configuration
    ENFORCE_WORKING_HOURS: bool = True
    WORKING_HOURS_START: int = 9  # 9 AM
    WORKING_HOURS_END: int = 23  # 11 PM (23:00)
    ALLOW_WEEKEND_SENDING: bool = True
    
    # App Settings
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

