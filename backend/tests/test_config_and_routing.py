"""Tests for GraphRAG provider configuration and query routing."""

import asyncio
import json
import re
from pathlib import Path

import pytest

from app.config import Settings, chat_temperature_for_model
from app.schemas.chat import MessageSchema, QueryRequestSchema
from app.services.graphrag import (
    Gemini3TemperatureGuardChatModel,
    GeminiFreeTierRateLimiter,
    GeminiRateLimitError,
    GraphRAGService,
    SourceHit,
)

BACKEND_ROOT = Path(__file__).resolve().parents[1]


def find_project_root() -> Path:
    """Find repo root in both local backend and Docker test layouts."""
    candidates = [
        Path(__file__).resolve().parents[2],
        Path.cwd(),
        Path.cwd().parent,
    ]
    for candidate in candidates:
        if (candidate / "docker-compose.yml").exists():
            return candidate
    return Path(__file__).resolve().parents[2]


PROJECT_ROOT = find_project_root()


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


def test_auto_router_selects_source_for_direct_storage_fact_lookup() -> None:
    service = GraphRAGService.__new__(GraphRAGService)

    mode, reason = service.route_search_mode(
        "Which system stores extracted entities and relationships?"
    )

    assert mode == "source"
    assert "direct source fact" in reason


def test_auto_router_selects_hybrid_for_source_bound_analysis() -> None:
    service = GraphRAGService.__new__(GraphRAGService)

    mode, reason = service.route_search_mode(
        "Answer strictly and exclusively from the indexed Albert Einstein Wikipedia article. "
        "Write a concise analytical answer explaining how the turning points in Albert "
        "Einstein's life, scientific achievements, and political decisions are connected."
    )

    assert mode == "hybrid"
    assert "hybrid" in reason


def test_auto_hybrid_falls_back_to_source_when_query_embeddings_are_unavailable() -> None:
    service = GraphRAGService.__new__(GraphRAGService)
    service.query_embed_provider = "ollama"
    service._load_indexed_data_objects = lambda: None  # type: ignore[method-assign]

    async def unavailable_detail(mode: str) -> str | None:
        assert mode == "hybrid"
        return "a query embedding provider nem elérhető"

    async def source_search(question: str) -> dict[str, object]:
        assert "indexed Albert Einstein Wikipedia article" in question
        return {
            "answer": "source answer",
            "retrieved_entities": [],
            "retrieved_relationships": [],
            "retrieved_sources": [],
        }

    service._query_embedding_unavailable_detail = unavailable_detail  # type: ignore[method-assign]
    service._execute_source_bound_search = source_search  # type: ignore[method-assign]

    result = asyncio.run(
        service._query_with_active_provider(
            "Answer strictly and exclusively from the indexed Albert Einstein Wikipedia article. "
            "Write a concise analytical answer explaining how the turning points in Albert "
            "Einstein's life, scientific achievements, and political decisions are connected.",
            search_mode="auto",
        )
    )

    assert result["answer"] == "source answer"
    assert result["search_mode_used"] == "source"
    assert "Source fallback" in result["search_mode_reason"]


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


def test_manual_hybrid_search_mode_overrides_auto_router() -> None:
    service = GraphRAGService.__new__(GraphRAGService)

    mode, reason = service.route_search_mode("Summarize the whole dataset", "hybrid")

    assert mode == "hybrid"
    assert "Manual" in reason


def test_hybrid_query_schema_is_valid() -> None:
    request = QueryRequestSchema(question="Explain from the indexed source", search_mode="hybrid")

    assert request.search_mode == "hybrid"


def test_message_schema_accepts_missing_retrieved_sources() -> None:
    message = MessageSchema(
        id="11111111-1111-1111-1111-111111111111",
        conversation_id="22222222-2222-2222-2222-222222222222",
        role="assistant",
        content="ok",
        created_at="2026-05-20T12:00:00",
    )

    assert message.retrieved_sources is None


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


