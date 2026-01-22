from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Database
    database_url: str = "sqlite:///data/fishcatch.db"
    
    # Anthropic API
    anthropic_api_key: str
    
    # SMTP for email-to-SMS
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str
    smtp_password: str
    
    # Authentication
    app_password: str = "fisherman"
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 1 week
    
    # Agent configuration
    agent_model: str = "claude-sonnet-4-5-20250929"
    agent_max_tokens: int = 4096
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
