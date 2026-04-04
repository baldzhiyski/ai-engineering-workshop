from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")

    openai_chat_model: str = Field(
        default="gpt-5.4-mini",
        alias="OPENAI_CHAT_MODEL",
    )
    openai_reasoning_model: str = Field(
        default="gpt-5.2",
        alias="OPENAI_REASONING_MODEL",
    )
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        alias="OPENAI_EMBEDDING_MODEL",
    )

    database_url: str = Field(
        default="sqlite:///./data/db/app.db",
        alias="DATABASE_URL",
    )

    docs_dir: str = Field(default="./data/docs", alias="DOCS_DIR")
    uploads_dir: str = Field(default="./data/uploads", alias="UPLOADS_DIR")
    vectorstore_dir: str = Field(default="./data/vectorstore", alias="VECTORSTORE_DIR")

    langsmith_api_key: str | None = Field(default=None, alias="LANGSMITH_API_KEY")
    langsmith_tracing: bool = Field(default=True, alias="LANGSMITH_TRACING")
    langsmith_project: str = Field(
        default="langchain-agentic-platform",
        alias="LANGSMITH_PROJECT",
    )

    app_name: str = "LangChain Agentic Platform"
    debug: bool = Field(default=True, alias="DEBUG")
    max_retries: int = Field(default=1, alias="MAX_RETRIES")
    default_retrieval_k: int = Field(default=5, alias="DEFAULT_RETRIEVAL_K")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()