def test_source_evidence_ranking_prioritizes_query_terms() -> None:
    service = GraphRAGService.__new__(GraphRAGService)
    service._document_source_labels_cache = {}
    service._load_text_unit_records = lambda: [  # type: ignore[method-assign]
        {
            "id": "a",
            "text": "Einstein played violin and discussed general cultural interests in Europe.",
        },
        {
            "id": "b",
            "text": "In 1939, Leo Szilard drafted a letter that Einstein signed and sent to President Franklin D. Roosevelt about uranium and nuclear weapons.",
        },
    ]

    evidence = service._rank_source_evidence("What does the source say about the 1939 Roosevelt letter?", limit=2)

    assert evidence[0].text_unit_id == "b"
    assert evidence[0].id == "S1"


def test_direct_storage_fact_lookup_answers_without_model_call() -> None:
    service = GraphRAGService.__new__(GraphRAGService)
    service._document_source_labels_cache = {}
    service._load_text_unit_records = lambda: [  # type: ignore[method-assign]
        {
            "id": "tu-storage",
            "text": (
                "Orion Assistant uses AtlasGraph to organize entities found during indexing. "
                "AtlasGraph stores extracted entities and relationships for the GraphRAG workspace."
            ),
        }
    ]

    result = service._execute_direct_source_fact_search(
        "Which system stores extracted entities and relationships?"
    )

    assert result is not None
    assert "AtlasGraph" in result["answer"]
    assert result["retrieved_sources"]
    assert result["retrieved_entities"][0]["title"] == "AtlasGraph"


def test_source_label_does_not_expose_document_hashes() -> None:
    service = GraphRAGService.__new__(GraphRAGService)
    service._document_source_labels_cache = {}
    text_unit = {
        "id": "tu-1",
        "document_ids": [
            "1224d1b7896f0c4080d03654dcf42eea041dbdedba4e8198474c2e11082759a4422"
        ],
    }

    label = service._source_label_for_text_unit(text_unit, 8)

    assert label == "Source 8"


def test_target_answer_language_prefers_explicit_instruction() -> None:
    service = GraphRAGService.__new__(GraphRAGService)

    assert service._target_answer_language("Válaszolj magyarul: What happened?") == "Hungarian"
    assert service._target_answer_language("Answer in English: mi történt?") == "English"


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


def test_inactive_ollama_provider_does_not_require_ollama_configuration() -> None:
    settings = make_settings(
        ollama_base_url=None,
        index_chat_provider="gemini",
        index_embed_provider="gemini",
        query_chat_provider="gemini",
        query_embed_provider="gemini",
        gemini_api_key="test-key",
    )

    active_roles = settings.get_active_provider_roles()

    assert all(provider == "gemini" for provider, _model_kind in active_roles.values())


def test_verify_models_checks_only_active_query_roles() -> None:
    service = GraphRAGService.__new__(GraphRAGService)
    service.query_chat_provider = "gemini"
    service.query_embed_provider = "gemini"
    calls: list[tuple[str, str]] = []

    async def check_provider(provider: str, model_kind: str = "both") -> bool:
        calls.append((provider, model_kind))
        return True

    service.check_provider_health = check_provider  # type: ignore[method-assign]

    result = asyncio.run(service.verify_models())

    assert result == {"llm": True, "embedding": True}
    assert calls == [("gemini", "chat"), ("gemini", "embedding")]


def test_gemini_free_tier_guard_defaults_are_conservative() -> None:
    settings = make_settings(query_chat_provider="gemini", gemini_api_key="test-key")

    assert settings.gemini_embed_model == "gemini-embedding-2"
    assert settings.gemini_free_tier_guard_enabled is True
    assert settings.gemini_free_tier_query_rpm == 7
    assert settings.gemini_free_tier_query_tpm == 120_000
    assert settings.gemini_free_tier_query_rpd == 500
    assert settings.gemini_free_tier_index_rpm == 7
    assert settings.gemini_free_tier_index_tpm == 120_000
    assert settings.gemini_free_tier_index_rpd == 500
    assert settings.gemini_free_tier_embed_guard_enabled is True
    assert settings.gemini_free_tier_embed_rpm == 100
    assert settings.gemini_free_tier_embed_tpm == 30_000
    assert settings.gemini_free_tier_embed_rpd == 1_000
    assert settings.gemini_free_tier_embed_batch_size == 16


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


