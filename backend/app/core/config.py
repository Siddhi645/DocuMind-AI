"""
DocuMind AI — Backend Configuration
Loads and validates all environment variables using pydantic-settings.
"""

from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central configuration for the DocuMind AI backend.
    All values are loaded from environment variables (or .env file).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- Application ----
    app_name: str = "DocuMind AI"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_debug: bool = True
    api_version: str = "v1"
    api_prefix: str = "/api"

    # ---- CORS ----
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    # ---- Database ----
    database_url: str = "postgresql+asyncpg://documind:password@localhost:5432/documind_db"

    # ---- JWT / Auth ----
    jwt_secret: str = "CHANGE_ME_IN_PRODUCTION_USE_A_LONG_RANDOM_SECRET"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    # ---- Pinecone ----
    pinecone_api_key: str = ""
    pinecone_index_name: str = "documind-knowledge"
    pinecone_namespace: str = "documents"   # logical partition within the index
    pinecone_environment: str = ""          # legacy field; not used by SDK v6

    # ---- OpenAI ----
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    # ---- Google ----
    google_api_key: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""

    # ---- n8n ----
    n8n_webhook_url: str = "http://localhost:5678"
    n8n_api_key: str = ""

    # ---- Logging ----
    log_level: str = "INFO"

    @field_validator("app_env")
    @classmethod
    def validate_env(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"app_env must be one of {allowed}")
        return v

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache()
def get_settings() -> Settings:
    """
    Return a cached Settings instance.
    Use FastAPI's Depends(get_settings) to inject config into endpoints.
    """
    return Settings()


# Singleton for direct import convenience
settings = get_settings()
