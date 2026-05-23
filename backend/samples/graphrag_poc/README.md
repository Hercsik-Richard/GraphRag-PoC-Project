# Course Documentation GraphRAG PoC Sample

This is a small, hand-checkable English corpus for validating a GraphRAG proof of concept over course documentation. It focuses on the actual pipeline concepts used by the project: ingestion, chunking, embeddings, vector storage, graph storage, retrieval, citations, and evaluation.

Unlike a fictional enterprise-policy assistant sample, this corpus directly represents the pipeline discussed in the course documentation. It is meant to verify that the system can index information as a network of entities and relationships, not only as isolated text snippets.

Expected key entities:

- GraphRAG PoC
- Document Loader
- Chunking Module
- Indexing Pipeline
- Embedding Model
- Vector Store
- Entity Extractor
- Relationship Extractor
- Graph Store
- Query Engine
- Answer Generator
- Evaluation Script
- graph traversal
- text chunks
- provenance metadata
- vector retrieval

Expected visible relationships:

- GraphRAG PoC uses hybrid retrieval.
- Document Loader sends text to Chunking Module.
- Chunking Module creates text chunks.
- Embedding Model converts text chunks.
- Vector Store indexes embeddings.
- Entity Extractor identifies software components.
- Relationship Extractor creates graph edges.
- Graph Store saves entities and relationships.
- Graph Store stores provenance metadata.
- Query Engine uses vector retrieval.
- Query Engine uses graph traversal.
- Answer Generator receives source excerpts and graph context.
- Answer Generator cites source chunks.
- Evaluation Script compares the extracted graph with the expected reference graph.

The source text still covers source metadata, hybrid retrieval, source chunks, and answer traceability, but the validator only requires the concepts that GraphRAG consistently extracted as standalone graph nodes for this indexed sample.

Useful demo questions:

- Which component creates the text chunks?
- How does the system keep answers traceable to the original documents?
- Which components are involved in building the graph?
- How are the Entity Extractor, Relationship Extractor, and Graph Store connected?
- Why does the prototype use hybrid retrieval instead of only vector retrieval?
- Which part of the system validates the extracted graph?

For the current one-file upload flow, upload:

```text
backend/samples/graphrag_poc/graphrag_poc_all.txt
```

After indexing the sample, validate the active GraphRAG workspace:

```bash
uv run scripts/validate_graphrag_poc_sample.py
```

To run the opt-in integration test after indexing:

```bash
RUN_GRAPHRAG_POC_INTEGRATION=1 uv run pytest tests/test_graphrag_poc_sample_integration.py
```