def test_gemini_free_tier_limiter_counts_batch_request_units(tmp_path: Path) -> None:
    limiter = GeminiFreeTierRateLimiter(
        state_path=tmp_path / "gemini-embedding-rate-limit.json",
        requests_per_minute=100,
        tokens_per_minute=30_000,
        requests_per_day=10,
    )

    async def reserve_batch() -> None:
        await limiter.acquire(1_000, request_count=8, label="query embedding")
        with pytest.raises(GeminiRateLimitError, match="napi query embedding limitet"):
            await limiter.acquire(1_000, request_count=3, label="query embedding")

    asyncio.run(reserve_batch())


def test_gemini_embedding_batch_rate_limit_scales_by_batch_size() -> None:
    service = GraphRAGService.__new__(GraphRAGService)

    limits = service._index_embedding_rate_limits("gemini")

    assert limits == {"requests_per_minute": 5, "tokens_per_minute": 30_000}


def test_gemini_index_embedding_request_estimate_is_conservative() -> None:
    service = GraphRAGService.__new__(GraphRAGService)

    assert service._estimate_gemini_index_embedding_requests(12) == 391


def test_delete_current_index_preserves_input_documents(tmp_path: Path) -> None:
    service = GraphRAGService.__new__(GraphRAGService)
    service.input_dir = tmp_path / "input"
    service.output_dir = tmp_path / "output"
    service.cache_dir = tmp_path / "cache"
    service.input_dir.mkdir()
    service.output_dir.mkdir()
    service.cache_dir.mkdir()
    input_file = service.input_dir / "source.txt"
    output_file = service.output_dir / "entities.parquet"
    cache_file = service.cache_dir / "cache.json"
    input_file.write_text("source document", encoding="utf-8")
    output_file.write_text("indexed output", encoding="utf-8")
    cache_file.write_text("cached output", encoding="utf-8")

    service.delete_current_index()

    assert input_file.read_text(encoding="utf-8") == "source document"
    assert service.output_dir.exists()
    assert service.cache_dir.exists()
    assert not output_file.exists()
    assert not cache_file.exists()


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


def test_database_init_script_stays_in_sync_for_retrieved_sources() -> None:
    files = [
        BACKEND_ROOT / "app" / "database.py",
        BACKEND_ROOT / "scripts" / "init_db.py",
    ]

    for path in files:
        content = path.read_text(encoding="utf-8")
        create_messages = re.search(
            r'CREATE_MESSAGES_TABLE = """(?P<body>.*?)"""',
            content,
            flags=re.DOTALL,
        )
        alter_messages = re.search(
            r'ALTER_MESSAGES_SEARCH_METADATA = """(?P<body>.*?)"""',
            content,
            flags=re.DOTALL,
        )

        assert create_messages is not None, f"{path} missing CREATE_MESSAGES_TABLE"
        assert alter_messages is not None, f"{path} missing ALTER_MESSAGES_SEARCH_METADATA"
        assert "retrieved_sources JSON" in create_messages.group("body")
        assert "retrieved_sources JSON" in alter_messages.group("body")


def _env_assignment_value(content: str, name: str) -> str:
    match = re.search(rf"^{name}=(?P<value>.+)$", content, flags=re.MULTILINE)
    assert match is not None, f"Missing {name}"
    return match.group("value").strip()


def _compose_fallback_value(content: str, name: str) -> str:
    match = re.search(rf"{name}=\$\{{{name}:-(?P<value>[^}}]+)\}}", content)
    assert match is not None, f"Missing compose fallback for {name}"
    return match.group("value").strip()


