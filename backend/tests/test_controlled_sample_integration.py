"""Opt-in integration checks for the controlled GraphRAG sample."""

import asyncio
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration


def test_controlled_sample_index_validates_and_source_query_returns_sources() -> None:
    if os.getenv("RUN_GRAPHRAG_INTEGRATION") != "1":
        pytest.skip("Set RUN_GRAPHRAG_INTEGRATION=1 after indexing the controlled sample.")

    from app.config import settings
    from app.schemas.graph import GraphDataSchema
    from app.services.graphrag import graphrag_service
    from scripts.validate_controlled_sample import (
        DEFAULT_EXPECTED_GRAPH,
        load_expected_graph,
        validate_output_against_spec,
    )

    graphrag_root = Path(settings.graphrag_root)
    diagnostics = graphrag_service.get_diagnostics()
    result = validate_output_against_spec(
        graphrag_root / "output",
        load_expected_graph(DEFAULT_EXPECTED_GRAPH),
        diagnostics,
    )

    assert result.ok, "\n".join(result.errors)
    GraphDataSchema(**graphrag_service.get_full_graph())

    query_result = asyncio.run(
        graphrag_service.query(
            "Based on the indexed source, which policy document does Orion Assistant cite?",
            search_mode="source",
        )
    )

    assert query_result["retrieved_sources"]
