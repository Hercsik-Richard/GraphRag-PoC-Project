# GraphRAG Hybrid Source-Grounded Answering Plan

## Summary

Implement a public `hybrid` search mode that improves the GraphRAG indexed model based on the Third Test findings. The goal is to keep GraphRAG's strengths in source grounding and auditability while improving language compliance, claim-level citations, causal reasoning, and broad analytical synthesis.

## Key Changes

- Add public `hybrid` search mode across backend API, backend service types, frontend types, and UI mode selection.
- Add optional `retrieved_sources` support so answers can cite raw text-unit evidence separately from graph entities and relationships.
- Route broad source-bound analytical prompts to `hybrid` in Auto mode.
- Keep the existing `source` mode for the current specialized collaborator/disputant extraction flow.
- Add response-language handling so answers follow explicit language instructions, otherwise default to the query language.
- Add a conservative causal wording guard for unsupported strong claims such as "launched the Manhattan Project."

## Implementation Steps

1. Add `hybrid` to backend and frontend search mode types.
2. Add `retrieved_sources` to message storage, API schemas, service return values, and frontend message types.
3. Extend Auto routing so source-bound analytical prompts use `hybrid`, while collaborator/disputant extraction stays on `source`.
4. Add answer-language policy based on explicit prompt instructions first, then dominant query language.
5. Add generic raw source retrieval over `text_units.parquet` with dependency-free lexical scoring.
6. Implement Hybrid Search by combining Local graph context with ranked raw source excerpts.
7. Require `[S1]`, `[S2]` style source markers for major factual and causal claims in Hybrid answers.
8. Add a causal wording guard that repairs unsupported strong causal language.
9. Render raw source citations separately from entity and relationship citations in the frontend.
10. Document recommended source-grounded indexing settings.

## Test Plan

- Auto source-bound analytical prompts route to `hybrid`.
- Collaborator/disputant extraction still routes to `source`.
- Manual `hybrid` override works.
- `QueryRequestSchema(search_mode="hybrid")` validates.
- Old messages with `retrieved_sources = null` remain valid.
- Roosevelt/1939 and annus mirabilis queries rank relevant text units ahead of unrelated chunks.
- English prompts receive English answer instructions; Hungarian prompts receive Hungarian answer instructions.
- Unsupported strong causal wording is repaired to cautious wording.
- TypeScript build succeeds and `Hybrid` is selectable.
- Source citations render as `[S1]` and do not trigger graph navigation.

## Assumptions

- `hybrid` is a public API/UI mode.
- The existing specialized `source` extraction behavior remains backward compatible.
- The first implementation uses lexical text-unit retrieval, not embedding rerank.
- Database migration continues using the project's current `ALTER TABLE ADD COLUMN IF NOT EXISTS` pattern.
- Claim extraction remains optional documentation guidance, not a required default.
