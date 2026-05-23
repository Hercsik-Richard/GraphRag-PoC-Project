"""Validate an existing GraphRAG index against the GraphRAG PoC sample.

The script does not run indexing. It reads the current GraphRAG output directory
and checks that a previously indexed GraphRAG PoC sample produced the expected
minimum graph shape.
"""

from __future__ import annotations

import argparse
import copy
from pathlib import Path
from typing import Any

try:
    from validate_controlled_sample import (
        BACKEND_ROOT,
        GraphWorkspaceSelection,
        default_workspace_selection,
        load_expected_graph,
        print_result,
        service_diagnostics,
        validate_output_against_spec,
    )
except ModuleNotFoundError:
    from scripts.validate_controlled_sample import (
        BACKEND_ROOT,
        GraphWorkspaceSelection,
        default_workspace_selection,
        load_expected_graph,
        print_result,
        service_diagnostics,
        validate_output_against_spec,
    )

DEFAULT_EXPECTED_GRAPH = (
    BACKEND_ROOT / "samples" / "graphrag_poc" / "expected_graph.json"
)
COMBINED_GRAPHRAG_POC_FILENAME = "graphrag_poc_all.txt"


def adapt_expected_graph_for_source(spec: dict[str, Any], source_filename: str | None) -> dict[str, Any]:
    """Adjust expectations for the supported combined GraphRAG PoC upload."""
    if source_filename != COMBINED_GRAPHRAG_POC_FILENAME:
        return spec

    adapted = copy.deepcopy(spec)
    minimum_counts = adapted.setdefault("minimum_counts", {})
    minimum_counts["documents"] = 1
    minimum_counts["text_units"] = 1
    return adapted


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--graphrag-root",
        type=Path,
        default=None,
        help="GraphRAG workspace root. Defaults to the active graph catalog entry or APP_GRAPHRAG_ROOT.",
    )
    parser.add_argument(
        "--expected-graph",
        type=Path,
        default=DEFAULT_EXPECTED_GRAPH,
        help="Path to expected_graph.json.",
    )
    parser.add_argument(
        "--skip-diagnostics",
        action="store_true",
        help="Skip the app GraphRAG get_diagnostics() check.",
    )
    args = parser.parse_args()

    if args.graphrag_root:
        workspace = GraphWorkspaceSelection(root=args.graphrag_root, source="--graphrag-root")
    else:
        workspace = default_workspace_selection()

    expected_graph = adapt_expected_graph_for_source(
        load_expected_graph(args.expected_graph),
        workspace.source_filename,
    )

    diagnostics: dict[str, Any] | None = None
    if not args.skip_diagnostics:
        diagnostics = service_diagnostics(workspace.root)

    result = validate_output_against_spec(workspace.root / "output", expected_graph, diagnostics)
    if workspace.graph_id:
        result.notes.append(f"Validated active graph {workspace.graph_id} from {workspace.root}")
    elif workspace.source != "--graphrag-root":
        result.notes.append(f"Validated {workspace.root} from {workspace.source}")

    print_result(result, title="GraphRAG PoC sample validation")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
