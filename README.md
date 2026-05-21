# GraphRAG Knowledge Graph Assistant

Ez a projekt egy teljes, lokálisan is futtatható GraphRAG alkalmazás. Szöveges dokumentumokból tudásgráfot épít, a gráfot vizualizálja, majd természetes nyelvű kérdésekre válaszol a Microsoft GraphRAG keresési módjaival.

A rendszer nem kötődik egyetlen témához: bármilyen UTF-8 kódolású `.txt` forrásszöveggel használható dokumentum-alapú tudásgráf asszisztensként.

## Fő képességek

- Dokumentumfeltöltés és háttérben futó GraphRAG indexelés.
- Entitások, kapcsolatok, közösségek és szövegegységek előállítása GraphRAG-gel.
- Interaktív React Flow gráfnézet fő komponens, összekapcsolt nézet és teljes nézet szűrőkkel.
- Chat felület beszélgetéslistával, üzenetelőzményekkel és kattintható forrás-entitásokkal.
- `auto`, `local`, `global`, `drift`, `source` és `hybrid` keresési módok.
- Könnyű automatikus routing: az `auto` mód a kérdés alapján választ local, global, DRIFT, source vagy hybrid keresést.
- Lokális Ollama alapértelmezés, opcionális Gemini és OpenRouter provider támogatással.
- Külön konfigurálható indexelési chat provider, indexelési embedding provider, lekérdezési chat provider és lekérdezési embedding provider.
- Indexelési folyamatjelzés százalékkal, chunk állapottal és hibaüzenetekkel.
- Graph diagnosztika: entitás- és kapcsolat-számok, izolált node-ok, provider konfiguráció és figyelmeztetések.

## Technológiai stack

Backend:

- Python 3.12
- FastAPI
- SQLAlchemy Core
- PostgreSQL
- Microsoft GraphRAG
- pandas / parquet GraphRAG output olvasáshoz
- uv csomagkezelés

Frontend:

- React 19
- TypeScript
- Vite
- Tailwind CSS
- SWR
- React Flow
- lucide-react ikonok

Infrastruktúra:

- Docker Compose
- opcionális natív vagy konténeres Ollama
- FastAPI által kiszolgált frontend build production módban

## Projekt felépítése

```text
.
├── docker-compose.yml
├── README.md
├── docs/
│   └── graphrag-optimization.md
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── api/
│   │   │   ├── chat.py
│   │   │   ├── graph.py
│   │   │   └── index.py
│   │   ├── schemas/
│   │   └── services/
│   │       ├── chat.py
│   │       └── graphrag.py
│   ├── scripts/
│   │   ├── init_db.py
│   │   └── init_graphrag.py
│   └── ragtest/
│       ├── input/
│       ├── output/
│       └── cache/
└── frontend/
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── app/
        ├── pages/
        ├── widgets/
        ├── features/
        ├── entities/
        └── shared/
```

## Gyors indítás Docker Compose-zal

Előfeltételek:

- Docker és Docker Compose
- PostgreSQL porthoz szabad `5432`, vagy átírt `APP_PG_PORT`
- Ollama, ha lokális modellt használsz
- legalább 8 GB RAM kisebb lokális modellekhez

1. Környezeti fájl létrehozása:

```bash
cp .env.example .env
```

2. GraphRAG munkakönyvtár biztosítása:

```bash
mkdir -p backend/ragtest/input backend/ragtest/output backend/ragtest/cache
```

3. Ollama lokális használata esetén indítsd el az Ollama szervert a host gépen:

```bash
ollama serve
ollama pull qwen2.5:3b
ollama pull nomic-embed-text
```

Apple Silicon gépen ez az ajánlott mód, mert a natív Ollama használni tudja a Metal gyorsítást. A Docker Compose alapértelmezett `APP_OLLAMA_BASE_URL` értéke ezért `http://host.docker.internal:11434`.

4. Konténerek indítása:

```bash
docker compose up -d --build
```

5. Logok követése:

```bash
docker compose logs -f backend
```

Az alkalmazás production módban egyetlen porton érhető el:

- App: http://localhost:8000
- OpenAPI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health
- Graph diagnosztika: http://localhost:8000/api/graph/diagnostics

A backend induláskor létrehozza a szükséges adatbázistáblákat, a Docker image pedig induláskor inicializálja a GraphRAG workspace konfigurációt.

## Konténeres Ollama

Ha nem natív Ollama-t szeretnél használni, a compose fájl tartalmaz egy opcionális `container-ollama` profilt:

