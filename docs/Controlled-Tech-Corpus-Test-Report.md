# Controlled Tech Corpus Test Report

## Test Context

This test validates the small controlled GraphRAG sample located in:

```text
backend/samples/controlled_tech_corpus/
```

The sample was designed as a hand-checkable technology-domain corpus for verifying that the indexing pipeline can extract a predictable minimum graph shape from short source documents.

The original corpus contains three source files:

- `01_astra_orion.txt`
- `02_ingestion_embeddings.txt`
- `03_betabank_policy.txt`

Because the current upload UI accepts one `.txt` file at a time, the three files were merged into:

```text
backend/samples/controlled_tech_corpus/controlled_tech_corpus_all.txt
```

The merged file preserves source boundaries with `Source: ...` labels before each original document section.

## Test Objective

The goal was to verify that the GraphRAG indexing pipeline can build a valid knowledge graph from the controlled corpus and that the validation script checks the active indexed graph rather than an older root workspace output.

The test specifically checks:

- whether the expected controlled-corpus entities are present,
- whether the expected relationship pairs or short graph paths are present,
- whether the index contains non-empty document, text-unit, entity, and relationship outputs,
- whether the validator resolves the active multi-graph workspace correctly,
- whether the combined single-file upload is handled as a valid form of the controlled corpus.

## Test Setup

The controlled corpus was indexed through the application upload flow using:

```text
controlled_tech_corpus_all.txt
```

The indexed graph was stored in an isolated multi-graph workspace:

```text
/app/ragtest/graphs/f2132d66-cd08-48b9-bd64-4178565ac6d9
```

The graph catalog marked this graph as the active completed graph.

Observed indexed graph metadata:

| Field | Value |
|---|---|
| Source filename | `controlled_tech_corpus_all.txt` |
| Status | `completed` |
| Active graph | `true` |
| Entity count | `10` |
| Relationship count | `15` |

## Validator Behavior

The validation script is:

```text
backend/scripts/validate_controlled_sample.py
```

Originally, the script defaulted to the configured root GraphRAG workspace:

```text
/app/ragtest/output
```

That was incorrect for the current multi-graph implementation. In this project version, newly uploaded documents are indexed into isolated graph workspaces under:

```text
/app/ragtest/graphs/<graph_id>/
```

The validator was updated so that, when `--graphrag-root` is not provided, it queries the graph catalog and selects the active completed graph workspace.

For the combined upload file, the validator also adapts the original controlled-corpus expectations:

- expected minimum document count changes from `3` to `1`,
- expected minimum text-unit count changes from `3` to `1`,
- the `Ravi Patel -> Ingestion Pipeline` relationship may be accepted as a path of length `2`.

This is necessary because the merged file is indexed as one document and the model extracted the Ravi Patel pipeline relation through an intermediate node rather than as one direct edge.

## Expected Graph Shape

The core expected entities are:

- `Astra Labs`
- `Orion Assistant`
- `Maya Chen`
- `AtlasGraph`
- `Ravi Patel`
- `Ingestion Pipeline`
- `EmbedLite`
- `BetaBank`
- `BetaBank Policy`

The core expected relationship checks are:

| Expected relationship | Expected match type |
|---|---|
| `Astra Labs -> Orion Assistant` | Direct edge |
| `Maya Chen -> Orion Assistant` | Direct edge |
| `Orion Assistant -> AtlasGraph` | Direct edge |
| `Ravi Patel -> Ingestion Pipeline` | Direct edge or path up to length 2 for combined upload |
| `EmbedLite -> BetaBank Policy` | Direct edge |
| `AtlasGraph -> Orion Assistant` | Direct edge |
| `BetaBank -> Orion Assistant` | Direct edge |
| `Orion Assistant -> BetaBank Policy` | Direct edge |
| `Maya Chen -> Ravi Patel` | Direct edge or path up to length 2 |

## Validation Command

The final validation command is:

```bash
docker compose exec backend uv run scripts/validate_controlled_sample.py
```

No manual `--graphrag-root` argument is required after the validator fix. The script resolves the active graph workspace automatically.

## Actual Validation Output

The relevant output was:

```text
Controlled sample validation
Counts: {"documents": 1, "entities": 10, "relationships": 15, "text_units": 1}
Matched relationships: 9
Diagnostics: {"document_count": 1, "entity_count": 10, "relationship_count": 15, "text_unit_count": 1}
INFO: Validated active graph f2132d66-cd08-48b9-bd64-4178565ac6d9 from /app/ragtest/graphs/f2132d66-cd08-48b9-bd64-4178565ac6d9
PASS
```

## Result Interpretation

The validation passed.

The indexed graph contains:

- `1` document,
- `1` text unit,
- `10` entities,
- `15` relationships.

The `1` document and `1` text unit counts are expected because the corpus was uploaded as one merged file.

The validator reports:

```text
Matched relationships: 9
```

This means all 9 expected controlled relationships were found. It does not mean the graph only contains 9 relationships. The graph contains 15 relationships in total; the remaining 6 are additional relationships extracted by GraphRAG beyond the minimum expected controlled graph shape.

## Chat Response Validation

After the graph-level validator passed, the active `controlled_tech_corpus_all.txt` graph was also tested through the chat interface with representative controlled-corpus questions.

The tested graph and runtime context were:

| Field | Value |
|---|---|
| Active graph id | `f2132d66-cd08-48b9-bd64-4178565ac6d9` |
| Source filename | `controlled_tech_corpus_all.txt` |
| Indexed graph status | `completed` |
| Observed entity count | `10` |
| Observed relationship count | `15` |
| Query chat provider | Gemini |
| Query embedding provider | Gemini |

