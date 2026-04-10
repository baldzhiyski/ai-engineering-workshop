# app/config.py
from __future__ import annotations

from functools import lru_cache
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    app_name: str = "mealprep-agentic"
    app_env: str = "dev"
    log_level: str = "INFO"

    postgres_host: str = "localhost"
    postgres_port: int = 5442
    postgres_db: str = "postgres"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_sslmode: str = "disable"

    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    langsmith_api_key: str | None = None
    langsmith_tracing: bool = True
    langsmith_project: str

    default_model: str
    fast_model: str
    validator_model: str
    coach_model: str

    default_locale: str = "en"
    default_unit_system: str = "metric"
    additional_models: list[str] = ["antropic/claude-2", "gpt-4o"]


    max_recipe_results: int = 8
    default_memory_search_limit: int = 5

    @property
    def db_uri(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            f"?sslmode={self.postgres_sslmode}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()