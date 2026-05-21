"""Validate an existing GraphRAG index against the controlled sample corpus.

The script does not run indexing. It reads the current GraphRAG output directory
and checks that a previously indexed controlled sample produced the expected
minimum graph shape.
"""

from __future__ import annotations

import argparse
import asyncio
import copy
import json
import os
import re
import sys
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd  # type: ignore

BACKEND_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_EXPECTED_GRAPH = BACKEND_ROOT / "samples" / "controlled_tech_corpus" / "expected_graph.json"
COMBINED_CONTROLLED_CORPUS_FILENAME = "controlled_tech_corpus_all.txt"
COUNT_FILES = {
    "documents": "documents.parquet",
    "text_units": "text_units.parquet",
    "entities": "entities.parquet",
    "relationships": "relationships.parquet",
}
EMPTY_INDEX_DIAGNOSTIC_FIELDS = (
    "document_count",
    "text_unit_count",
    "entity_count",
    "relationship_count",
)


@dataclass
class ValidationResult:
    """Structured validation outcome for script output and tests."""

    counts: dict[str, int] = field(default_factory=dict)
    diagnostics: dict[str, Any] = field(default_factory=dict)
    matched_relationships: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


@dataclass(frozen=True)
class GraphWorkspaceSelection:
    """Resolved GraphRAG workspace and catalog metadata used for validation."""

    root: Path
    source: str
    graph_id: str | None = None
    source_filename: str | None = None


