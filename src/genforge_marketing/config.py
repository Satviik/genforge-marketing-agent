"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings. Secrets are read only from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="GENFORGE_MARKETING_",
        extra="ignore",
    )

    environment: str = "development"
    log_level: str = "INFO"
    data_dir: Path = Path("./data")
    screening_command: str = "genforge"
    screening_workdir: Path | None = None
    screening_timeout_seconds: int = 120
    github_token: str | None = None
    ai_provider: str = "none"
    ai_api_key: str | None = None
    ai_model: str | None = None
    ai_base_url: str = "https://api.openai.com/v1"


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
