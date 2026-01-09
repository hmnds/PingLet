"""Configuration management using Pydantic Settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql://user:pass@localhost/pinglet"

    # X API
    x_api_bearer_token: str = ""

    # OpenAI
    openai_api_key: str = ""

    # Logging
    log_level: str = "INFO"

    # Scheduler settings
    polling_interval_minutes: int = 15
    digest_time: str = "09:00"  # HH:MM format
    timezone: str = "America/New_York"

    # AI Model settings
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4-turbo-preview"

    # Security
    secret_key: str = "your-secret-key-should-be-changed-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


# Global settings instance
settings = Settings()



