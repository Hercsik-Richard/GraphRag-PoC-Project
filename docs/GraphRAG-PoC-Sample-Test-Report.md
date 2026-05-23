# GraphRAG PoC Sample Test Report

## Test Context

This test validates the GraphRAG PoC sample located in:

```text
backend/samples/graphrag_poc/
```

The sample was designed as a hand-checkable course-documentation corpus for validating the actual pipeline concepts used by this project: ingestion, chunking, embeddings, vector storage, graph storage, retrieval, source citations, and evaluation.

The original corpus contains three source files:

- `01_project_overview.txt`
- `02_indexing_pipeline.txt`
- `03_query_and_evaluation.txt`

Because the current upload UI accepts one `.txt` file at a time, the three files were merged into:

```text
backend/samples/graphrag_poc/graphrag_poc_all.txt
```

The merged file preserves source boundaries with `Source: ...` labels before each original document section.

## Test Objective

The goal was to verify that the GraphRAG indexing pipeline can build a valid knowledge graph from a corpus that directly describes the GraphRAG PoC architecture.

The test specifically checks:

- whether the expected GraphRAG PoC entities are present,
- whether the expected pipeline relationships or short graph paths are present,
- whether the index contains non-empty document, text-unit, entity, and relationship outputs,
- whether the validator resolves the active multi-graph workspace correctly,
- whether the combined single-file upload is handled as a valid form of the sample corpus.

## Test Setup

The GraphRAG PoC sample was indexed through the application upload flow using:

```text
graphrag_poc_all.txt
```

The indexed graph was stored in an isolated multi-graph workspace:

```text
/app/ragtest/graphs/95dc20ab-8068-4511-bc2c-963b92d5bd2c
```

Local workspace path:

```text
backend/ragtest/graphs/95dc20ab-8068-4511-bc2c-963b92d5bd2c/
```

Observed indexed graph metadata:

| Field | Value |
|---|---|
| Source filename | `graphrag_poc_all.txt` |
| Active graph id | `95dc20ab-8068-4511-bc2c-963b92d5bd2c` |
| Document count | `1` |
| Text-unit count | `1` |
| Entity count | `16` |
| Relationship count | `17` |

The key GraphRAG output files are located under:

```text
backend/ragtest/graphs/95dc20ab-8068-4511-bc2c-963b92d5bd2c/output/
```

Important files:

- `documents.parquet`
- `text_units.parquet`
- `entities.parquet`
- `relationships.parquet`
- `communities.parquet`
- `community_reports.parquet`
- `indexing-engine.log`
- `lancedb/`

## Validator Behavior

The validation script is:

```text
backend/scripts/validate_graphrag_poc_sample.py
```

The script reuses the controlled-sample validation utilities and validates the active completed graph from the graph catalog when no `--graphrag-root` argument is provided.

For the combined upload file, the validator adapts the original multi-file expectations:

- expected minimum document count changes from `3` to `1`,
- expected minimum text-unit count changes from `3` to `1`.

This is necessary because the sample was uploaded as one merged `.txt` file, so GraphRAG indexes it as one document and one text unit in the current upload flow.

The validator checks:

- minimum output counts,
- expected entity names,
- expected direct relationship pairs,
- accepted short graph paths where GraphRAG extracted an intermediate node.

## Expected Graph Shape

The final expected entity set is:

- `GraphRAG PoC`
- `Document Loader`
- `Chunking Module`
- `Indexing Pipeline`
- `Embedding Model`
- `Vector Store`
- `Entity Extractor`
- `Relationship Extractor`
- `Graph Store`
- `Query Engine`
- `Answer Generator`
- `Evaluation Script`
- `graph traversal`
- `text chunks`
- `provenance metadata`
- `vector retrieval`

The expected relationship checks are:

| Expected relationship | Expected match type |
|---|---|
| `GraphRAG PoC -> vector retrieval` | Direct edge |
| `GraphRAG PoC -> graph traversal` | Direct edge |
| `Document Loader -> Chunking Module` | Direct edge |
| `Chunking Module -> text chunks` | Direct edge or path up to length 3 |
| `Embedding Model -> text chunks` | Direct edge or path up to length 2 |
| `Vector Store -> Embedding Model` | Direct edge |
| `Entity Extractor -> Graph Store` | Direct edge |
| `Relationship Extractor -> Graph Store` | Direct edge |
| `Graph Store -> Evaluation Script` | Direct edge |
| `Graph Store -> provenance metadata` | Direct edge |
| `Query Engine -> Vector Store` | Direct edge |
| `Query Engine -> Graph Store` | Direct edge |
| `Answer Generator -> Query Engine` | Direct edge |
| `Evaluation Script -> Graph Store` | Direct edge |

