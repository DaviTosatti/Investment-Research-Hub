from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="HUB_", env_file=".env", extra="ignore")
    database_url: str = "postgresql+psycopg://hub:local-development-only@127.0.0.1:5432/hub"
    public_origin: str = "http://localhost:3000"
    cookie_secure: bool = False
    session_hours: int = Field(default=12, ge=1, le=72)


@lru_cache
def get_settings() -> Settings:
    return Settings()