```bash
docker compose --profile container-ollama up -d --build
```

Ebben az esetben állítsd az Ollama címet a konténeres szolgáltatásra:

```env
APP_OLLAMA_BASE_URL=http://ollama:11434
```

## Lokális fejlesztés Docker nélkül

Backend:

```bash
cd backend
cp .env.example .env.local
uv sync
uv run scripts/init_graphrag.py
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

PostgreSQL indítható külön Docker konténerben:

```bash
docker run -d \
  --name graphrag-postgres \
  -p 5432:5432 \
  -e POSTGRES_USER=graphrag_user \
  -e POSTGRES_PASSWORD=graphrag_pass123 \
  -e POSTGRES_DB=graphrag_db \
  postgres:17-alpine
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Fejlesztés közben:

- frontend: http://localhost:3000
- backend API: http://localhost:8000

A Vite dev server a `/api` kéréseket a backend felé proxyzza.

## Fontos konfigurációk

Alapértelmezésben minden provider Ollama:

```env
APP_MODEL_PROVIDER=ollama
APP_OLLAMA_BASE_URL=http://host.docker.internal:11434
APP_OLLAMA_LLM_MODEL=qwen2.5:3b
APP_OLLAMA_EMBED_MODEL=nomic-embed-text
```

Finomhangolt provider szétválasztás:

```env
APP_INDEX_CHAT_PROVIDER=ollama
APP_INDEX_EMBED_PROVIDER=ollama
APP_QUERY_CHAT_PROVIDER=ollama
APP_QUERY_EMBED_PROVIDER=ollama
```

Gemini példa:

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

Gemini indexelés és query chat Ollama embeddinggel:

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

A GraphRAG indexelés sok LLM hívást indíthat, ezért a napi `500 RPD` limit mellett a
backend indexelés előtt becsült napi keretet foglal. Ha a dokumentum nem fér bele,
az indexelést leállítja, mielőtt Gemini hívás indulna.

A Gemini embedding free tier külön limitált (`100 RPM`, `30k TPM`, `1000 RPD`).
A backend ezért az embedding workflow-ra külön guardot használ. A Gemini
`batchEmbedContents` quota a batchben lévő elemeket is számolja, ezért a GraphRAG
embedding batch hívások ütemezése szándékosan a publikus RPM limit alatt marad.

A projekt Gemini embedding defaultja `gemini-embedding-2`. A meglévő
`gemini-embedding-001` indexekkel nem kompatibilis, ezért váltáskor az index és
query embedding modellt együtt kell átállítani, majd teljesen újra kell indexelni.

OpenRouter chat Ollama embeddinggel:

```env
APP_INDEX_CHAT_PROVIDER=openrouter
APP_INDEX_EMBED_PROVIDER=ollama
APP_QUERY_CHAT_PROVIDER=openrouter
APP_QUERY_EMBED_PROVIDER=ollama
APP_OPENROUTER_API_KEY=your-key
APP_OPENROUTER_LLM_MODEL=openai/gpt-4.1-mini
```

Fontos: a lekérdezési embedding providernek és modellnek egyeznie kell az indexeléskor használt embedding providerrel és modellel. Ha eltérnek, az entitás-visszakeresés pontatlan lehet, és a `/api/graph/diagnostics` figyelmeztetést ad.

GraphRAG indexelési beállítások:

```env
APP_GRAPHRAG_CONCURRENT_REQUESTS=1
APP_GRAPHRAG_MAX_RETRIES=8
APP_GRAPHRAG_MAX_RETRY_WAIT=60.0
APP_GRAPHRAG_INDEX_TIMEOUT_SECONDS=7200
APP_GRAPHRAG_REQUEST_TIMEOUT=600.0
APP_GRAPHRAG_CHUNK_SIZE=1000
APP_GRAPHRAG_CHUNK_OVERLAP=150
APP_GRAPHRAG_CLAIM_EXTRACTION_ENABLED=false
APP_GEMINI_FREE_TIER_EMBED_BATCH_SIZE=16
APP_GEMINI_FREE_TIER_EMBED_BATCH_MAX_TOKENS=8191
```

Részletes provider- és query-mode javaslatok: [docs/graphrag-optimization.md](docs/graphrag-optimization.md).

## Használat

1. Nyisd meg az alkalmazást: http://localhost:8000
2. Hozz létre vagy válassz ki egy beszélgetést.
3. Tölts fel egy `.txt` fájlt az `Upload Document` gombbal.
4. Várd meg az indexelés végét.
5. Kérdezz a dokumentum tartalmáról.
6. Nyisd meg a `Graph view` nézetet a tudásgráf bejárásához.

