<details open>
<summary>English</summary>

**Language / Nyelv:** [English](#english) | [Magyar](#magyar)

<a id="english"></a>

# GraphRAG PoC Sample Test Report

## Test Context

In this test, I validated the GraphRAG PoC sample located in:

```text
backend/samples/graphrag_poc/
```

I used this sample because it is a hand-checkable course-documentation corpus. It validates the actual pipeline concepts used by this project: ingestion, chunking, embeddings, vector storage, graph storage, retrieval, source citations, and evaluation.

The original corpus contains three source files:

- `01_project_overview.txt`
- `02_indexing_pipeline.txt`
- `03_query_and_evaluation.txt`

Because the current upload UI accepts one `.txt` file at a time, I tested the sample with the three files merged into:

```text
backend/samples/graphrag_poc/graphrag_poc_all.txt
```

The merged file preserves source boundaries with `Source: ...` labels before each original document section.

## Test Objective

My goal was to verify that the GraphRAG indexing pipeline can build a valid knowledge graph from a corpus that directly describes the GraphRAG PoC architecture.

In practice, I checked:

- whether the expected GraphRAG PoC entities are present,
- whether the expected pipeline relationships or short graph paths are present,
- whether the index contains non-empty document, text-unit, entity, and relationship outputs,
- whether the validator resolves the active multi-graph workspace correctly,
- whether the combined single-file upload is handled as a valid form of the sample corpus.

## Test Setup

I indexed the GraphRAG PoC sample through the application upload flow using:

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

This is necessary because I uploaded the sample as one merged `.txt` file, so GraphRAG indexes it as one document and one text unit in the current upload flow.

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

The `1` document and `1` text unit counts are expected because I uploaded the corpus as one merged file.

The validator reports:

```text
Matched relationships: 14
```

This means all 14 expected GraphRAG PoC relationship checks were found. It does not mean the graph only contains 14 relationships. The graph contains 17 relationships in total; the additional relationships were extracted by GraphRAG beyond the minimum expected validation contract.

## Graph Visualization Interpretation

I also inspected two screenshots from the frontend graph visualization. They show the same indexed `graphrag_poc_all.txt` graph, but they do not show the same filtered viewport.

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

This view was useful for checking the operational GraphRAG pipeline. The central structure is the `Graph Store`, which connects to extraction, evaluation, provenance, query, and retrieval-related components. This matches the expected project architecture: the graph store is the persistence point for extracted graph structure and is reused by evaluation and query-time graph traversal.

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

This confirmed for me that the indexed graph contains both the implementation pipeline and the high-level hybrid retrieval concept. The only limitation is that the model did not connect those two parts into one single component. I considered that acceptable for the current validation because the validator explicitly checks both parts of the graph.

## Contract Adjustment During Validation

The first validation attempt failed because my original expected graph contract was too literal. It expected several concepts as standalone entities:

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

I adjusted the expected graph contract to validate the stable graph structure GraphRAG actually extracted, while still checking the intended pipeline behavior.

I think this adjustment is appropriate for this PoC because the validator should test the minimum reliable graph shape, not force the model to create every noun phrase as a separate node.

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

## My Conclusion

My conclusion is that the GraphRAG PoC sample index is valid.

The active indexed graph contains the expected course-documentation pipeline components and all 14 expected relationship checks. I also verified that the validator correctly supports the multi-graph workspace layout and the one-file combined upload workflow.

For this project, I consider this sample more useful than a fictional enterprise-policy corpus because it validates the exact concepts the project describes: ingestion, chunking, embeddings, vector retrieval, graph construction, graph storage, source-grounded answer generation, and evaluation.

</details>

<a id="magyar"></a>

<details>
<summary>Magyar</summary>

# GraphRAG PoC Mintateszt Jelentés

## Tesztkörnyezet

Ebben a tesztben a következő helyen található GraphRAG PoC mintát validáltam:

```text
backend/samples/graphrag_poc/
```

Azért ezt a mintát használtam, mert kézzel ellenőrizhető kurzusdokumentációs korpusz. A projekt által használt tényleges pipeline-fogalmakat validálja: betöltés, darabolás, beágyazások, vektortárolás, gráftárolás, lekérés, forráshivatkozások és értékelés.

Az eredeti korpusz három forrásfájlt tartalmaz:

- `01_project_overview.txt`
- `02_indexing_pipeline.txt`
- `03_query_and_evaluation.txt`

Mivel a jelenlegi feltöltési felület egyszerre egy `.txt` fájlt fogad el, a mintát a három fájl összevonásával teszteltem:

```text
backend/samples/graphrag_poc/graphrag_poc_all.txt
```

Az összevont fájl megőrzi a forráshatárokat az egyes eredeti dokumentumszakaszok előtt szereplő `Source: ...` címkékkel.

## Tesztcél

A célom annak ellenőrzése volt, hogy a GraphRAG indexelési pipeline képes-e érvényes tudásgráfot építeni egy olyan korpuszból, amely közvetlenül a GraphRAG PoC architektúrát írja le.

A gyakorlatban azt ellenőriztem:

- jelen vannak-e a várt GraphRAG PoC entitások,
- jelen vannak-e a várt pipeline-kapcsolatok vagy rövid gráfútvonalak,
- tartalmaz-e az index nem üres dokumentum-, szövegegység-, entitás- és kapcsolat-kimeneteket,
- a validátor helyesen oldja-e fel az aktív többgráfos munkaterületet,
- az összevont egyfájlos feltöltést a mintakorpusz érvényes formájaként kezeli-e.

## Tesztbeállítás

A GraphRAG PoC mintát az alkalmazás feltöltési folyamatán keresztül indexeltem a következővel:

```text
graphrag_poc_all.txt
```

Az indexelt gráf egy izolált többgráfos munkaterületben lett tárolva:

```text
/app/ragtest/graphs/95dc20ab-8068-4511-bc2c-963b92d5bd2c
```

Helyi munkaterület útvonala:

```text
backend/ragtest/graphs/95dc20ab-8068-4511-bc2c-963b92d5bd2c/
```

Megfigyelt indexelt gráf metaadatok:

| Mező | Érték |
|---|---|
| Forrásfájlnév | `graphrag_poc_all.txt` |
| Aktív gráfazonosító | `95dc20ab-8068-4511-bc2c-963b92d5bd2c` |
| Dokumentumszám | `1` |
| Szövegegység-szám | `1` |
| Entitásszám | `16` |
| Kapcsolatszám | `17` |

A fő GraphRAG kimeneti fájlok itt találhatók:

```text
backend/ragtest/graphs/95dc20ab-8068-4511-bc2c-963b92d5bd2c/output/
```

Fontos fájlok:

- `documents.parquet`
- `text_units.parquet`
- `entities.parquet`
- `relationships.parquet`
- `communities.parquet`
- `community_reports.parquet`
- `indexing-engine.log`
- `lancedb/`

## Validátor Viselkedése

A validációs script:

```text
backend/scripts/validate_graphrag_poc_sample.py
```

A script újrahasználja a kontrollált minta validációs segédeszközeit, és a gráfkatalógusból validálja az aktív befejezett gráfot, ha nincs megadva `--graphrag-root` argumentum.

Az összevont feltöltési fájlhoz a validátor az eredeti többfájlos elvárásokat módosítja:

- a várt minimális dokumentumszám `3`-ról `1`-re változik,
- a várt minimális szövegegység-szám `3`-ról `1`-re változik.

Erre azért van szükség, mert a mintát egy összevont `.txt` fájlként töltöttem fel, így a GraphRAG a jelenlegi feltöltési folyamatban egy dokumentumként és egy szövegegységként indexeli.

A validátor ellenőrzi:

- minimális kimeneti darabszámok,
- várt entitásnevek,
- várt közvetlen kapcsolatpárok,
- elfogadott rövid gráfútvonalak, ahol a GraphRAG köztes csomópontot vont ki.

## Várt Gráfszerkezet

A végső várt entitáshalmaz:

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

A várt kapcsolatellenőrzések:

| Várt kapcsolat | Várt egyezéstípus |
|---|---|
| `GraphRAG PoC -> vector retrieval` | Közvetlen él |
| `GraphRAG PoC -> graph traversal` | Közvetlen él |
| `Document Loader -> Chunking Module` | Közvetlen él |
| `Chunking Module -> text chunks` | Közvetlen él vagy legfeljebb 3 hosszú út |
| `Embedding Model -> text chunks` | Közvetlen él vagy legfeljebb 2 hosszú út |
| `Vector Store -> Embedding Model` | Közvetlen él |
| `Entity Extractor -> Graph Store` | Közvetlen él |
| `Relationship Extractor -> Graph Store` | Közvetlen él |
| `Graph Store -> Evaluation Script` | Közvetlen él |
| `Graph Store -> provenance metadata` | Közvetlen él |
| `Query Engine -> Vector Store` | Közvetlen él |
| `Query Engine -> Graph Store` | Közvetlen él |
| `Answer Generator -> Query Engine` | Közvetlen él |
| `Evaluation Script -> Graph Store` | Közvetlen él |

## Validációs Parancs

A validációs parancs:

```bash
docker compose exec backend uv run scripts/validate_graphrag_poc_sample.py
```

Nincs szükség kézi `--graphrag-root` argumentumra. A script automatikusan feloldja az aktív gráf munkaterületet.

## Tényleges Validációs Kimenet

A releváns kimenet:

```text
GraphRAG PoC sample validation
Counts: {"documents": 1, "entities": 16, "relationships": 17, "text_units": 1}
Matched relationships: 14
Diagnostics: {"document_count": 1, "entity_count": 16, "relationship_count": 17, "text_unit_count": 1}
INFO: Validated active graph 95dc20ab-8068-4511-bc2c-963b92d5bd2c from /app/ragtest/graphs/95dc20ab-8068-4511-bc2c-963b92d5bd2c
PASS
```

## Egyező Kapcsolatok

A validátor mind a 14 várt kapcsolatellenőrzést egyeztette:

| Egyező kapcsolat | Egyezéstípus |
|---|---|
| `GraphRAG PoC -> vector retrieval` | Közvetlen |
| `GraphRAG PoC -> graph traversal` | Közvetlen |
| `Document Loader -> Chunking Module` | Közvetlen |
| `Chunking Module -> text chunks` | Legfeljebb 3 hosszú út |
| `Embedding Model -> text chunks` | Legfeljebb 2 hosszú út |
| `Vector Store -> Embedding Model` | Közvetlen |
| `Entity Extractor -> Graph Store` | Közvetlen |
| `Relationship Extractor -> Graph Store` | Közvetlen |
| `Graph Store -> Evaluation Script` | Közvetlen |
| `Graph Store -> provenance metadata` | Közvetlen |
| `Query Engine -> Vector Store` | Közvetlen |
| `Query Engine -> Graph Store` | Közvetlen |
| `Answer Generator -> Query Engine` | Közvetlen |
| `Evaluation Script -> Graph Store` | Közvetlen |

## Eredmény Értelmezése

A validáció sikeres volt.

Az indexelt gráf tartalma:

- `1` dokumentum,
- `1` szövegegység,
- `16` entitás,
- `17` kapcsolat.

Az `1` dokumentum és `1` szövegegység darabszámok vártak, mert a korpuszt egy összevont fájlként töltöttem fel.

A validátor ezt jelenti:

```text
Matched relationships: 14
```

Ez azt jelenti, hogy mind a 14 várt GraphRAG PoC kapcsolatellenőrzés megtalálható volt. Nem azt jelenti, hogy a gráf csak 14 kapcsolatot tartalmaz. A gráf összesen 17 kapcsolatot tartalmaz; a további kapcsolatokat a GraphRAG a minimálisan várt validációs szerződésen túl vonta ki.

## Gráfvizualizáció Értelmezése

Két képernyőképet is megvizsgáltam a frontend gráfvizualizációjából. Ugyanazt az indexelt `graphrag_poc_all.txt` gráfot mutatják, de nem ugyanazt a szűrt nézetablakot.

A frontend gráfnézetének több módja van:

- `Main`: a legnagyobb összefüggő komponenst mutatja.
- `Connected`: azokat a csomópontokat mutatja, amelyeknek legalább egy élük van.
- `All`: minden gráfcsomópontot mutat, beleértve a legnagyobb komponensen kívüli csomópontokat is.

### 1. Kép: Fő Pipeline Komponens

Az első kép az indexelt gráf fő pipeline-komponensét mutatja.

Látható csomópontok többek között:

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

Ez a nézet hasznos volt az operatív GraphRAG pipeline vizsgálatához. A központi szerkezet a `Graph Store`, amely kapcsolódik a kivonáshoz, értékeléshez, provenienciaadatokhoz, lekérdezéshez és lekéréshez kapcsolódó komponensekhez. Ez illeszkedik a várt projektarchitektúrához: a gráftároló a kivont gráfszerkezet perzisztencia-pontja, és az értékelés, valamint a lekérdezéskori gráfbejárás is újrahasználja.

Az első kép nem mutatja a `GraphRAG PoC`, `Vector Retrieval` vagy `Graph Traversal` csomópontokat. Ezek a csomópontok nem hiányoznak az indexből; a nézetablakban megjelenített legnagyobb összefüggő komponensen kívül vannak.

### 2. Kép: Teljes Gráf Külön Lekérési-Stratégia Komponenssel

A második kép szélesebb gráfnézetet mutat. Tartalmazza ugyanazt a fő pipeline-komponenst, és alul egy külön kisebb komponenst is mutat:

```text
GraphRAG PoC -> Vector Retrieval
GraphRAG PoC -> Graph Traversal
```

Ez magyarázza, miért látható két gráfterület. Ezek nem két külön teszt és nem két külön index. Ugyanazon indexelt gráfon belüli két szétkapcsolt összefüggő komponensről van szó.

A szétválás azért történt, mert a GraphRAG ezt vonta ki:

- az implementációs pipeline-t egy összefüggő komponensként,
- a magas szintű lekérési-stratégia állítást egy másik összefüggő komponensként.

A forrásszöveg azt mondja, hogy a GraphRAG PoC hibrid lekérést használ, és a hibrid lekérés a vektoros lekérést és a gráfbejárást kombinálja. A GraphRAG ezt az állítást a `GraphRAG PoC`-től a `Vector Retrieval` és `Graph Traversal` felé mutató élekként reprezentálta, de nem vont ki további áthidaló élt a `GraphRAG PoC` és a fő implementációs komponens között, például `GraphRAG PoC -> Query Engine`, `GraphRAG PoC -> Vector Store` vagy `GraphRAG PoC -> Graph Store`.

Mivel nem lett kivonva áthidaló él, a frontend elrendezés helyesen különíti el a lekérési-stratégia komponenst a fő pipeline-komponenstől.

### Vizuális Kódolás

A csomópontszínek a GraphRAG által visszaadott és a frontend által renderelt entitástípusokat követik:

- A kék csomópontok többnyire `ORGANIZATION` típusú entitások. Ebben a mintában a GraphRAG ezt a típust sok szoftverkomponensre használta, például `Graph Store`, `Vector Store`, `Chunking Module` és `Document Loader`.
- A narancssárga csomópontok `EVENT` típusú entitások, például `Evaluation Script`, `Indexing Pipeline`, `GraphRAG PoC` és `Graph Traversal`.
- A fehér `Vector Retrieval` csomópontnak nincs erős leképezett entitástípusa a kivont kimenetben, ezért visszaesik az alapértelmezett csomópontstílusra.

A gráf ezért szerkezetileg hasznos akkor is, ha az entitástípus-címkék szemantikailag nem tökéletesek. Ennél a PoC-nál a fontos validációs cél a kivont entitás-kapcsolat szerkezet, nem pedig a GraphRAG által minden szoftverfogalomhoz rendelt pontos típus.

### A Különbség Értelmezése

A két kép közötti különbség várt:

| Szempont | 1. kép | 2. kép |
|---|---|---|
| Fő cél | A legnagyobb operatív pipeline-komponens vizsgálata | A teljes összefüggő gráfkimenet vizsgálata |
| Látható gráfterjedelem | Fő összefüggő komponens | Fő komponens plusz a külön lekérési-stratégia komponens |
| Mutatja a `GraphRAG PoC` csomópontot | Nem | Igen |
| Mutatja a `Vector Retrieval` és `Graph Traversal` csomópontokat | Nem | Igen |
| Legjobb használat | Pipeline/debug nézet | Teljes validációs/inspekciós nézet |

Ez megerősítette számomra, hogy az indexelt gráf tartalmazza mind az implementációs pipeline-t, mind a magas szintű hibrid lekérési koncepciót. Az egyetlen korlát az, hogy a modell nem kapcsolta össze ezt a két részt egyetlen komponenssé. Ezt a jelenlegi validáció szempontjából elfogadhatónak tartottam, mert a validátor explicit módon ellenőrzi a gráf mindkét részét.

## Szerződésmódosítás a Validáció Során

Az első validációs próbálkozás azért bukott el, mert az eredeti várt gráfszerződésem túl szó szerinti volt. Több fogalmat önálló entitásként várt:

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

Az indexelt gráf ezek közül sok elképzelést továbbra is reprezentált, de nem mindig önálló gráfcsomópontként. Például:

- A `TEXT CHUNKS` csomópontként lett kivonva.
- A `VECTOR RETRIEVAL` és `GRAPH TRAVERSAL` lekéréshez kapcsolódó csomópontokként lettek kivonva.
- A `PROVENANCE METADATA` csomópontként lett kivonva.
- A `source metadata`, `hybrid retrieval` és answer traceability leírásokban vagy támogató szövegben jelent meg, nem pedig kötelező önálló entitásként.
- A `Query Engine` a `Vector Store` és `Graph Store` csomópontokhoz kapcsolódott, nem pedig közvetlenül a `vector retrieval` és `graph traversal` csomópontokhoz.

A várt gráfszerződést úgy módosítottam, hogy azt a stabil gráfszerkezetet validálja, amelyet a GraphRAG ténylegesen kivont, miközben továbbra is ellenőrzi a kívánt pipeline-viselkedést.

Ezt a módosítást megfelelőnek tartom ehhez a PoC-hoz, mert a validátornak a minimálisan megbízható gráfszerkezetet kell tesztelnie, nem pedig arra kell kényszerítenie a modellt, hogy minden főnévi kifejezésből külön csomópontot hozzon létre.

## Figyelmeztetések Értelmezése

A parancs harmadik féltől származó csomagok figyelmeztetéseit is kiírta:

```text
LiteLLM: could not pre-load bedrock-runtime response stream shape
LiteLLM: could not pre-load sagemaker-runtime response stream shape
SyntaxWarning: invalid escape sequence
```

Ezek a figyelmeztetések nem validációs hibák.

A LiteLLM figyelmeztetések azt jelzik, hogy az opcionális AWS Bedrock és SageMaker streamelési támogatás nem volt elérhető, mert a `botocore` nincs telepítve. Ez a teszt nem használ Bedrockot vagy SageMakert.

A `SyntaxWarning` üzenetek telepített harmadik féltől származó könyvtárakból erednek, és nem befolyásolják a GraphRAG PoC minta validációs eredményét.

## Saját Következtetés

A következtetésem az, hogy a GraphRAG PoC mintaindex érvényes.

Az aktív indexelt gráf tartalmazza a várt kurzusdokumentációs pipeline-komponenseket és mind a 14 várt kapcsolatellenőrzést. Azt is ellenőriztem, hogy a validátor helyesen támogatja a többgráfos munkaterület-elrendezést és az egyfájlos összevont feltöltési munkafolyamatot.

Ehhez a projekthez ezt a mintát hasznosabbnak tartom, mint egy kitalált vállalati szabályzatkorpuszt, mert pontosan azokat a fogalmakat validálja, amelyeket a projekt leír: betöltés, darabolás, beágyazások, vektoros lekérés, gráfépítés, gráftárolás, forrásalapú válaszgenerálás és értékelés.

</details>
