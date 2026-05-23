"""Opt-in integration checks for the GraphRAG PoC sample."""

import asyncio
import os

import pytest

pytestmark = pytest.mark.integration


def test_graphrag_poc_sample_index_validates_and_source_query_returns_sources() -> None:
    if os.getenv("RUN_GRAPHRAG_POC_INTEGRATION") != "1":
        pytest.skip(
            "Set RUN_GRAPHRAG_POC_INTEGRATION=1 after indexing the GraphRAG PoC sample."
        )

    from app.schemas.graph import GraphDataSchema
    from app.services.graphrag import graphrag_service
    from scripts.validate_controlled_sample import (
        default_workspace_selection,
        load_expected_graph,
        service_diagnostics,
        validate_output_against_spec,
    )
    from scripts.validate_graphrag_poc_sample import (
        DEFAULT_EXPECTED_GRAPH,
        adapt_expected_graph_for_source,
    )

    workspace = default_workspace_selection()
    graphrag_service.use_workspace(workspace.root)

    result = validate_output_against_spec(
        workspace.root / "output",
        adapt_expected_graph_for_source(
            load_expected_graph(DEFAULT_EXPECTED_GRAPH),
            workspace.source_filename,
        ),
        service_diagnostics(workspace.root),
    )

    assert result.ok, "\n".join(result.errors)
    GraphDataSchema(**graphrag_service.get_full_graph())

    query_result = asyncio.run(
        graphrag_service.query(
            "Which component creates the text chunks?",
            search_mode="source",
        )
    )

    assert query_result["retrieved_sources"]