A feltöltés csak `.txt` fájlokat fogad, legfeljebb 10 MB méretig. A GraphRAG indexelés hosszú ideig is futhat, különösen lokális modellekkel vagy nagy dokumentumokkal.

## Keresési módok

- `Auto`: egyszerű routing alapján választ módot.
- `Local`: konkrét entitásokra, tényekre és dokumentumrészletekre jó.
- `Global`: teljes korpuszra vonatkozó összefoglalókhoz, témákhoz és mintázatokhoz jó.
- `DRIFT`: több entitást, kapcsolatot, ok-okozatot vagy összehasonlítást érintő kérdésekhez jó.
- `Source`: forráshű kivonatoláshoz jó, amikor csak a szövegben explicit szereplő kapcsolatokat szabad említeni.

A chat válasza eltárolja a ténylegesen használt módot és a routing indoklását is.

## API végpontok

Chat:

- `POST /api/chat/conversations`
- `GET /api/chat/conversations`
- `GET /api/chat/conversations/{conversation_id}/messages`
- `POST /api/chat/conversations/{conversation_id}/query`
- `DELETE /api/chat/conversations/{conversation_id}`

Indexelés:

- `POST /api/index/upload`
- `GET /api/index/progress/{document_id}`
- `GET /api/index/status`

Gráf:

- `GET /api/graph/full`
- `GET /api/graph/stats`
- `GET /api/graph/diagnostics`

Példa kérdezés API-ból:

```bash
curl -X POST "http://localhost:8000/api/chat/conversations/{conversation_id}/query" \
  -H "Content-Type: application/json" \
  -d '{"question":"Give me an overview of the document","search_mode":"auto"}'
```

Példa dokumentumfeltöltés:

```bash
curl -X POST "http://localhost:8000/api/index/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@./example.txt"
```

## Újraindexelés

Indexeld újra a dokumentumokat, ha ezek bármelyike változik:

- embedding provider vagy embedding modell
- chunk size vagy chunk overlap
- entitástípusok
- GraphRAG extraction beállítások
- community report beállítások
- cluster graph beállítások

Csak a query chat provider változtatása általában nem igényel újraindexelést.

Egyszerű reset fejlesztés közben:

```bash
docker compose down
docker compose up -d --build
```

Docker volume reset:

```bash
docker compose down -v
```

Ez törli a PostgreSQL és az Ollama Docker volume-okat. A hostról bind mountolt GraphRAG workspace (`backend/ragtest`) ettől még megmaradhat, ezért fejlesztés közbeni teljes újraindexelésnél ellenőrizd külön a `backend/ragtest/input` és `backend/ragtest/output` tartalmát.

## Tesztek és ellenőrzés

Backend tesztek:

```bash
cd backend
uv run pytest
```

Frontend build:

```bash
cd frontend
npm run build
```

Backend lint:

```bash
cd backend
uv run ruff check .
```

Frontend lint:

```bash
cd frontend
npm run lint
```

## Hibakeresés

Ollama elérés ellenőrzése host gépen:

```bash
ollama list
curl http://localhost:11434/api/tags
```

Ollama elérés ellenőrzése backend konténerből:

```bash
docker compose exec backend python -c "import httpx; print(httpx.get('http://host.docker.internal:11434/api/tags').json())"
```

Backend logok:

```bash
docker compose logs -f backend
```

PostgreSQL logok:

```bash
docker compose logs -f postgres
```

GraphRAG output és indexelési napló:

```text
backend/ragtest/output/
backend/ragtest/output/indexing-engine.log
```

Ha az indexelés túl lassú vagy timeoutol, csökkentsd az `APP_GRAPHRAG_CHUNK_SIZE` értékét, növeld az `APP_GRAPHRAG_REQUEST_TIMEOUT` értékét, vagy használj gyorsabb cloud providert indexeléshez.

## Dokumentum-előkészítési javaslatok

- Használj tiszta, UTF-8 kódolású `.txt` fájlokat.
- Távolítsd el az ismétlődő fejléceket, lábléceket és zajos boilerplate részeket.
- Egy fájl egy jól körülhatárolt témát vagy forrásegységet tartalmazzon.
- Nagy korpuszt több kisebb, koherens fájlra érdemes bontani.
- Provider vagy embedding modell váltás után töltsd fel újra a forrásokat.