def normalize_name(value: Any) -> str:
    """Normalize names for case, punctuation, and GraphRAG quote variants."""
    text = str(value or "").strip().strip('"').strip("'")
    text = text.replace("’", "'")
    text = re.sub(r"[^\w\s]", " ", text.casefold(), flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def load_expected_graph(path: Path = DEFAULT_EXPECTED_GRAPH) -> dict[str, Any]:
    """Load the controlled sample expectation file."""
    return json.loads(path.read_text(encoding="utf-8"))


def adapt_expected_graph_for_source(spec: dict[str, Any], source_filename: str | None) -> dict[str, Any]:
    """Adjust expectations for supported alternate controlled-corpus upload shapes."""
    if source_filename != COMBINED_CONTROLLED_CORPUS_FILENAME:
        return spec

    adapted = copy.deepcopy(spec)
    minimum_counts = adapted.setdefault("minimum_counts", {})
    minimum_counts["documents"] = 1
    minimum_counts["text_units"] = 1

    for relationship in adapted.get("relationships", []):
        if not isinstance(relationship, dict):
            continue
        source = normalize_name(relationship.get("source"))
        target = normalize_name(relationship.get("target"))
        if source == "ravi patel" and target == "ingestion pipeline":
            relationship["max_path_length"] = max(int(relationship.get("max_path_length", 1)), 2)

    return adapted


def validate_expected_graph_spec(spec: dict[str, Any]) -> ValidationResult:
    """Validate the expected graph contract before applying it to GraphRAG output."""
    result = ValidationResult()
    if not isinstance(spec.get("minimum_counts"), dict):
        result.errors.append("expected_graph.json must contain a minimum_counts object.")

    entities = spec.get("entities")
    if not isinstance(entities, list) or not entities:
        result.errors.append("expected_graph.json must contain a non-empty entities list.")
        entities = []

    entity_names = [normalize_name(entity.get("name")) for entity in entities if isinstance(entity, dict)]
    if any(not name for name in entity_names):
        result.errors.append("Every expected entity must have a non-empty name.")
    if len(entity_names) != len(set(entity_names)):
        result.errors.append("Expected entity names must be unique after normalization.")

    relationships = spec.get("relationships")
    if not isinstance(relationships, list):
        result.errors.append("expected_graph.json must contain a relationships list.")
        relationships = []
    if len(relationships) < 5:
        result.errors.append("expected_graph.json must define at least 5 expected relationships.")

    entity_name_set = set(entity_names)
    for index, relationship in enumerate(relationships, start=1):
        if not isinstance(relationship, dict):
            result.errors.append(f"Expected relationship #{index} must be an object.")
            continue
        source = normalize_name(relationship.get("source"))
        target = normalize_name(relationship.get("target"))
        if not source or not target:
            result.errors.append(f"Expected relationship #{index} needs source and target.")
            continue
        if entity_name_set and source not in entity_name_set:
            result.errors.append(
                f"Expected relationship #{index} source is not listed as an entity: {relationship.get('source')}"
            )
        if entity_name_set and target not in entity_name_set:
            result.errors.append(
                f"Expected relationship #{index} target is not listed as an entity: {relationship.get('target')}"
            )

    return result


def read_parquet_records(output_dir: Path, filename: str) -> list[dict[str, Any]]:
    """Read a GraphRAG parquet file into plain records, or return an empty list."""
    path = output_dir / filename
    if not path.exists():
        return []
    df = pd.read_parquet(path)
    return df.to_dict("records")  # type: ignore[no-any-return]


def entity_names_from_records(records: list[dict[str, Any]]) -> set[str]:
    """Return normalized GraphRAG entity names from entity output records."""
    names: set[str] = set()
    for entity in records:
        name = normalize_name(entity.get("title", entity.get("name", "")))
        if name:
            names.add(name)
    return names


def relationship_graph(
    records: list[dict[str, Any]],
) -> tuple[set[tuple[str, str]], dict[str, set[str]]]:
    """Build undirected direct-pair and adjacency structures from relationship records."""
    direct_pairs: set[tuple[str, str]] = set()
    adjacency: dict[str, set[str]] = {}

    for relationship in records:
        source = normalize_name(relationship.get("source"))
        target = normalize_name(relationship.get("target"))
        if not source or not target or source == target:
            continue

        direct_pairs.add((source, target))
        direct_pairs.add((target, source))
        adjacency.setdefault(source, set()).add(target)
        adjacency.setdefault(target, set()).add(source)

    return direct_pairs, adjacency


def has_path(
    adjacency: dict[str, set[str]],
    source: str,
    target: str,
    max_path_length: int,
) -> bool:
    """Return whether source and target are connected within max_path_length edges."""
    if source == target:
        return True
    if max_path_length < 1:
        return False

    queue: deque[tuple[str, int]] = deque([(source, 0)])
    seen = {source}
    while queue:
        current, depth = queue.popleft()
        if depth >= max_path_length:
            continue
        for neighbor in adjacency.get(current, set()):
            if neighbor == target:
                return True
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append((neighbor, depth + 1))
    return False


def validate_output_against_spec(
    output_dir: Path,
    spec: dict[str, Any],
    diagnostics: dict[str, Any] | None = None,
) -> ValidationResult:
    """Validate existing GraphRAG output against the controlled expected graph."""
    result = validate_expected_graph_spec(spec)
    if result.errors:
        return result

    records_by_key = {
        key: read_parquet_records(output_dir, filename) for key, filename in COUNT_FILES.items()
    }
    result.counts = {key: len(records) for key, records in records_by_key.items()}

    minimum_counts = spec["minimum_counts"]
    for key, minimum in minimum_counts.items():
        if key not in result.counts:
            result.warnings.append(f"Unknown minimum count key ignored: {key}")
            continue
        if result.counts[key] < int(minimum):
            result.errors.append(
                f"{key} count is {result.counts[key]}, expected at least {int(minimum)}."
            )

    actual_entities = entity_names_from_records(records_by_key["entities"])
    for entity in spec["entities"]:
        expected_name = normalize_name(entity["name"])
        if expected_name not in actual_entities:
            result.errors.append(f"Missing expected entity: {entity['name']}")

    direct_pairs, adjacency = relationship_graph(records_by_key["relationships"])
    for relationship in spec["relationships"]:
        source = normalize_name(relationship["source"])
        target = normalize_name(relationship["target"])
        max_path_length = int(relationship.get("max_path_length", 1))
        label = f"{relationship['source']} -> {relationship['target']}"

        if (source, target) in direct_pairs:
            result.matched_relationships.append(f"{label} (direct)")
        elif has_path(adjacency, source, target, max_path_length):
            result.matched_relationships.append(f"{label} (path <= {max_path_length})")
        else:
            result.errors.append(
                f"Missing expected relationship pair or path: {label} "
                f"(max_path_length={max_path_length})"
            )

    if diagnostics:
        result.diagnostics = diagnostics
        for field_name in EMPTY_INDEX_DIAGNOSTIC_FIELDS:
            value = int(diagnostics.get(field_name, 0) or 0)
            if value <= 0:
                result.errors.append(f"Diagnostics indicate an empty index: {field_name}=0.")

        for warning in diagnostics.get("warnings", []):
            normalized_warning = str(warning).casefold()
            if "empty" in normalized_warning or "no source text units" in normalized_warning:
                result.errors.append(f"Critical diagnostics warning: {warning}")

    return result


def configured_graphrag_root() -> Path:
    """Return APP_GRAPHRAG_ROOT from the app configuration."""
    env_root = os.getenv("APP_GRAPHRAG_ROOT")
    if env_root:
        return Path(env_root)

    sys.path.append(str(BACKEND_ROOT))
    from app.config import settings  # type: ignore

    return Path(settings.graphrag_root)


async def active_graph_workspace_from_database() -> GraphWorkspaceSelection | None:
    """Return the active completed graph workspace from the graph catalog, if available."""
    sys.path.append(str(BACKEND_ROOT))
    from sqlalchemy import text  # type: ignore

    from app.database import async_session_maker  # type: ignore

    async with async_session_maker() as session:
        result = await session.execute(
            text("""
                SELECT id, source_filename, workspace_path
                FROM indexed_graphs
                WHERE is_active = TRUE
                  AND status = 'completed'
                  AND workspace_path IS NOT NULL
                ORDER BY activated_at DESC NULLS LAST,
                         indexed_at DESC NULLS LAST,
                         created_at DESC
                LIMIT 1
            """)
        )
        row = result.fetchone()

    if row is None:
        return None

    return GraphWorkspaceSelection(
        root=Path(row.workspace_path),
        source="active graph catalog",
        graph_id=str(row.id),
        source_filename=str(row.source_filename) if row.source_filename else None,
    )


def default_workspace_selection() -> GraphWorkspaceSelection:
    """Resolve the default workspace for validation in single- and multi-graph installs."""
    try:
        active_workspace = asyncio.run(active_graph_workspace_from_database())
    except Exception as exc:
        return GraphWorkspaceSelection(
            root=configured_graphrag_root(),
            source=f"configured APP_GRAPHRAG_ROOT; active graph lookup failed: {exc}",
        )

    if active_workspace is not None:
        return active_workspace

    return GraphWorkspaceSelection(
        root=configured_graphrag_root(),
        source="configured APP_GRAPHRAG_ROOT; no active completed graph found",
    )


def service_diagnostics(graphrag_root: Path) -> dict[str, Any]:
    """Call the existing GraphRAG service diagnostics method."""
    sys.path.append(str(BACKEND_ROOT))
    from app.services.graphrag import graphrag_service  # type: ignore

    graphrag_service.use_workspace(graphrag_root)
    diagnostics = graphrag_service.get_diagnostics()
    return diagnostics if isinstance(diagnostics, dict) else {}


def print_result(result: ValidationResult) -> None:
    """Print a compact validation report."""
    print("Controlled sample validation")
    print(f"Counts: {json.dumps(result.counts, sort_keys=True)}")
    print(f"Matched relationships: {len(result.matched_relationships)}")

    if result.diagnostics:
        diagnostic_counts = {
            key: result.diagnostics.get(key)
            for key in EMPTY_INDEX_DIAGNOSTIC_FIELDS
            if key in result.diagnostics
        }
        print(f"Diagnostics: {json.dumps(diagnostic_counts, sort_keys=True)}")

    for warning in result.warnings:
        print(f"WARNING: {warning}")
    for note in result.notes:
        print(f"INFO: {note}")
    for error in result.errors:
        print(f"ERROR: {error}")

    print("PASS" if result.ok else "FAIL")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--graphrag-root",
        type=Path,
        default=None,
        help="GraphRAG workspace root. Defaults to configured APP_GRAPHRAG_ROOT.",
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
    print_result(result)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
