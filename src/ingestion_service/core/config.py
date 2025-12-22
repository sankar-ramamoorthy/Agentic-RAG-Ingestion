# src/ingestion_service/core/config.py

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Return cached application settings.

    Environment variables and .env are read once.
    Pyright is satisfied because Settings() is not
    treated as a raw constructor call everywhere.
    """
    return Settings()  # type: ignore[reportCallIssue]
