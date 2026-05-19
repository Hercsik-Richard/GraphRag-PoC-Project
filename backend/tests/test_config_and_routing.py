"""Tests for GraphRAG provider configuration and query routing."""

import asyncio
from pathlib import Path

import pytest

from app.config import Settings, chat_temperature_for_model
from app.services.graphrag import (
    Gemini3TemperatureGuardChatModel,
    GeminiFreeTierRateLimiter,
    GeminiRateLimitError,
    GraphRAGService,
    SourceHit,
)


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


def test_auto_router_selects_source_for_source_bound_extraction() -> None:
    service = GraphRAGService.__new__(GraphRAGService)

    mode, reason = service.route_search_mode(
        "A megadott Wikipedia cikk alapján gyűjtsd össze azokat, akik Albert Einsteinnel vitatkoztak. Csak azokat említsd, akik kifejezetten szerepelnek a szövegben!"
    )

    assert mode == "source"
    assert "source-bound" in reason


def test_manual_search_mode_overrides_auto_router() -> None:
    service = GraphRAGService.__new__(GraphRAGService)

    mode, reason = service.route_search_mode("Summarize the whole dataset", "local")

    assert mode == "local"
    assert "Manual" in reason


def test_manual_source_search_mode_overrides_auto_router() -> None:
    service = GraphRAGService.__new__(GraphRAGService)

    mode, reason = service.route_search_mode("Summarize the whole dataset", "source")

    assert mode == "source"
    assert "Manual" in reason


def test_source_validator_rejects_committee_relationship_false_positive() -> None:
    service = GraphRAGService.__new__(GraphRAGService)
    text = (
        "Einstein was appointed as a German delegate because of the machinations of "
        "Oskar Halecki and Giuseppe Motta. Einstein's former physics professor Hendrik "
        "Lorentz and the Polish chemist Marie Curie were also members of the committee."
    )
    parsed = {
        "collaborators": [
            {
                "person": "Oskar Halecki",
                "topic": "International Committee on Intellectual Cooperation",
                "description": "Einsteinnel bizottsági ügyben szerepelt.",
                "evidence_quote": "Oskar Halecki and Giuseppe Motta",
            }
        ],
        "disputants": [],
    }

    hits = service._validated_source_hits(parsed, text_unit_id="1", text=text)

    assert hits == []


def test_source_validator_rejects_topic_as_person() -> None:
    service = GraphRAGService.__new__(GraphRAGService)
    text = "The Bohr-Einstein debates were public disputes about quantum mechanics."
    parsed = {
        "collaborators": [],
        "disputants": [
            {
                "person": "Kvantummechanika értelmezése",
                "topic": "quantum mechanics",
                "description": "Nem személy, hanem téma.",
                "evidence_quote": "public disputes about quantum mechanics",
            }
        ],
    }

    hits = service._validated_source_hits(parsed, text_unit_id="1", text=text)

    assert hits == []


def test_source_answer_is_formatted_from_validated_hits_only() -> None:
    service = GraphRAGService.__new__(GraphRAGService)
    hits = [
        SourceHit(
            category="collaborator",
            person="Nathan Rosen",
            topic="Einstein-Rosen bridges",
            description="Einstein és Rosen féregjáratmodellt készítettek.",
            evidence_quote="Einstein collaborated with Nathan Rosen to produce a model of a wormhole",
            text_unit_id="tu-1",
        ),
        SourceHit(
            category="disputant",
            person="Niels Bohr",
            topic="quantum mechanics",
            description="Einstein és Bohr a kvantummechanika alapjairól vitatkoztak.",
            evidence_quote="public disputes about quantum mechanics between Einstein and Niels Bohr",
            text_unit_id="tu-2",
        ),
    ]

    answer = service._format_source_bound_answer(hits)

    assert "### Együttműködők" in answer
    assert "Nathan Rosen" in answer
    assert "### Vitatkozó partnerek" in answer
    assert "Niels Bohr" in answer


