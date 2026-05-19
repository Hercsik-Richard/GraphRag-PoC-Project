# GraphRAG Query and Model Optimization

## Query Modes

`Auto` routes each question to one of three GraphRAG strategies:

- `Local`: best for specific entities, facts, and document details.
- `Global`: best for full-dataset summaries, themes, trends, and broad patterns.
- `DRIFT`: best for multi-hop questions, relationships between multiple actors, and "why/how are these connected" questions.

Manual mode selection in the chat UI overrides the router. API clients can set `search_mode` to `auto`, `local`, `global`, or `drift` on `POST /api/chat/conversations/{id}/query`.

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
APP_GEMINI_LLM_MODEL=gemini-2.5-flash-lite
APP_GEMINI_EMBED_MODEL=gemini-embedding-001
```

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
