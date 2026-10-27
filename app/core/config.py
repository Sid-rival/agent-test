"""Application configuration loaded from environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_name: str = "RAG QA API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Security
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Database
    database_url: str = "sqlite:///./rag_qa.db"

    # Embeddings
    embedding_dim: int = 384
    chunk_size: int = 512
    chunk_overlap: int = 64

    # LLM (pluggable; default is a deterministic extractive summarizer so the
    # service runs end-to-end without external API keys)
    llm_provider: str = "local"

    # Observability
    log_level: str = "INFO"


settings = Settings()