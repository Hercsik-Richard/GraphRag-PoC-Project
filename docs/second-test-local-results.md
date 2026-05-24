**Language / Nyelv:** [English](#english) | [Magyar](#magyar)

<a id="english"></a>

# Second-Test-Local-Results

## Test Setup

In this test, I evaluated the GraphRAG pipeline with the following setup:

- Indexing model: `qwen2.5:3b`
- Query model: `gemini-2.5-flash-lite`
- Query mode: `Local`
- Source document: indexed Albert Einstein Wikipedia article

My goal was to check whether the original broad evaluation prompt becomes more reliable if I split it into smaller Local-mode questions. I wanted to see whether focused questions improve retrieval quality and answer accuracy.

## Test Prompts

The original broad prompt had asked for a source-bound, chronological and causal analysis of Einstein's life, scientific work, and political-historical decisions.

Because Local mode is better suited to focused entity/relationship questions, I split the broad prompt into five smaller questions:

1. What are the key dated life events connecting Einstein from Ulm to Munich, Switzerland, Berlin, and the United States?
2. What does the source say about Einstein's 1905 annus mirabilis papers?
3. Why did Einstein receive the Nobel Prize, and why was it not for relativity?
4. How does the source connect the 1933 Nazi rise to power with Einstein's move to the United States?
5. What does the source say about Einstein's letter to Roosevelt?

## Result Summary

The results were mixed in a useful way.

The system answered the Nobel Prize question well, and it partially answered the broad life-route question, especially around the 1933 transition from Europe to the United States.

However, it failed on several questions where I expected the relevant information to exist in the underlying Wikipedia article. In particular, it claimed that there was no information about the 1905 annus mirabilis papers, the 1933 Nazi rise to power connection, and Einstein's letter to Roosevelt.

I interpret this as a retrieval failure, not as evidence that the source document lacks the information.

## Question-by-Question Analysis

### 1. Life Events From Ulm to the United States

The answer partly worked, but it was unfocused.

It retrieved useful information about Einstein's 1933 transition:

- He was in the United States in February 1933.
- He recognized that returning to Germany had become impossible after the Nazi rise to power.
- His Berlin apartment was raided.
- He learned of the Enabling Act.
- He and Elsa Einstein decided not to return to Berlin.
- He landed in Antwerp on March 28, 1933.
- He surrendered his passport and renounced German citizenship.
- He spent time in Belgium and England.
- He ultimately accepted the Institute for Advanced Study position in Princeton.

This is valuable and source-like.

However, the answer did not cleanly provide the requested full dated route:

```text
Ulm -> Munich -> Switzerland -> Berlin -> United States
```

Instead, the answer drifted into unrelated graph context, including:

- Oskar Halecki and Giuseppe Motta
- League of Nations committee politics
- Kurt Goedel
- Hebrew University of Jerusalem
- South America visits
- Harry Fosdick, Upton Sinclair, and Charlie Chaplin
- J. Robert Oppenheimer's 1965 memorial lecture

These are connected to Einstein in the graph, but they are not central to the question.

### 2. 1905 Annus Mirabilis Papers

This was a clear failure in my validation.

The system answered that the provided data did not contain information about Einstein's 1905 annus mirabilis papers. It only mentioned that Einstein published his first paper in 1901 and completed his doctoral dissertation in 1905.

This is incorrect as a source-level expectation: the Einstein Wikipedia article does contain the annus mirabilis topic. For me, this failure indicates that Local retrieval did not surface the relevant text or graph nodes.

The retrieved source list was also noisy, including unrelated entities such as:

- Juan Jorge Duclout and Mauricio Nirenstein
- Hebrew University of Jerusalem
- Alfred Einstein
- John Robert Oppenheimer
- Bohr
- Harry Fosdick, Upton Sinclair, and Charlie Chaplin
- League of Nations-related figures
- Einstein refrigerator
- Zurich
- Trenton

This suggests that the graph representation around Einstein is broad but poorly filtered for the actual question.

### 3. Nobel Prize and Relativity

This was the strongest answer in the whole Local-mode test.

The system correctly stated that Einstein received the 1921 Nobel Prize in Physics for his services to theoretical physics and especially for discovering the law of the photoelectric effect.

It also correctly explained why the prize was not awarded for relativity: relativity was still controversial and less directly settled for the Nobel committee, while the photoelectric effect was more experimentally grounded and important for quantum theory.

I think this question worked because it maps well to a concrete entity/relationship:

```text
Einstein -> Nobel Prize -> photoelectric effect
```

This is the kind of task where Local mode looked reliable.

### 4. 1933 Nazi Rise to Power and Move to the United States

This was a retrieval inconsistency.

The system answered that the provided text did not contain information about the 1933 Nazi rise to power or its connection to Einstein's move to the United States.

This contradicts the answer to question 1, where the system had already retrieved relevant 1933 information from `Sources (4)`.

This means the failure was not due to missing source data. The relevant source exists, but Local retrieval did not return it consistently for this phrasing of the question.

### 5. Einstein's Letter to Roosevelt

This also failed.

The system answered that the source material did not contain information about a letter from Einstein to Roosevelt.

I treat this as very likely a retrieval failure. The broader previous test had retrieved and used the Roosevelt-letter topic, and the Einstein article is expected to contain this event.

The retrieved context was again dominated by unrelated Einstein-adjacent graph elements rather than Roosevelt, Szilard, nuclear weapons, uranium, or the Manhattan Project.

## What Worked In My Check

Local mode worked when the question was tightly bound to a well-represented graph relationship.

The Nobel Prize question is the clearest example. The system found the relevant Nobel Prize context and answered accurately.

The 1933 migration story also appeared in one answer when the right source chunk was retrieved. This proves the underlying indexed data contains at least some relevant material.

The Gemini query model behaved relatively responsibly. When the retrieved context did not contain enough evidence, it often refused to answer instead of freely hallucinating. In a source-restricted test, I consider that better than inventing unsupported details.

## What Did Not Work In My Check

### Local Retrieval Recall Was Weak

The system failed to retrieve obvious source-relevant information for:

- annus mirabilis papers
- 1933 Nazi rise to power
- Roosevelt letter

These are not obscure details. Their absence from the answer indicates a retrieval problem.

### The Graph Was Noisy

The source lists repeatedly included many low-relevance or irrelevant graph nodes:

- `ALFRED EINSTEIN`
- `JUAN JORGE DUCLOUT AND MAURICIO NIRENSTEIN`
- `O.S. HALLECKI AND GIOVANNI MOTTARA`
- `HARRY FOSDICK AND UPTON SINCLAIR AND CHARLIE CHAPLIN`
- `ZOOELLNER FAMILY CONSERVATORY`
- `TRENTON`
- `EINSTEIN REFRIGERATOR`
- `HEBREW UNIVERSITY OF JERUSALEM`
- `UNESCO`
- `JOHN ROBERT OPPENHEIMER`

These may be present in the source article, but they are not useful for the tested questions.

### Some Relationships Were Overloaded

The `EINSTEIN -> ZURICH` relationship is especially problematic. It bundled many unrelated claims into one relationship, including religion, pacifism, violin playing, vegetarianism, Hebrew University, and Zurich meetings.

This kind of relationship reduces retrieval precision. A single high-weight relationship becomes semantically broad and can pollute many unrelated answers.

### The Indexing Model Likely Limited Graph Quality

The graph was created using `qwen2.5:3b`. The observed graph artifacts suggest that this model may be too weak for high-quality entity and relationship extraction from a complex biographical article.

Examples of graph quality issues:

- combined multi-person entities
- noisy or irrelevant relationships
- overloaded relationship descriptions
- weak representation of key events
- missing or under-retrieved topics such as annus mirabilis and Roosevelt letter

## Why the System Could Not Answer Some Questions

The system did not fail because Gemini could not answer. It failed because the Local-mode context often did not contain the necessary evidence.

When the model says:

```text
The provided source material does not contain this information.
```

it should be read more precisely as:

```text
The retrieved Local-mode context did not contain this information.
```

That is a major distinction.

The source article may contain the fact, but Local retrieval did not retrieve the right text unit, entity, report, or relationship.

## Main Diagnosis

My main conclusion is that the current pipeline is limited by retrieval quality and graph quality, not primarily by the query model.

The query model upgrade to `gemini-2.5-flash-lite` helped significantly. However, this test showed me that a strong query model cannot reliably answer source-grounded questions if the retrieved graph context is incomplete or noisy.

Local mode is not ideal for all five questions:

- It is good for direct entity relationships, such as Nobel Prize and photoelectric effect.
- It is weaker for source-span questions, such as "what does the article say about the Roosevelt letter?"
- It is weaker for historical chronology, such as Ulm -> Munich -> Switzerland -> Berlin -> United States.
- It is weaker for broad event synthesis, such as the 1933 Nazi rise and emigration story.

## My Follow-Up Conclusions

### 1. Re-index With a Stronger Indexing Model

Based on this run, the highest-impact improvement would be to re-index the article with a stronger model. I would start here before spending time on more query prompt changes.

The setup I would use next:

- Index chat model: `gemini-2.5-flash-lite` or another stronger model
- Query chat model: `gemini-2.5-flash-lite`
- Embedding model: keep a stable embedding model, but ensure index and query embedding models match

The current `qwen2.5:3b` index appears to produce a noisy graph.

### 2. Add a Source or Hybrid Retrieval Mode

For questions like annus mirabilis, 1933 emigration, and the Roosevelt letter, my test suggests that graph-local retrieval is not enough.

The strategy I would validate next is:

```text
Step 1: retrieve relevant raw text units
Step 2: retrieve local graph entities and relationships
Step 3: rerank evidence against the question
Step 4: answer only from the filtered evidence
```

This would combine the benefits of text retrieval and graph retrieval.

### 3. Improve Routing

The router should send different question types to different retrieval modes. In this test, the same Local strategy behaved very differently depending on the question wording:

| Question type | Best mode |
|---|---|
| Direct entity relationship | Local |
| "What does the source say about..." | Source |
| Chronological life path | Source or Global |
| Broad synthesis | Global or DRIFT |
| Multi-hop causal relation | DRIFT or Hybrid |
| Source-grounded factual evidence | Source + Local |

### 4. Rerank Retrieved Nodes

Before the final answer, retrieved nodes and relationships should be filtered by relevance to the user question. I saw too many technically connected but practically irrelevant nodes in the evidence context.

For example, a Roosevelt-letter question should prefer:

- Einstein
- Roosevelt
- Leo Szilard
- uranium
- nuclear weapons
- Manhattan Project
- 1939 letter

It should exclude:

- Alfred Einstein
- Hebrew University
- South America visit
- Charlie Chaplin
- Zurich violin/religion relationship
- Einstein refrigerator

### 5. Limit Displayed Sources

The frontend should not display every retrieved entity and relationship.

It should display only:

- sources actually used in the answer
- top-ranked relevant entities/relationships
- a small capped number, for example 5-8 sources

This would make the citation area more trustworthy and less noisy.

### 6. Validate Critical Test Facts

For this Einstein test, I would consider the system successful only if it can reliably retrieve and answer:

- 1905 annus mirabilis papers
- Nobel Prize reason
- 1933 Nazi rise to power and emigration
- Roosevelt letter
- Ulm -> Munich -> Switzerland -> Berlin -> United States route

If any of these cannot be retrieved, I would investigate the issue at the index/retrieval level first.

## My Final Conclusion

This second Local-mode test showed me that the GraphRAG system is partially working, but not yet reliable for broad historical-scientific synthesis.

The strongest result was the Nobel Prize question, where Local mode matched a clear entity relationship.

The weakest results were the annus mirabilis and Roosevelt-letter questions, where the system incorrectly claimed the source did not contain information. I see these failures as retrieval and graph-index quality problems.

My practical takeaway is that the most important next step is not another query-model upgrade. The query model is already good enough to expose the problem clearly. I would improve the indexed graph and add source/hybrid retrieval so that relevant text evidence is available before answer generation.


<a id="magyar"></a>

# Második Teszt - Local Eredmények

## Tesztbeállítás

Ebben a tesztben a GraphRAG pipeline-t a következő beállítással értékeltem:

- Indexelési modell: `qwen2.5:3b`
- Lekérdezési modell: `gemini-2.5-flash-lite`
- Lekérdezési mód: `Local`
- Forrásdokumentum: indexelt Albert Einstein Wikipédia-cikk

A célom az volt, hogy ellenőrizzem: az eredeti, széles értékelési prompt kisebb Local-módú kérdésekre bontása javítja-e a lekérési minőséget és a válasz pontosságát.

## Tesztpromptok

Az eredeti széles prompt forráshoz kötött, kronológiai és oksági elemzést kért Einstein életéről, tudományos munkájáról, valamint politikai-történelmi döntéseiről.

Mivel a Local mód jobban illik fókuszált entitás-/kapcsolatkérdésekhez, a széles promptot öt kisebb kérdésre bontottam:

1. Melyek azok a fő, dátummal ellátott életesemények, amelyek Einsteint Ulmtól Münchenen, Svájcon és Berlinen át az Egyesült Államokig kapcsolják össze?
2. Mit mond a forrás Einstein 1905-ös annus mirabilis cikkeiről?
3. Miért kapta Einstein a Nobel-díjat, és miért nem a relativitásért?
4. Hogyan kapcsolja össze a forrás az 1933-as náci hatalomra jutást Einstein Egyesült Államokba költözésével?
5. Mit mond a forrás Einstein Rooseveltnek írt leveléről?

## Eredményösszefoglaló

Az eredmények vegyesek voltak, de tanulságos módon.

A rendszer jól válaszolta meg a Nobel-díj kérdését, és részben megválaszolta a széles életút-kérdést is, különösen az 1933-as Európából az Egyesült Államokba vezető átmenet körül.

Ugyanakkor több olyan kérdésen elbukott, ahol várakozásom szerint a releváns információnak szerepelnie kellene az alapul szolgáló Wikipédia-cikkben. Különösen azt állította, hogy nincs információ az 1905-ös annus mirabilis cikkekről, az 1933-as náci hatalomra jutás kapcsolatáról, valamint Einstein Rooseveltnek írt leveléről.

Ezt lekérési hibaként értelmezem, nem annak bizonyítékaként, hogy a forrásdokumentumból hiányzik az információ.

## Kérdésenkénti Elemzés

### 1. Életesemények Ulmtól az Egyesült Államokig

A válasz részben működött, de fókuszálatlan volt.

Hasznos információkat kért le Einstein 1933-as átmenetéről:

- 1933 februárjában az Egyesült Államokban tartózkodott.
- Felismerte, hogy a nácik hatalomra jutása után lehetetlenné vált a visszatérés Németországba.
- Berlini lakását átkutatták.
- Tudomást szerzett a felhatalmazási törvényről.
- Elsa Einsteinnel úgy döntöttek, hogy nem térnek vissza Berlinbe.
- 1933. március 28-án Antwerpenben szállt partra.
- Leadta útlevelét és lemondott német állampolgárságáról.
- Időt töltött Belgiumban és Angliában.
- Végül elfogadta a princetoni Institute for Advanced Study pozícióját.

Ez értékes és forrásszerű.

A válasz azonban nem adta meg tisztán a kért, teljes, dátummal ellátott útvonalat:

```text
Ulm -> Munich -> Switzerland -> Berlin -> United States
```

Ehelyett a válasz nem kapcsolódó gráfkontextusba sodródott, többek között:

- Oskar Halecki és Giuseppe Motta
- Népszövetségi bizottsági politika
- Kurt Goedel
- Jeruzsálemi Héber Egyetem
- Dél-amerikai látogatások
- Harry Fosdick, Upton Sinclair és Charlie Chaplin
- J. Robert Oppenheimer 1965-ös emlékbeszéde

Ezek kapcsolódnak Einsteinhez a gráfban, de nem központi elemei a kérdésnek.

### 2. 1905-ös Annus Mirabilis Cikkek

Ez az ellenőrzésem szerint egyértelmű hiba volt.

A rendszer azt válaszolta, hogy a megadott adatok nem tartalmaznak információt Einstein 1905-ös annus mirabilis cikkeiről. Csak azt említette, hogy Einstein 1901-ben publikálta első cikkét, és 1905-ben fejezte be doktori disszertációját.

Ez forrásszintű elvárásként hibás: az Einstein Wikipédia-cikk tartalmazza az annus mirabilis témát. Számomra a hiba azt jelzi, hogy a Local lekérés nem hozta felszínre a releváns szöveget vagy gráfcsomópontokat.

A lekért forráslista is zajos volt, és nem kapcsolódó entitásokat tartalmazott, például:

- Juan Jorge Duclout és Mauricio Nirenstein
- Jeruzsálemi Héber Egyetem
- Alfred Einstein
- John Robert Oppenheimer
- Bohr
- Harry Fosdick, Upton Sinclair és Charlie Chaplin
- Népszövetséghez kapcsolódó személyek
- Einstein-hűtőszekrény
- Zürich
- Trenton

Ez arra utal, hogy az Einstein körüli gráfreprezentáció széles, de gyengén szűrt az adott kérdéshez.

### 3. Nobel-díj és Relativitás

Ez volt a legerősebb válasz a Local-módú tesztben.

A rendszer helyesen állította, hogy Einstein az 1921-es fizikai Nobel-díjat az elméleti fizikának tett szolgálataiért, különösen a fotoelektromos hatás törvényének felfedezéséért kapta.

Azt is helyesen magyarázta el, hogy miért nem a relativitásért ítélték oda a díjat: a relativitás még vitatott volt, és a Nobel-bizottság számára kevésbé volt közvetlenül lezárt kérdés, míg a fotoelektromos hatás kísérletileg jobban alátámasztott volt, és fontosabbnak számított a kvantumelmélet számára.

Szerintem ez a kérdés azért működött, mert jól illeszkedik egy konkrét entitás-/kapcsolatmintára:

```text
Einstein -> Nobel Prize -> photoelectric effect
```

Ez az a feladattípus, ahol a Local mód megbízhatónak tűnt.

### 4. 1933-as Náci Hatalomra Jutás és az Egyesült Államokba Költözés

Ez lekérési következetlenség volt.

A rendszer azt válaszolta, hogy a megadott szöveg nem tartalmaz információt az 1933-as náci hatalomra jutásról vagy annak Einstein Egyesült Államokba költözésével való kapcsolatáról.

Ez ellentmond az 1. kérdésre adott válasznak, ahol a rendszer már lekért releváns 1933-as információkat a `Sources (4)` forrásból.

Ez azt jelenti, hogy a hiba nem hiányzó forrásadat miatt történt. A releváns forrás létezik, de a Local lekérés nem adta vissza következetesen ennél a kérdésmegfogalmazásnál.

### 5. Einstein Rooseveltnek Írt Levele

Ez is elbukott.

A rendszer azt válaszolta, hogy a forrásanyag nem tartalmaz információt Einstein Rooseveltnek írt leveléről.

Ezt nagyon valószínűen lekérési hibának tartom. A korábbi, szélesebb teszt már lekérte és használta a Roosevelt-levél témát, és az Einstein-cikk várhatóan tartalmazza ezt az eseményt.

A lekért kontextust ismét Einsteinhez lazán kapcsolódó, de Roosevelt, Szilard, nukleáris fegyverek, urán vagy Manhattan-terv szempontjából irreleváns gráfelemek uralták.

## Ami Működött az Ellenőrzésemben

A Local mód akkor működött, amikor a kérdés szorosan kötődött egy jól reprezentált gráfkapcsolathoz.

A Nobel-díj kérdése a legtisztább példa. A rendszer megtalálta a releváns Nobel-díj kontextust, és pontos választ adott.

Az 1933-as migrációs történet is megjelent az egyik válaszban, amikor a megfelelő forrásrészlet került lekérésre. Ez bizonyítja, hogy az alapul szolgáló indexelt adatok legalább némi releváns anyagot tartalmaznak.

A Gemini lekérdezési modell viszonylag felelősen viselkedett. Amikor a lekért kontextus nem tartalmazott elég bizonyítékot, gyakran megtagadta a választ ahelyett, hogy szabadon hallucinált volna. Forráskorlátozott tesztnél ezt jobbnak tartom, mint alátámasztatlan részleteket kitalálni.

## Ami Nem Működött az Ellenőrzésemben

### A Local Lekérési Visszahívás Gyenge Volt

A rendszer nem tudott nyilvánvalóan forrásreleváns információt lekérni a következőkhöz:

- annus mirabilis cikkek
- 1933-as náci hatalomra jutás
- Roosevelt-levél

Ezek nem homályos részletek. Hiányuk a válaszból lekérési problémára utal.

### A Gráf Zajos Volt

A forráslisták ismételten sok alacsony relevanciájú vagy irreleváns gráfcsomópontot tartalmaztak:

- `ALFRED EINSTEIN`
- `JUAN JORGE DUCLOUT AND MAURICIO NIRENSTEIN`
- `O.S. HALLECKI AND GIOVANNI MOTTARA`
- `HARRY FOSDICK AND UPTON SINCLAIR AND CHARLIE CHAPLIN`
- `ZOOELLNER FAMILY CONSERVATORY`
- `TRENTON`
- `EINSTEIN REFRIGERATOR`
- `HEBREW UNIVERSITY OF JERUSALEM`
- `UNESCO`
- `JOHN ROBERT OPPENHEIMER`

Ezek jelen lehetnek a forráscikkben, de nem hasznosak a tesztelt kérdésekhez.

### Néhány Kapcsolat Túlterhelt Volt

Az `EINSTEIN -> ZURICH` kapcsolat különösen problémás. Sok, egymással nem összefüggő állítást kötött egybe, többek között vallást, pacifizmust, hegedülést, vegetarianizmust, a Jeruzsálemi Héber Egyetemet és zürichi találkozókat.

Ez a fajta kapcsolat csökkenti a lekérési pontosságot. Egyetlen nagy súlyú kapcsolat szemantikailag túl szélessé válik, és sok, nem kapcsolódó választ beszennyezhet.

### Az Indexelési Modell Valószínűleg Korlátozta a Gráf Minőségét

A gráf `qwen2.5:3b` használatával készült. A megfigyelt gráfarbeavatkozások arra utalnak, hogy ez a modell túl gyenge lehet egy összetett életrajzi cikkből való jó minőségű entitás- és kapcsolatkivonáshoz.

Példák a gráfminőségi problémákra:

- összekapcsolt, több személyből álló entitások
- zajos vagy irreleváns kapcsolatok
- túlterhelt kapcsolatleírások
- kulcsesemények gyenge reprezentációja
- hiányzó vagy alul-lekért témák, például az annus mirabilis és a Roosevelt-levél

## Miért Nem Tudott a Rendszer Megválaszolni Egyes Kérdéseket

A rendszer nem azért bukott el, mert a Gemini nem tudott válaszolni. Azért bukott el, mert a Local-módú kontextus gyakran nem tartalmazta a szükséges bizonyítékot.

Amikor a modell ezt mondja:

```text
The provided source material does not contain this information.
```

ezt pontosabban így kell érteni:

```text
The retrieved Local-mode context did not contain this information.
```

Ez lényeges különbség.

A forráscikk tartalmazhatja a tényt, de a Local lekérés nem kérte le a megfelelő szövegegységet, entitást, jelentést vagy kapcsolatot.

## Fő Diagnózis

A fő következtetésem az, hogy a jelenlegi pipeline-t a lekérési minőség és a gráfminőség korlátozza, nem elsősorban a lekérdezési modell.

A lekérdezési modell `gemini-2.5-flash-lite`-ra frissítése jelentősen segített. Ez a teszt viszont megmutatta, hogy egy erős lekérdezési modell sem tud megbízhatóan forrásalapú kérdésekre válaszolni, ha a lekért gráfkontextus hiányos vagy zajos.

A Local mód nem ideális mind az öt kérdéshez:

- Jó közvetlen entitáskapcsolatokhoz, például a Nobel-díjhoz és a fotoelektromos hatáshoz.
- Gyengébb forrásszakasz-kérdésekhez, például: "mit mond a cikk a Roosevelt-levélről?"
- Gyengébb történeti kronológiához, például: Ulm -> München -> Svájc -> Berlin -> Egyesült Államok.
- Gyengébb széles eseményszintézishez, például az 1933-as náci hatalomra jutás és emigráció történetéhez.

## Saját Következtetéseim a Következő Lépésekhez

### 1. Újraindexelés Erősebb Indexelési Modellel

A látottak alapján a legnagyobb hatású javítás valószínűleg a cikk újraindexelése egy erősebb modellel. Ezzel kezdeném, mielőtt további lekérdezési promptokat finomítanék.

A következő ellenőrzéshez ezt a beállítást használnám:

- Index chat modell: `gemini-2.5-flash-lite` vagy más erősebb modell
- Lekérdezési chat modell: `gemini-2.5-flash-lite`
- Beágyazási modell: maradjon stabil beágyazási modell, de az indexelési és lekérdezési beágyazási modellek egyezzenek

A jelenlegi `qwen2.5:3b` index zajos gráfot látszik létrehozni.

### 2. Forrás vagy Hibrid Lekérési Mód Hozzáadása

Az annus mirabilis, az 1933-as emigráció és a Roosevelt-levél jellegű kérdésekhez a saját tesztem alapján a graph-local lekérés nem elég.

A következő validálásban ezt a stratégiát próbálnám ki:

```text
Step 1: retrieve relevant raw text units
Step 2: retrieve local graph entities and relationships
Step 3: rerank evidence against the question
Step 4: answer only from the filtered evidence
```

Ez egyesítené a szöveges lekérés és a gráflekérés előnyeit.

### 3. Útválasztás Javítása

Az útválasztónak különböző kérdéstípusokat különböző lekérési módokba kellene küldenie. Ebben a tesztben ugyanaz a Local stratégia nagyon eltérően viselkedett a kérdés megfogalmazásától függően:

| Kérdéstípus | Legjobb mód |
|---|---|
| Közvetlen entitáskapcsolat | Local |
| "Mit mond a forrás erről..." | Source |
| Kronológiai életút | Source vagy Global |
| Széles szintézis | Global vagy DRIFT |
| Több ugrásos oksági kapcsolat | DRIFT vagy Hybrid |
| Forrásalapú ténybizonyíték | Source + Local |

### 4. Lekért Csomópontok Újrarangsorolása

A végső válasz előtt a lekért csomópontokat és kapcsolatokat a felhasználói kérdéshez való relevancia szerint kellene szűrni. Túl sok olyan csomópontot láttam, amely technikailag kapcsolódott Einsteinhez, de az adott kérdéshez nem adott hasznos bizonyítékot.

Például egy Roosevelt-levél kérdésnél előnyben kellene részesíteni:

- Einstein
- Roosevelt
- Leo Szilard
- uranium
- nuclear weapons
- Manhattan Project
- 1939 letter

Ki kellene zárni:

- Alfred Einstein
- Hebrew University
- South America visit
- Charlie Chaplin
- Zurich violin/religion relationship
- Einstein refrigerator

### 5. Megjelenített Források Korlátozása

A frontendnek nem kellene minden lekért entitást és kapcsolatot megjelenítenie.

Csak ezeket kellene megjelenítenie:

- a válaszban ténylegesen használt forrásokat
- a legjobbra rangsorolt releváns entitásokat/kapcsolatokat
- egy kis, korlátozott számot, például 5-8 forrást

Ez megbízhatóbbá és kevésbé zajossá tenné az idézetterületet.

### 6. Kritikus Teszttények Validálása

Ennél az Einstein-tesztnél csak akkor tartanám sikeresnek a rendszert, ha megbízhatóan le tudja kérni és meg tudja válaszolni:

- 1905-ös annus mirabilis cikkek
- Nobel-díj oka
- 1933-as náci hatalomra jutás és emigráció
- Roosevelt-levél
- Ulm -> München -> Svájc -> Berlin -> Egyesült Államok útvonal

Ha ezek bármelyike nem kérhető le, először az indexelési vagy lekérési szinten vizsgálnám a problémát.

## Saját Végső Következtetés

A második Local-módú teszt számomra azt mutatja, hogy a GraphRAG rendszer részben működik, de még nem megbízható széles történeti-tudományos szintézishez.

A legerősebb eredmény a Nobel-díj kérdése volt, ahol a Local mód illeszkedett egy világos entitáskapcsolathoz.

A leggyengébb eredmények az annus mirabilis és a Roosevelt-levél kérdések voltak, ahol a rendszer tévesen azt állította, hogy a forrás nem tartalmaz információt. Ezeket a hibákat lekérési és gráfindex-minőségi problémának látom.

A gyakorlati tanulságom az, hogy a legfontosabb következő lépés nem egy újabb lekérdezésimodell-frissítés. A lekérdezési modell már elég jó ahhoz, hogy világosan feltárja a problémát. A következő lépésként az indexelt gráfot javítanám, és forrás-/hibrid lekérést adnék hozzá, hogy a releváns szöveges bizonyíték a válaszgenerálás előtt rendelkezésre álljon.