def test_gemini_provider_requires_api_key() -> None:
    with pytest.raises(ValueError, match="APP_GEMINI_API_KEY"):
        make_settings(query_chat_provider="gemini", gemini_api_key=None)


def test_ollama_index_with_gemini_query_chat_profile() -> None:
    settings = make_settings(
        index_chat_provider="ollama",
        index_embed_provider="ollama",
        query_chat_provider="gemini",
        query_embed_provider="ollama",
        gemini_api_key="test-key",
        gemini_llm_model="gemini-3.1-flash-lite",
    )

    assert settings.get_index_chat_provider() == "ollama"
    assert settings.get_index_embed_provider() == "ollama"
    assert settings.get_query_chat_provider() == "gemini"
    assert settings.get_query_embed_provider() == "ollama"
    assert settings.embedding_config_matches_index() is True


def test_gemini_index_and_query_chat_with_ollama_embeddings_profile() -> None:
    settings = make_settings(
        index_chat_provider="gemini",
        index_embed_provider="ollama",
        query_chat_provider="gemini",
        query_embed_provider="ollama",
        gemini_api_key="test-key",
        gemini_llm_model="gemini-3.1-flash-lite",
    )

    assert settings.get_index_chat_provider() == "gemini"
    assert settings.get_index_embed_provider() == "ollama"
    assert settings.get_query_chat_provider() == "gemini"
    assert settings.get_query_embed_provider() == "ollama"
    assert settings.embedding_config_matches_index() is True


def test_gemini_free_tier_guard_defaults_are_conservative() -> None:
    settings = make_settings(query_chat_provider="gemini", gemini_api_key="test-key")

    assert settings.gemini_free_tier_guard_enabled is True
    assert settings.gemini_free_tier_query_rpm == 7
    assert settings.gemini_free_tier_query_tpm == 120_000
    assert settings.gemini_free_tier_query_rpd == 500
    assert settings.gemini_free_tier_index_rpm == 7
    assert settings.gemini_free_tier_index_tpm == 120_000
    assert settings.gemini_free_tier_index_rpd == 500


def test_gemini_3_temperature_uses_litellm_safe_default() -> None:
    assert chat_temperature_for_model("gemini", "gemini-3.1-flash-lite") == 1.0
    assert chat_temperature_for_model("gemini", "models/gemini-3-pro") == 1.0


def test_non_gemini_3_temperature_remains_deterministic() -> None:
    assert chat_temperature_for_model("gemini", "gemini-2.5-flash-lite") == 0.0
    assert chat_temperature_for_model("ollama", "qwen2.5:3b") == 0.0
    assert chat_temperature_for_model("openrouter", "openai/gpt-4.1-mini") == 0.0


def test_gemini_3_temperature_guard_overrides_low_temperature() -> None:
    class DummyChatModel:
        def __init__(self) -> None:
            self.kwargs: dict[str, object] = {}

        async def achat(self, *args: object, **kwargs: object) -> str:
            self.kwargs = kwargs
            return "ok"

    async def call_guard() -> dict[str, object]:
        wrapped_model = DummyChatModel()
        guarded_model = Gemini3TemperatureGuardChatModel(wrapped_model, 1.0)
        await guarded_model.achat("prompt", temperature=0.0, model_params={"temperature": 0})
        return wrapped_model.kwargs

    kwargs = asyncio.run(call_guard())

    assert kwargs["temperature"] == 1.0
    assert kwargs["model_params"] == {"temperature": 1.0}


def test_gemini_free_tier_limiter_blocks_after_daily_budget(tmp_path: Path) -> None:
    limiter = GeminiFreeTierRateLimiter(
        state_path=tmp_path / "gemini-rate-limit.json",
        requests_per_minute=60,
        tokens_per_minute=10_000,
        requests_per_day=1,
    )

    async def reserve_twice() -> None:
        await limiter.acquire(100)
        with pytest.raises(GeminiRateLimitError, match="napi query limitet"):
            await limiter.acquire(100)

    asyncio.run(reserve_twice())


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
