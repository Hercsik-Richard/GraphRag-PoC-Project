# Controlled Tech Corpus

This is a small, hand-checkable English corpus for GraphRAG PoC validation. It is designed to make entity and relationship extraction easy to inspect without a large external document.

Expected key entities:

- Astra Labs
- Orion Assistant
- Maya Chen
- AtlasGraph
- Ravi Patel
- Ingestion Pipeline
- EmbedLite
- BetaBank
- BetaBank Policy

Expected visible relationships:

- Astra Labs builds Orion Assistant.
- Maya Chen is lead architect of Orion Assistant.
- Orion Assistant uses AtlasGraph.
- Ravi Patel maintains the ingestion pipeline.
- EmbedLite creates embeddings for BetaBank Policy and indexed policy documents.
- AtlasGraph stores extracted entities and relationships.
- BetaBank uses Orion Assistant for onboarding policy questions.
- Orion Assistant cites BetaBank Policy.
- Maya Chen asks Ravi Patel to verify the AtlasGraph relationship for BetaBank.

Useful demo questions:

- Who builds Orion Assistant?
- How are BetaBank, Orion Assistant, and BetaBank Policy connected?
- Which system stores extracted entities and relationships?
- Based on the indexed source, which policy document does Orion Assistant cite?
- Explain how Maya Chen and Ravi Patel are connected to AtlasGraph and BetaBank.

After indexing these files, run:

```bash
uv run scripts/validate_controlled_sample.py
```
