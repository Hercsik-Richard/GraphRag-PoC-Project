# GraphRAG Query and Model Optimization

## Query Modes

`Auto` routes each question to one of three GraphRAG strategies:

- `Local`: best for specific entities, facts, and document details.
- `Global`: best for full-dataset summaries, themes, trends, and broad patterns.
- `DRIFT`: best for multi-hop questions, relationships between multiple actors, and "why/how are these connected" questions.
- `Source`: best for source-bound extraction where the answer must only use relationships explicitly stated in the uploaded text.
- `Hybrid`: best for source-bound analytical synthesis. It combines Local graph context with ranked raw text-unit excerpts and asks the model to cite major claims with `[S1]`, `[S2]`, etc.

Manual mode selection in the chat UI overrides the router. API clients can set `search_mode` to `auto`, `local`, `global`, `drift`, `source`, or `hybrid` on `POST /api/chat/conversations/{id}/query`.

## Provider Profiles

### Ollama Only

```env
APP_INDEX_CHAT_PROVIDER=ollama
APP_INDEX_EMBED_PROVIDER=ollama
APP_QUERY_CHAT_PROVIDER=ollama
APP_QUERY_EMBED_PROVIDER=ollama
APP_OLLAMA_BASE_URL=http://host.docker.internal:11434
APP_OLLAMA_LLM_MODEL=qwen2.5:3b
APP_OLLAMA_EMBED_MODEL=nomic-embed-text
```

This is the default profile and requires no cloud API key.

### Gemini

```env
APP_INDEX_CHAT_PROVIDER=gemini
APP_INDEX_EMBED_PROVIDER=gemini
APP_QUERY_CHAT_PROVIDER=gemini
APP_QUERY_EMBED_PROVIDER=gemini
APP_GEMINI_API_KEY=your-key
APP_GEMINI_LLM_MODEL=gemini-3.1-flash-lite
APP_GEMINI_EMBED_MODEL=gemini-embedding-2
APP_GEMINI_FREE_TIER_EMBED_GUARD_ENABLED=true
APP_GEMINI_FREE_TIER_EMBED_RPM=100
APP_GEMINI_FREE_TIER_EMBED_TPM=30000
APP_GEMINI_FREE_TIER_EMBED_RPD=1000
APP_GEMINI_FREE_TIER_EMBED_BATCH_SIZE=16
APP_GEMINI_FREE_TIER_EMBED_BATCH_MAX_TOKENS=8191
```

### Gemini Index And Query Chat With Ollama Embeddings

```env
APP_MODEL_PROVIDER=ollama
APP_INDEX_CHAT_PROVIDER=gemini
APP_INDEX_EMBED_PROVIDER=ollama
APP_QUERY_CHAT_PROVIDER=gemini
APP_QUERY_EMBED_PROVIDER=ollama
APP_OLLAMA_LLM_MODEL=qwen2.5:3b
APP_OLLAMA_EMBED_MODEL=nomic-embed-text
APP_GEMINI_API_KEY=your-key
APP_GEMINI_LLM_MODEL=gemini-3.1-flash-lite
APP_GEMINI_FREE_TIER_GUARD_ENABLED=true
APP_GEMINI_FREE_TIER_QUERY_RPM=7
APP_GEMINI_FREE_TIER_QUERY_TPM=120000
APP_GEMINI_FREE_TIER_QUERY_RPD=500
APP_GEMINI_FREE_TIER_INDEX_GUARD_ENABLED=true
APP_GEMINI_FREE_TIER_INDEX_RPM=7
APP_GEMINI_FREE_TIER_INDEX_TPM=120000
APP_GEMINI_FREE_TIER_INDEX_RPD=500
```

This keeps embeddings local while using Gemini 3.1 Flash-Lite for GraphRAG index-time
extraction and query-time answer generation. The runtime guards stay below the configured
15 RPM / 250k TPM / 500 RPD project limits, and index/query share the same daily counter.

When Gemini is used for embeddings, the embedding model has a separate free-tier quota:
100 RPM, 30k TPM, and 1000 RPD. GraphRAG calls Gemini embeddings through
`batchEmbedContents`, but the Gemini quota is charged against the embedded content items,
not just the outer batch request. The application therefore converts the public embedding
RPM into a conservative batch RPM before indexing.

The project uses `gemini-embedding-2` as the Gemini embedding default. Do not mix it
with an existing `gemini-embedding-001` index; the embedding spaces are incompatible,
so switching requires setting both index and query embedding model to
`gemini-embedding-2` and re-indexing all documents.

### OpenRouter Chat With Ollama Embeddings

```env
APP_INDEX_CHAT_PROVIDER=openrouter
APP_INDEX_EMBED_PROVIDER=ollama
APP_QUERY_CHAT_PROVIDER=openrouter
APP_QUERY_EMBED_PROVIDER=ollama
APP_OPENROUTER_API_KEY=your-key
APP_OPENROUTER_LLM_MODEL=openai/gpt-4.1-mini
APP_OPENROUTER_API_BASE=https://openrouter.ai/api/v1
```

OpenRouter embeddings are only safe when `APP_OPENROUTER_EMBED_MODEL` is known to work through OpenRouter's `/embeddings` endpoint. If the health check rejects it, use Gemini or Ollama embeddings.

### Cloud Index, Local Query

```env
APP_INDEX_CHAT_PROVIDER=gemini
APP_INDEX_EMBED_PROVIDER=ollama
APP_QUERY_CHAT_PROVIDER=ollama
APP_QUERY_EMBED_PROVIDER=ollama
APP_GEMINI_API_KEY=your-key
```

This uses a cloud LLM for indexing throughput while keeping query-time traffic local. The embedding provider and model still match across index and query.

## Reindexing Rules

Reindex after changing:

- `APP_INDEX_EMBED_PROVIDER` or `APP_*_EMBED_MODEL`
- chunk size or overlap
- entity type list
- extraction gleanings
- community report length/input length
- cluster graph max cluster size

Changing only the query chat provider does not require reindexing.

## Current Index Defaults

```env
APP_GRAPHRAG_CHUNK_SIZE=1000
APP_GRAPHRAG_CHUNK_OVERLAP=150
```

Graph extraction uses broader entity types: `person`, `organization`, `geo`, `event`, `concept`, `artifact`, `work`, and `technology`.

## Dataset Checklist

- Use plain `.txt` files with meaningful document boundaries.
- Remove boilerplate, duplicated headers, and unrelated footers.
- Keep source text in one language when possible.
- Split very large corpora into coherent files before upload.
- Reindex after provider/model or chunking changes.
- Check `GET /api/graph/diagnostics` after indexing for low relationship density, isolated nodes, and weak community structure.

## Source-Grounded Analytical Test Profile

For tests like the Einstein Wikipedia analysis, use `Hybrid` mode or let `Auto` route source-bound analytical prompts to `Hybrid`.

Recommended quality profile:

```env
APP_INDEX_CHAT_PROVIDER=gemini
APP_QUERY_CHAT_PROVIDER=gemini
APP_GRAPHRAG_CHUNK_SIZE=900
APP_GRAPHRAG_CHUNK_OVERLAP=200
```

Keep the index and query embedding provider/model identical. For quality experiments, enable:

```env
APP_GRAPHRAG_CLAIM_EXTRACTION_ENABLED=true
```

Claim extraction is intentionally optional because it increases indexing cost and should be evaluated per corpus.