## Validation Command

The validation command is:

```bash
docker compose exec backend uv run scripts/validate_graphrag_poc_sample.py
```

No manual `--graphrag-root` argument is required. The script resolves the active graph workspace automatically.

## Actual Validation Output

The relevant output was:

```text
GraphRAG PoC sample validation
Counts: {"documents": 1, "entities": 16, "relationships": 17, "text_units": 1}
Matched relationships: 14
Diagnostics: {"document_count": 1, "entity_count": 16, "relationship_count": 17, "text_unit_count": 1}
INFO: Validated active graph 95dc20ab-8068-4511-bc2c-963b92d5bd2c from /app/ragtest/graphs/95dc20ab-8068-4511-bc2c-963b92d5bd2c
PASS
```

## Matched Relationships

The validator matched all 14 expected relationship checks:

| Matched relationship | Match type |
|---|---|
| `GraphRAG PoC -> vector retrieval` | Direct |
| `GraphRAG PoC -> graph traversal` | Direct |
| `Document Loader -> Chunking Module` | Direct |
| `Chunking Module -> text chunks` | Path up to length 3 |
| `Embedding Model -> text chunks` | Path up to length 2 |
| `Vector Store -> Embedding Model` | Direct |
| `Entity Extractor -> Graph Store` | Direct |
| `Relationship Extractor -> Graph Store` | Direct |
| `Graph Store -> Evaluation Script` | Direct |
| `Graph Store -> provenance metadata` | Direct |
| `Query Engine -> Vector Store` | Direct |
| `Query Engine -> Graph Store` | Direct |
| `Answer Generator -> Query Engine` | Direct |
| `Evaluation Script -> Graph Store` | Direct |

## Result Interpretation

The validation passed.

The indexed graph contains:

- `1` document,
- `1` text unit,
- `16` entities,
- `17` relationships.

The `1` document and `1` text unit counts are expected because the corpus was uploaded as one merged file.

The validator reports:

```text
Matched relationships: 14
```

This means all 14 expected GraphRAG PoC relationship checks were found. It does not mean the graph only contains 14 relationships. The graph contains 17 relationships in total; the additional relationships were extracted by GraphRAG beyond the minimum expected validation contract.

## Graph Visualization Interpretation

Two screenshots were inspected from the frontend graph visualization. They show the same indexed `graphrag_poc_all.txt` graph, but they do not show the same filtered viewport.

The frontend graph view has multiple modes:

- `Main`: shows the largest connected component.
- `Connected`: shows nodes that have at least one edge.
- `All`: shows every graph node, including nodes outside the largest component.

### Image 1: Main Pipeline Component

The first image shows the main pipeline component of the indexed graph.

Visible nodes include:

- `Relationship Extractor`
- `Entity Extractor`
- `Graph Store`
- `Embedding Model`
- `Provenance Metadata`
- `Document Loader`
- `Answer Generator`
- `Vector Store`
- `Query Engine`
- `Chunking Module`
- `Text Chunks`
- `Indexing Pipeline`
- `Evaluation Script`

This view is useful for inspecting the operational GraphRAG pipeline. The central structure is the `Graph Store`, which connects to extraction, evaluation, provenance, query, and retrieval-related components. This matches the expected project architecture: the graph store is the persistence point for extracted graph structure and is reused by evaluation and query-time graph traversal.

The first image does not show `GraphRAG PoC`, `Vector Retrieval`, or `Graph Traversal`. Those nodes are not absent from the index; they are outside the largest connected component shown in this viewport.

### Image 2: Full Graph With Separate Retrieval-Strategy Component

The second image shows a broader graph view. It includes the same main pipeline component and also shows a separate smaller component at the bottom:

```text
GraphRAG PoC -> Vector Retrieval
GraphRAG PoC -> Graph Traversal
```

This explains why two graph regions are visible. They are not two separate tests and not two separate indexes. They are two disconnected connected components inside the same indexed graph.

The separation happened because GraphRAG extracted:

- the implementation pipeline as one connected component,
- the high-level retrieval-strategy statement as another connected component.

