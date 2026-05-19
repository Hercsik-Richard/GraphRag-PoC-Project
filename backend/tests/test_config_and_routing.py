"""Tests for GraphRAG provider configuration and query routing."""

import pytest

from app.config import Settings
from app.services.graphrag import GraphRAGService


def make_settings(**overrides: object) -> Settings:
    """Create settings with the required non-provider fields."""
    values = {
        "database_url": "postgresql://user:pass@localhost:5432/db",
        "ollama_base_url": "http://localhost:11434",
        "graphrag_root": "/tmp/graphrag-test",
        "cors_origins": ["http://localhost:3000"],
    }
    values.update(overrides)
    return Settings(**values)


def test_auto_router_selects_global_for_overview_query() -> None:
    service = GraphRAGService.__new__(GraphRAGService)

    mode, reason = service.route_search_mode("Give me an overview of the whole dataset")

    assert mode == "global"
    assert "global" in reason


def test_auto_router_selects_drift_for_relationship_query() -> None:
    service = GraphRAGService.__new__(GraphRAGService)

    mode, reason = service.route_search_mode("How are Zeus and Hera related?")

    assert mode == "drift"
    assert "DRIFT" in reason


def test_auto_router_keeps_source_bound_extraction_local() -> None:
    service = GraphRAGService.__new__(GraphRAGService)

    mode, reason = service.route_search_mode(
        "A megadott Wikipedia cikk alapján gyűjtsd össze azokat, akik Albert Einsteinnel vitatkoztak. Csak azokat említsd, akik kifejezetten szerepelnek a szövegben!"
    )

    assert mode == "local"
    assert "source-bound" in reason


def test_manual_search_mode_overrides_auto_router() -> None:
    service = GraphRAGService.__new__(GraphRAGService)

    mode, reason = service.route_search_mode("Summarize the whole dataset", "local")

    assert mode == "local"
    assert "Manual" in reason


def test_gemini_provider_requires_api_key() -> None:
    with pytest.raises(ValueError, match="APP_GEMINI_API_KEY"):
        make_settings(query_chat_provider="gemini", gemini_api_key=None)


def test_openrouter_provider_requires_api_key() -> None:
    with pytest.raises(ValueError, match="APP_OPENROUTER_API_KEY"):
        make_settings(query_chat_provider="openrouter", openrouter_api_key=None)


def test_embedding_mismatch_is_detected() -> None:
    settings = make_settings(
        index_embed_provider="ollama",
        query_embed_provider="gemini",
        gemini_api_key="test-key",
    )

    assert settings.embedding_config_matches_index() is False