def test_graphrag_chunk_defaults_are_consistent_in_config_and_docs() -> None:
    expected_size = "1000"
    expected_overlap = "150"
    root_env = (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8")
    backend_env = (BACKEND_ROOT / ".env.example").read_text(encoding="utf-8")
    compose = (PROJECT_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    docs = (PROJECT_ROOT / "docs" / "graphrag-optimization.md").read_text(encoding="utf-8")

    assert _env_assignment_value(root_env, "APP_GRAPHRAG_CHUNK_SIZE") == expected_size
    assert _env_assignment_value(root_env, "APP_GRAPHRAG_CHUNK_OVERLAP") == expected_overlap
    assert _env_assignment_value(backend_env, "APP_GRAPHRAG_CHUNK_SIZE") == expected_size
    assert _env_assignment_value(backend_env, "APP_GRAPHRAG_CHUNK_OVERLAP") == expected_overlap
    assert _compose_fallback_value(compose, "APP_GRAPHRAG_CHUNK_SIZE") == expected_size
    assert _compose_fallback_value(compose, "APP_GRAPHRAG_CHUNK_OVERLAP") == expected_overlap
    assert "APP_GRAPHRAG_CHUNK_SIZE=1000" in readme
    assert "APP_GRAPHRAG_CHUNK_OVERLAP=150" in readme

    current_defaults = re.search(
        r"## Current Index Defaults.*?```env(?P<body>.*?)```",
        docs,
        flags=re.DOTALL,
    )
    assert current_defaults is not None
    assert "APP_GRAPHRAG_CHUNK_SIZE=1000" in current_defaults.group("body")
    assert "APP_GRAPHRAG_CHUNK_OVERLAP=150" in current_defaults.group("body")


def test_controlled_expected_graph_spec_is_well_formed() -> None:
    spec_path = BACKEND_ROOT / "samples" / "controlled_tech_corpus" / "expected_graph.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))

    assert spec["minimum_counts"]["documents"] >= 3
    assert spec["minimum_counts"]["text_units"] >= 3
    assert spec["minimum_counts"]["entities"] >= 8
    assert spec["minimum_counts"]["relationships"] >= 5

    entity_names = [entity["name"].casefold() for entity in spec["entities"]]
    assert len(entity_names) == len(set(entity_names))
    assert {"orion assistant", "atlasgraph", "betabank policy"}.issubset(entity_names)

    relationships = spec["relationships"]
    assert len(relationships) >= 5
    expected_entities = set(entity_names)
    for relationship in relationships:
        assert relationship["source"].casefold() in expected_entities
        assert relationship["target"].casefold() in expected_entities
        assert int(relationship.get("max_path_length", 1)) >= 1


def test_graph_transform_adds_edges_and_component_metadata_from_records() -> None:
    service = GraphRAGService.__new__(GraphRAGService)
    entities = [
        {
            "title": "Orion Assistant",
            "type": "technology",
            "description": "Policy assistant.",
            "x": 0.0,
            "y": 0.0,
        },
        {
            "title": "Maya Chen",
            "type": "person",
            "description": "Lead architect of Orion Assistant.",
        },
        {
            "title": "AtlasGraph",
            "type": "technology",
            "description": "Stores extracted relationships.",
        },
        {
            "title": "EmbedLite",
            "type": "technology",
            "description": "Creates embeddings.",
        },
    ]
    relationships = [
        {
            "source": "Maya Chen",
            "target": "Orion Assistant",
            "description": "lead architect of",
            "weight": 1.5,
        },
        {
            "source": "Orion Assistant",
            "target": "AtlasGraph",
            "description": "uses",
            "weight": 2,
        },
        {
            "source": "Ravi Patel",
            "target": "Ingestion Pipeline",
            "description": "maintains",
            "weight": 1,
        },
    ]

    nodes, duplicate_count = service._transform_entities_to_nodes(entities)
    edges, graph_nodes, cleanup_stats = service._transform_relationships_to_edges(
        relationships,
        nodes,
    )
    metadata = service._annotate_graph_components(graph_nodes, edges)
    node_by_label = {node["data"]["label"]: node for node in graph_nodes}

    assert duplicate_count == 0
    assert len(edges) == 3
    assert cleanup_stats["relationship_only_node_count"] == 2
    assert node_by_label["Ravi Patel"]["data"]["generated_from_relationship"] is True
    assert node_by_label["EmbedLite"]["data"]["degree"] == 0
    assert node_by_label["EmbedLite"]["data"]["is_isolated"] is True
    assert metadata["isolated_node_count"] == 1
    assert metadata["largest_component_node_count"] == 3