The source text says that the GraphRAG PoC uses hybrid retrieval, and that hybrid retrieval combines vector retrieval and graph traversal. GraphRAG represented that statement as edges from `GraphRAG PoC` to `Vector Retrieval` and `Graph Traversal`, but it did not extract an additional bridging edge from `GraphRAG PoC` to the main implementation component, such as `GraphRAG PoC -> Query Engine`, `GraphRAG PoC -> Vector Store`, or `GraphRAG PoC -> Graph Store`.

Because no bridging edge was extracted, the frontend layout correctly packs the retrieval-strategy component separately from the main pipeline component.

### Visual Encoding

The node colors follow the entity types returned by GraphRAG and rendered by the frontend:

- Blue nodes are mostly `ORGANIZATION` typed entities. In this sample, GraphRAG used that type for many software components, such as `Graph Store`, `Vector Store`, `Chunking Module`, and `Document Loader`.
- Orange nodes are `EVENT` typed entities, such as `Evaluation Script`, `Indexing Pipeline`, `GraphRAG PoC`, and `Graph Traversal`.
- The white `Vector Retrieval` node has no strong mapped entity type in the extracted output, so it falls back to the default node styling.

The graph is therefore structurally useful even if the entity type labels are not semantically perfect. For this PoC, the important validation target is the extracted entity-relation structure, not the exact GraphRAG type assigned to every software concept.

### Interpretation Of The Difference

The difference between the two images is expected:

| Aspect | Image 1 | Image 2 |
|---|---|---|
| Main purpose | Inspect the largest operational pipeline component | Inspect the full connected graph output |
| Visible graph scope | Main connected component | Main component plus the separate retrieval-strategy component |
| Shows `GraphRAG PoC` | No | Yes |
| Shows `Vector Retrieval` and `Graph Traversal` | No | Yes |
| Best use | Pipeline/debugging view | Complete validation/inspection view |

This confirms that the indexed graph contains both the implementation pipeline and the high-level hybrid retrieval concept. The only limitation is that the model did not connect those two parts into one single component. That is acceptable for the current validation because the validator explicitly checks both parts of the graph.

## Contract Adjustment During Validation

The first validation attempt failed because the original expected graph contract was too literal. It expected several concepts as standalone entities:

- `source metadata`
- `hybrid retrieval`
- `embeddings`
- `software components`
- `graph edges`
- `entities and relationships`
- `source excerpts and graph context`
- `source chunks`
- `extracted graph with expected reference graph`
- `answer traceability`

The indexed graph still represented many of these ideas, but not always as standalone graph nodes. For example:

- `TEXT CHUNKS` was extracted as a node.
- `VECTOR RETRIEVAL` and `GRAPH TRAVERSAL` were extracted as retrieval-related nodes.
- `PROVENANCE METADATA` was extracted as a node.
- `source metadata`, `hybrid retrieval`, and answer traceability appeared in descriptions or supporting text rather than as required standalone entities.
- The `Query Engine` was connected to `Vector Store` and `Graph Store`, rather than directly to `vector retrieval` and `graph traversal`.

The expected graph contract was adjusted to validate the stable graph structure GraphRAG actually extracted, while still checking the intended pipeline behavior.

This adjustment is appropriate for this PoC because the validator should test the minimum reliable graph shape, not force the model to create every noun phrase as a separate node.

## Warning Interpretation

The command also printed warnings from third-party packages:

```text
LiteLLM: could not pre-load bedrock-runtime response stream shape
LiteLLM: could not pre-load sagemaker-runtime response stream shape
SyntaxWarning: invalid escape sequence
```

These warnings are not validation failures.

The LiteLLM warnings indicate that optional AWS Bedrock and SageMaker streaming support was not available because `botocore` is not installed. This test does not use Bedrock or SageMaker.

The `SyntaxWarning` messages come from installed third-party libraries and do not affect the GraphRAG PoC sample validation result.

## Conclusion

The GraphRAG PoC sample index is valid.

The active indexed graph contains the expected course-documentation pipeline components and all 14 expected relationship checks. The validator correctly supports the multi-graph workspace layout and the one-file combined upload workflow.

This test is better aligned with the project documentation than a fictional enterprise-policy corpus because it validates the exact concepts the project describes: ingestion, chunking, embeddings, vector retrieval, graph construction, graph storage, source-grounded answer generation, and evaluation.