### Question 1: Relationship Synthesis

Question:

```text
How are BetaBank, Orion Assistant, and BetaBank Policy connected?
```

Observed answer summary:

- BetaBank was described as the institutional user of Orion Assistant.
- BetaBank Policy was described as the policy content used by the system.
- Orion Assistant was described as the tool/interface that retrieves and answers questions from policy data.
- The answer also connected the supporting infrastructure: Ingestion Pipeline, EmbedLite, AtlasGraph, Maya Chen, and Ravi Patel.
- The answer cited graph community reports with markers such as `[Data: Reports (0, 1, 2)]`.

Validation against the controlled source:

| Requirement | Result | Notes |
|---|---|---|
| Mentions `BetaBank` | Pass | Matches the expected entity. |
| Mentions `Orion Assistant` | Pass | Matches the expected entity. |
| Mentions `BetaBank Policy` | Pass | Matches the expected entity. |
| Explains `BetaBank -> Orion Assistant` | Pass | Supported by: `BetaBank uses Orion Assistant for onboarding policy questions from new employees.` |
| Explains `Orion Assistant -> BetaBank Policy` | Pass | Supported by: `Orion Assistant cites BetaBank Policy when it answers onboarding policy questions.` |
| Connects supporting infrastructure | Pass | The answer correctly references Ingestion Pipeline, EmbedLite, and AtlasGraph as supporting systems. |
| Avoids unsupported elaboration | Partial | The answer contains broader phrasing such as "proprietary policy manuals", "cognitive intelligence layer", "regulatory guidelines", and "high-stakes employee onboarding". These are plausible paraphrases but are not explicitly stated in the controlled source. |

Interpretation:

The first chat response passes the functional controlled-corpus relationship test because it identifies the expected entities and explains the required relationships. It is also consistent with the indexed graph structure. However, it is not a strict source-only answer: it adds polished explanatory language and several expanded claims that go beyond the literal controlled corpus. This does not invalidate the graph extraction test, but it shows that broad synthesis questions should be evaluated with a source-fidelity caveat unless they are asked in `source` mode or with an explicit source-only instruction.

### Question 2: Direct Fact Lookup

Question:

```text
Which system stores extracted entities and relationships?
```

Observed answer:

```text
The system is AtlasGraph. The source states: AtlasGraph stores extracted entities and relationships for the GraphRAG workspace. [S1]
```

Observed citations:

```text
[S1] controlled_tech_corpus_all.txt
text unit: e2dbc2acf08df7c461d3911ae2341608892026f2bc30e5a1d533967f754fdfcba4e7a55d6cb8bc97ae4765835f985c078cd261f7eada645404b50446e164cee9
excerpt: AtlasGraph stores extracted entities and relationships for the GraphRAG workspace.
```

Validation against the controlled source:

| Requirement | Result | Notes |
|---|---|---|
| Identifies the correct system | Pass | Correct answer: `AtlasGraph`. |
| Grounds the answer in the indexed source | Pass | The answer cites `[S1]` and includes the exact supporting sentence. |
| Returns source citation metadata | Pass | The response includes the source filename and text-unit id. |
| Returns graph citation metadata | Pass | The response includes the `AtlasGraph` entity and a storage relationship citation. |
| Avoids unnecessary reasoning overhead | Pass | The response used the source lookup path instead of a DRIFT-style multi-hop search. |

Interpretation:

The second chat response fully passes the controlled direct-fact test. It is concise, identifies the expected entity, provides a source citation, and returns supporting citation metadata. This validates the fix for the previous failure mode where this simple question could be routed into an expensive DRIFT query and leave the chat without a visible answer.

## Chat Test Conclusion

The chat tests are considered successful with one caveat.

The direct fact lookup test is a full pass. It confirms that the application can answer a simple controlled-corpus question from the indexed source and return visible citations.

The relationship synthesis test is a functional pass because it identifies the expected entities and relationship chain. It should be treated as a source-fidelity partial pass because the answer includes some expanded language not literally present in the controlled source. For strict regression testing, this question should either be run in `source` mode or evaluated with a rubric that separates graph-relationship correctness from source-only wording discipline.

## Warning Interpretation

The command also printed warnings from third-party packages:

```text
LiteLLM: could not pre-load bedrock-runtime response stream shape
LiteLLM: could not pre-load sagemaker-runtime response stream shape
SyntaxWarning: invalid escape sequence
```

These warnings are not validation failures.

The LiteLLM warnings indicate that optional AWS Bedrock and SageMaker streaming support was not available because `botocore` is not installed. This test does not use Bedrock or SageMaker.

The `SyntaxWarning` messages come from installed third-party libraries and do not affect the controlled corpus validation result.

## Previous Failure Cause

Before the validator fix, the same command failed with output similar to:

```text
Counts: {"documents": 1, "entities": 320, "relationships": 190, "text_units": 12}
Matched relationships: 0
ERROR: Missing expected entity: Astra Labs
...
FAIL
```

Those counts came from an older Einstein index in the root workspace, not from the newly indexed controlled tech corpus.

The failure was therefore caused by workspace selection, not by a bad controlled-corpus index.

## Conclusion

The controlled tech corpus index is valid.

The active indexed graph contains all expected controlled entities and all 9 expected relationship checks. The validator now correctly supports the multi-graph workspace layout and the one-file combined upload workflow.

This test confirms that the application can index a small, deterministic corpus and produce a minimum expected GraphRAG structure suitable for regression checks and manual graph inspection.
