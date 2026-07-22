from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    app_name: str = "CloudCart Sentinel"
    environment: Literal["local", "test", "staging", "production"] = "local"
    log_level: str = "INFO"
    database_url: str = "postgresql+asyncpg://sentinel:sentinel@localhost:5432/sentinel"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = Field(default=30, ge=5, le=1440)
    admin_username: str = "admin"
    admin_password: str = Field(min_length=8)
    cors_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
