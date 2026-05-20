"""Application configuration using Pydantic Settings."""

import json
from typing import Any, Literal, cast

from pydantic import PostgresDsn, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ModelProvider = Literal["ollama", "gemini", "openrouter"]


def is_gemini_3_model(provider: ModelProvider, model: str) -> bool:
    """Return whether a chat model is from the Gemini 3 family."""
    normalized_model = model.casefold().removeprefix("models/")
    return provider == "gemini" and normalized_model.startswith("gemini-3")


def chat_temperature_for_model(provider: ModelProvider, model: str) -> float:
    """Return a LiteLLM-safe chat temperature for the selected provider/model."""
    if is_gemini_3_model(provider, model):
        return 1.0
    return 0.0


class Settings(BaseSettings):
    """Application settings loaded from environment variables with APP_ prefix."""

    database_url: PostgresDsn

    # Model provider configuration. The split provider fields are preferred; model_provider and
    # index_model_provider are accepted as backward-compatible defaults.
    model_provider: ModelProvider | None = None
    index_model_provider: ModelProvider | None = None
    index_chat_provider: ModelProvider | None = None
    index_embed_provider: ModelProvider | None = None
    query_chat_provider: ModelProvider | None = None
    query_embed_provider: ModelProvider | None = None

    # Ollama configuration (required when model_provider is "ollama")
    ollama_base_url: str | None = None
    ollama_llm_model: str = "qwen2.5:3b"
    ollama_embed_model: str = "nomic-embed-text"

    # Gemini configuration (required when model_provider or index_model_provider is "gemini")
    gemini_api_key: str | None = None
    gemini_llm_model: str = "gemini-3.1-flash-lite"
    gemini_embed_model: str = "gemini-embedding-001"
    gemini_free_tier_guard_enabled: bool = True
    gemini_free_tier_query_rpm: int = 7
    gemini_free_tier_query_tpm: int = 120_000
    gemini_free_tier_query_rpd: int = 500
    gemini_free_tier_index_guard_enabled: bool = True
    gemini_free_tier_index_rpm: int = 7
    gemini_free_tier_index_tpm: int = 120_000
    gemini_free_tier_index_rpd: int = 500

    # OpenRouter configuration. Embeddings require a model that OpenRouter exposes through
    # /embeddings; otherwise use Ollama or Gemini for embeddings.
    openrouter_api_key: str | None = None
    openrouter_llm_model: str = "openai/gpt-4.1-mini"
    openrouter_embed_model: str = ""
    openrouter_api_base: str = "https://openrouter.ai/api/v1"

    # GraphRAG indexing controls. Gemini indexing is many sequential LLM calls, so
    # these defaults favor reliability over speed.
    graphrag_concurrent_requests: int = 1
    graphrag_max_retries: int = 8
    graphrag_max_retry_wait: float = 60.0
    graphrag_index_timeout_seconds: int = 7200
    graphrag_request_timeout: float = 600.0
    graphrag_query_timeout_seconds: int = 240
    graphrag_chunk_size: int = 1000
    graphrag_chunk_overlap: int = 150
    graphrag_claim_extraction_enabled: bool = False
    graphrag_clean_output_on_index: bool = True
    graphrag_replace_corpus_on_upload: bool = True

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

    @field_validator(
        "model_provider",
        "index_model_provider",
        "index_chat_provider",
        "index_embed_provider",
        "query_chat_provider",
        "query_embed_provider",
        mode="before",
    )
    @classmethod
    def parse_optional_provider(cls, v: Any) -> Any:
        """Treat empty provider env vars from docker compose as unset."""
        if v == "":
            return None
        return v

    @model_validator(mode="after")
    def validate_provider_configuration(self) -> "Settings":
        """Validate that required settings are present for the configured provider."""
        default_provider = self.model_provider or "ollama"
        self.index_chat_provider = self.index_chat_provider or self.index_model_provider or default_provider
        self.index_embed_provider = self.index_embed_provider or self.index_model_provider or default_provider
        self.query_chat_provider = self.query_chat_provider or default_provider
        self.query_embed_provider = self.query_embed_provider or self.index_embed_provider

        configured_providers = {
            self.index_chat_provider,
            self.index_embed_provider,
            self.query_chat_provider,
            self.query_embed_provider,
        }

        # Validate Ollama configuration
        if "ollama" in configured_providers:
            if not self.ollama_base_url:
                raise ValueError("APP_OLLAMA_BASE_URL is required when any provider is 'ollama'")

        # Validate Gemini configuration
        if "gemini" in configured_providers:
            if not self.gemini_api_key:
                raise ValueError("APP_GEMINI_API_KEY is required when any provider is 'gemini'")

        # Validate OpenRouter configuration
        if "openrouter" in configured_providers:
            if not self.openrouter_api_key:
                raise ValueError(
                    "APP_OPENROUTER_API_KEY is required when any provider is 'openrouter'"
                )
            if "openrouter" in {self.index_chat_provider, self.query_chat_provider}:
                if not self.openrouter_llm_model:
                    raise ValueError("APP_OPENROUTER_LLM_MODEL is required for OpenRouter chat")
            if "openrouter" in {self.index_embed_provider, self.query_embed_provider}:
                if not self.openrouter_embed_model:
                    raise ValueError("APP_OPENROUTER_EMBED_MODEL is required for OpenRouter embeddings")

        return self

    def get_index_provider(self) -> ModelProvider:
        """Get the chat provider to use for indexing."""
        return self.get_index_chat_provider()

    def get_query_provider(self) -> ModelProvider:
        """Get the chat provider to use for querying."""
        return self.get_query_chat_provider()

    def get_index_chat_provider(self) -> ModelProvider:
        """Get the chat provider to use for indexing."""
        return cast(ModelProvider, self.index_chat_provider)

    def get_index_embed_provider(self) -> ModelProvider:
        """Get the embedding provider to use for indexing."""
        return cast(ModelProvider, self.index_embed_provider)

    def get_query_chat_provider(self) -> ModelProvider:
        """Get the chat provider to use for querying."""
        return cast(ModelProvider, self.query_chat_provider)

    def get_query_embed_provider(self) -> ModelProvider:
        """Get the embedding provider to use for querying."""
        return cast(ModelProvider, self.query_embed_provider)

    def get_model_name(self, provider: ModelProvider, model_kind: Literal["chat", "embedding"]) -> str:
        """Return the configured model name for a provider and model kind."""
        if provider == "ollama":
            return self.ollama_llm_model if model_kind == "chat" else self.ollama_embed_model
        if provider == "gemini":
            return self.gemini_llm_model if model_kind == "chat" else self.gemini_embed_model
        return self.openrouter_llm_model if model_kind == "chat" else self.openrouter_embed_model

    def get_active_provider_roles(
        self,
    ) -> dict[str, tuple[ModelProvider, Literal["chat", "embedding"]]]:
        """Return only providers actively configured for index/query roles."""
        return {
            "index_chat": (self.get_index_chat_provider(), "chat"),
            "index_embedding": (self.get_index_embed_provider(), "embedding"),
            "query_chat": (self.get_query_chat_provider(), "chat"),
            "query_embedding": (self.get_query_embed_provider(), "embedding"),
        }

    def embedding_config_matches_index(self) -> bool:
        """Return whether query embeddings match the embedding model used for indexing."""
        return (
            self.get_query_embed_provider() == self.get_index_embed_provider()
            and self.get_model_name(self.get_query_embed_provider(), "embedding")
            == self.get_model_name(self.get_index_embed_provider(), "embedding")
        )


settings = Settings()  # type: ignore
