"""Application configuration using Pydantic Settings."""

import json
from typing import Any, Literal

from pydantic import PostgresDsn, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables with APP_ prefix."""

    database_url: PostgresDsn

    # Model provider configuration
    # "ollama" for local inference, "gemini" for Google Gemini API
    # Same provider is used for both indexing and querying to ensure embedding compatibility
    model_provider: Literal["ollama", "gemini"] = "ollama"

    # Ollama configuration (required when model_provider is "ollama")
    ollama_base_url: str | None = None
    ollama_llm_model: str = "qwen2.5:3b"
    ollama_embed_model: str = "nomic-embed-text"

    # Gemini configuration (required when model_provider or index_model_provider is "gemini")
    gemini_api_key: str | None = None
    gemini_llm_model: str = "gemini-2.5-flash-lite"
    gemini_embed_model: str = "gemini-embedding-001"

    # GraphRAG indexing controls. Gemini indexing is many sequential LLM calls, so
    # these defaults favor reliability over speed.
    graphrag_concurrent_requests: int = 1
    graphrag_max_retries: int = 8
    graphrag_max_retry_wait: float = 60.0
    graphrag_index_timeout_seconds: int = 7200
    graphrag_request_timeout: float = 600.0
    graphrag_chunk_size: int = 1600
    graphrag_chunk_overlap: int = 100
    graphrag_claim_extraction_enabled: bool = False

    graphrag_root: str
    cors_origins: list[str]
    debug: bool = False

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env.local",
        env_file_encoding="utf-8",
        extra="forbid",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        """Parse CORS origins from JSON string or list."""
        if isinstance(v, str):
            return json.loads(v)
        return v

    @model_validator(mode="after")
    def validate_provider_configuration(self) -> "Settings":
        """Validate that required settings are present for the configured provider."""
        # Validate Ollama configuration
        if self.model_provider == "ollama":
            if not self.ollama_base_url:
                raise ValueError("APP_OLLAMA_BASE_URL is required when model_provider is 'ollama'")

        # Validate Gemini configuration
        if self.model_provider == "gemini":
            if not self.gemini_api_key:
                raise ValueError("APP_GEMINI_API_KEY is required when model_provider is 'gemini'")

        return self

    def get_index_provider(self) -> Literal["ollama", "gemini"]:
        """Get the provider to use for indexing."""
        return self.model_provider

    def get_query_provider(self) -> Literal["ollama", "gemini"]:
        """Get the provider to use for querying."""
        return self.model_provider


settings = Settings()  # type: ignore
