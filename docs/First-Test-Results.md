**Language / Nyelv:** [English](#english) | [Magyar](#magyar)

<a id="english"></a>

# First Test Run Result

## Test Context

In this first run, I compared two responses to the same prompt about the indexed Wikipedia article on Albert Einstein:

- Baseline model: plain `qwen2.5:3b`
- GraphRAG model: `qwen2.5:3b` using the indexed Albert Einstein article

I used this prompt because it is intentionally difficult for a RAG system: it does not only ask for isolated facts, but also for chronology, causal or thematic links, the 1905 annus mirabilis papers, the Nobel Prize distinction, the 1933 political shift, the Roosevelt letter, and a short source-evidence section.

## Baseline `qwen2.5:3b` Response

### Strengths

The plain model gave me a coherent and readable high-level summary. It identified some broadly relevant Einstein topics, including relativity, the photoelectric effect, the Nobel Prize, public fame after 1919, nuclear weapons, and his death in Princeton.

Compared with the GraphRAG response, it also avoided some of the more extreme fabricated citation patterns. The answer is generic, but as a short biographical overview it felt more stable during my check.

### Weaknesses

The baseline response did not really follow the requested task. It did not build an eight-date chronological chain, did not explain the path from Ulm through Munich, Switzerland, Berlin, and the United States, and did not separate the 1905 papers from general relativity and quantum/statistical mechanics contributions.

It also missed the key Nobel Prize distinction: Einstein did not receive the Nobel Prize for relativity, but for his explanation of the photoelectric effect. The response mentions the Nobel Prize only generally.

There are also factual and source-faithfulness issues. For example, it says Einstein was born in "Ulm, Germany (now part of Austria)", which is incorrect. Ulm is in Germany. It also claims he had "three daughters", while the well-known biographical record is more complex and includes two sons and a daughter. Because the prompt explicitly requested use of the indexed source only, these mistakes matter.

### Overall Assessment

My conclusion for the baseline answer is that it was safer in tone and simpler, but it mostly ignored the analytical structure I asked for in the prompt. It did not demonstrate strong relationship reasoning. It answered as if the task were "summarize Albert Einstein", not "analyze source-grounded connections across Einstein's life, science, and politics."

## GraphRAG `qwen2.5:3b` Response

### Strengths

The GraphRAG response tried to follow my requested structure more directly. It used headings, and it attempted to organize the answer around chronology, scientific contributions, the Nobel Prize, the 1933 political shift, the Roosevelt letter, and source evidence.

This showed me that it recognized more of the shape of the task than the baseline model. It also attempted to make connections between Einstein's scientific work and political-historical events, especially around the Roosevelt letter and nuclear weapons.

### Weaknesses

Even though the structure was closer to the prompt, I found the GraphRAG response much weaker in factual reliability.

It invented or distorted several major facts:

- "1904 October 27" is presented as a key date for movement through Munich, Switzerland, and Berlin, but this does not match the requested source narrative.
- "1905 January 16 to February 31" is impossible because February 31 does not exist.
- It places Einstein in a "Los Angeles conservatory" in 1920, which is not a valid source-grounded milestone for this task.
- It gives the route as "Ulm, Germany - Munich, Austria - Berlin, Germany - Los Angeles, USA", which is geographically and historically wrong. Munich is in Germany, and the requested path included Switzerland and the United States, not Los Angeles as the main endpoint.
- It incorrectly lists general relativity as an "1905 annus mirabilis" result. General relativity was completed later, with 1915 being the key year.
- It does not clearly identify the four 1905 annus mirabilis papers.
- It blurs the Nobel Prize explanation instead of clearly stating that the prize was awarded for the photoelectric effect, not relativity.
- It introduces unrelated or weakly supported figures such as Kurt Goedel, Chaim Weizmann, and Wilfrid Israel in a way that does not answer the prompt's requested causal chain.

The source-evidence section is also poor. It does not provide verifiable source facts. Instead, it uses artificial-looking placeholders such as:

```text
[Data: Einstein 1905-os adatok (1, 5, 15)]
[Data: General Knowledge (href)]
```

These are not useful citations for the user. Worse, they create the appearance of source grounding while the underlying claims are often incorrect.

### Overall Assessment

My assessment is that the GraphRAG answer understood the requested format better, but failed at the most important requirement: source-grounded accuracy. It seemed to "see" that the question asked for relationships, chronology, and evidence, but it did not reliably map those requirements to correct facts from the indexed article.

For me this made the GraphRAG response more risky than the baseline response in this run. It was more confident, more structured, and more citation-like, but also more misleading.

## Direct Comparison

| Criterion | Plain `qwen2.5:3b` | GraphRAG `qwen2.5:3b` | Winner |
|---|---|---|---|
| Prompt following | Weak | Medium | GraphRAG |
| Chronological structure | Weak | Attempted, but inaccurate | Neither |
| Factual accuracy | Mixed, but simpler | Poor, with serious fabrications | Plain model |
| Source faithfulness | Weak | Weak to misleading | Plain model |
| Relationship reasoning | Weak | Attempted, but unreliable | Neither |
| Citation/source evidence | Missing | Present-looking but not trustworthy | Neither |
| User trustworthiness | Medium-low | Low | Plain model |

## Which Model Is Stronger?

For this specific test run, I consider the plain `qwen2.5:3b` response stronger overall, not because it was good, but because it was less misleading.

The GraphRAG response was stronger only in surface-level task recognition. It tried to produce the requested analytical structure and tried to connect biography, science, and politics. However, those connections were often built on incorrect facts, fabricated dates, and unusable pseudo-citations.

If the question is "which model sees the requested structure better?", the answer is GraphRAG.

If the question is "which answer should a user trust more?", the answer is the plain model.

If the question is "which model currently demonstrates the real strength of GraphRAG?", the answer is neither. The GraphRAG pipeline is not yet converting retrieved context into accurate, verifiable, clickable, source-grounded answers for this kind of broad multi-hop prompt.

## My Diagnosis

From this run, I do not think the retrieval/indexing layer is the only issue. The answer-generation step also seems to struggle with a broad, multi-part prompt on a small local model (`qwen2.5:3b`).

The model receives or reconstructs some GraphRAG context, but in my validation it did not preserve the factual details reliably. It also appeared to fabricate citation labels instead of using the actual retrieved entities and relationships in a controlled way.

The earlier log also showed that the auto router selected DRIFT mode for this prompt. DRIFT is reasonable for multi-hop relationship questions, but in the current application it does not expose clickable node sources the same way Local mode does. During validation, this made the final answer harder to inspect and verify.

## My Follow-Up Conclusion

Based on what I saw in this run, I would not continue evaluating this setup with only one broad Einstein prompt. I would split the next validation into two separate prompts:

1. A Local-mode factual precision prompt focused on specific entities and relationships.
2. A broader DRIFT or Global-mode synthesis prompt, but evaluated mainly for narrative quality and then checked against source facts.

For this exact Einstein test, I would only count the GraphRAG answer as successful if it can correctly state at least the following:

- Einstein was born in Ulm in 1879.
- His family moved to Munich, and he later studied in Switzerland.
- His 1905 annus mirabilis papers covered the photoelectric effect, Brownian motion, special relativity, and mass-energy equivalence.
- General relativity was completed later, with 1915 as the key year.
- The Nobel Prize was awarded for the photoelectric effect, not relativity.
- In 1933, the Nazi rise to power was connected to his decision not to return to Germany and to settle in the United States.
- The Roosevelt letter relates to fears about nuclear weapons development, not to Einstein directly building the atomic bomb.

Based on the output I inspected, the current GraphRAG response did not meet this bar.


<a id="magyar"></a>

# Első Tesztfuttatás Eredménye

## Tesztkörnyezet

Ebben az első futásban két választ hasonlítottam össze ugyanarra az, Albert Einstein indexelt Wikipédia-cikkéről szóló promptra:

- Alapmodell: egyszerű `qwen2.5:3b`
- GraphRAG modell: `qwen2.5:3b` az indexelt Albert Einstein-cikk használatával

Azért ezt a promptot használtam, mert szándékosan nehéz egy RAG-rendszer számára: nem csak különálló tényeket kér, hanem kronológiát, oksági vagy tematikus kapcsolatokat, az 1905-ös annus mirabilis cikkeket, a Nobel-díj megkülönböztetését, az 1933-as politikai fordulatot, a Roosevelt-levelet, valamint egy rövid forrásbizonyíték-szakaszt.

## Alap `qwen2.5:3b` Válasz

### Erősségek

Az egyszerű modell koherens, olvasható, magas szintű összefoglalót adott. Azonosított néhány általánosan releváns Einstein-témát, többek között a relativitást, a fotoelektromos hatást, a Nobel-díjat, az 1919 utáni nyilvános ismertséget, a nukleáris fegyvereket és a Princetonban bekövetkezett halálát.

A GraphRAG-válaszhoz képest elkerülte a szélsőségesebb kitalált hivatkozási minták egy részét. A válasz általános, de rövid életrajzi áttekintésként az ellenőrzésem alapján viszonylag stabilnak tűnt.

### Gyengeségek

Az alapválasz valójában nem követte a kért feladatot. Nem épített fel nyolc dátumból álló kronológiai láncot, nem magyarázta el az utat Ulmtól Münchenen és Svájcon át Berlinig és az Egyesült Államokig, és nem választotta szét az 1905-ös cikkeket az általános relativitástól, valamint a kvantum- és statisztikus mechanikai hozzájárulásoktól.

Kihagyta a Nobel-díj kulcsfontosságú megkülönböztetését is: Einstein nem a relativitásért kapta a Nobel-díjat, hanem a fotoelektromos hatás magyarázatáért. A válasz a Nobel-díjat csak általánosan említi.

Ténybeli és forráshűségi problémák is vannak. Például azt állítja, hogy Einstein "Ulm, Germany (now part of Austria)" helyen született, ami téves. Ulm Németországban van. Azt is állítja, hogy "három lánya" volt, miközben a jól ismert életrajzi adatok összetettebbek, és két fiút, valamint egy lányt tartalmaznak. Mivel a prompt kifejezetten csak az indexelt forrás használatát kérte, ezek a hibák számítanak.

### Átfogó Értékelés

Az alapmodellről az volt a benyomásom, hogy biztonságosabb és egyszerűbb hangon válaszolt, de többnyire figyelmen kívül hagyta a prompt által kért elemző szerkezetet. Nem mutatott erős kapcsolati következtetést. Úgy válaszolt, mintha a feladat ez lenne: "foglalja össze Albert Einsteint", nem pedig ez: "elemezze a forrásalapú kapcsolatokat Einstein élete, tudománya és politikája között."

## GraphRAG `qwen2.5:3b` Válasz

### Erősségek

A GraphRAG-válasz közvetlenebbül próbálta követni a kért szerkezetet. Címsorokat használt, és megpróbálta a választ a kronológia, a tudományos hozzájárulások, a Nobel-díj, az 1933-as politikai fordulat, a Roosevelt-levél és a forrásbizonyíték köré szervezni.

Ebből számomra az látszott, hogy jobban felismerte a feladat formáját, mint az alapmodell. Megpróbált kapcsolatokat teremteni Einstein tudományos munkája és politikai-történelmi események között is, különösen a Roosevelt-levél és a nukleáris fegyverek körül.

### Gyengeségek

Bár szerkezetileg közelebb állt a prompthoz, az ellenőrzésem alapján a GraphRAG-válasz tényszerű megbízhatósága sokkal gyengébb volt.

Több jelentős tényt kitalált vagy eltorzított:

- A "1904 October 27" kulcsdátumként jelenik meg a Münchenen, Svájcon és Berlinen át vezető mozgáshoz, de ez nem illeszkedik a kért forrásnarratívához.
- A "1905 January 16 to February 31" lehetetlen, mert február 31. nem létezik.
- Einsteint 1920-ban egy "Los Angeles conservatory" helyszínre helyezi, ami nem érvényes forrásalapú mérföldkő ehhez a feladathoz.
- Az útvonalat így adja meg: "Ulm, Germany - Munich, Austria - Berlin, Germany - Los Angeles, USA", ami földrajzilag és történelmileg hibás. München Németországban van, és a kért út Svájcot, valamint az Egyesült Államokat tartalmazta, nem Los Angelest mint fő végpontot.
- Tévesen sorolja az általános relativitást az "1905 annus mirabilis" eredményei közé. Az általános relativitás később teljesedett ki, a kulcsév 1915.
- Nem azonosítja világosan a négy 1905-ös annus mirabilis cikket.
- Elhomályosítja a Nobel-díj magyarázatát ahelyett, hogy egyértelműen kimondaná: a díjat a fotoelektromos hatásért, nem a relativitásért ítélték oda.
- Olyan nem kapcsolódó vagy gyengén alátámasztott személyeket vezet be, mint Kurt Goedel, Chaim Weizmann és Wilfrid Israel, olyan módon, amely nem válaszolja meg a prompt által kért oksági láncot.

A forrásbizonyíték-szakasz is gyenge. Nem ad ellenőrizhető forrástényeket. Ehelyett mesterségesnek tűnő helyőrzőket használ, például:

```text
[Data: Einstein 1905-os adatok (1, 5, 15)]
[Data: General Knowledge (href)]
```

Ezek nem hasznos idézetek a felhasználó számára. Ami rosszabb, a forrásalapúság látszatát keltik, miközben az alapul szolgáló állítások gyakran hibásak.

### Átfogó Értékelés

Az értékelésem szerint a GraphRAG-válasz jobban értette a kért formátumot, de a legfontosabb követelményben elbukott: a forrásalapú pontosságban. Úgy tűnt, "látja", hogy a kérdés kapcsolatokat, kronológiát és bizonyítékot kér, de ezeket a követelményeket nem tudta megbízhatóan a helyes tényekhez kötni az indexelt cikkből.

Ezért ebben a futásban a GraphRAG-választ kockázatosabbnak tartom az alapválasznál. Magabiztosabb, strukturáltabb és hivatkozásszerűbb volt, de félrevezetőbb is.

## Közvetlen Összehasonlítás

| Kritérium | Egyszerű `qwen2.5:3b` | GraphRAG `qwen2.5:3b` | Győztes |
|---|---|---|---|
| Promptkövetés | Gyenge | Közepes | GraphRAG |
| Kronológiai szerkezet | Gyenge | Megpróbált, de pontatlan | Egyik sem |
| Ténybeli pontosság | Vegyes, de egyszerűbb | Gyenge, súlyos kitalálásokkal | Egyszerű modell |
| Forráshűség | Gyenge | Gyengétől félrevezetőig | Egyszerű modell |
| Kapcsolati következtetés | Gyenge | Megpróbált, de megbízhatatlan | Egyik sem |
| Idézetek/forrásbizonyíték | Hiányzik | Látszólag jelen van, de nem megbízható | Egyik sem |
| Felhasználói megbízhatóság | Közepesen alacsony | Alacsony | Egyszerű modell |

## Melyik Modell Erősebb?

Ebben a konkrét tesztfutásban az egyszerű `qwen2.5:3b` választ tartom összességében erősebbnek, nem azért, mert jó volt, hanem azért, mert kevésbé volt félrevezető.

A GraphRAG-válasz csak felszíni feladatfelismerésben volt erősebb. Megpróbálta létrehozni a kért elemző szerkezetet, és megpróbálta összekapcsolni az életrajzot, a tudományt és a politikát. Ezek a kapcsolatok azonban gyakran helytelen tényekre, kitalált dátumokra és használhatatlan pszeudoidézetekre épültek.

Ha a kérdés az, hogy "melyik modell látja jobban a kért szerkezetet?", a válasz: GraphRAG.

Ha a kérdés az, hogy "melyik válaszban bízhat meg jobban a felhasználó?", a válasz: az egyszerű modell.

Ha a kérdés az, hogy "melyik modell mutatja jelenleg a GraphRAG valódi erejét?", a válasz: egyik sem. A GraphRAG pipeline még nem alakítja át a lekért kontextust pontos, ellenőrizhető, kattintható, forrásalapú válaszokká az ilyen széles, több ugrásos promptok esetében.

## Saját Diagnózis

Ebből a futásból nem azt látom, hogy kizárólag a lekérési/indexelési réteg lenne a probléma. A válaszgenerálási lépés is valószínűleg küszködik egy széles, több részből álló prompttal egy kisméretű helyi modellen (`qwen2.5:3b`).

A modell kap vagy rekonstruál valamennyi GraphRAG-környezetet, de a validálás alapján nem őrzi meg megbízhatóan a tényszerű részleteket. Úgy tűnik, idézetcímkéket is kitalál ahelyett, hogy a ténylegesen lekért entitásokat és kapcsolatokat használná kontrollált módon.

A korábbi napló azt is mutatta, hogy az automatikus útválasztó ehhez a prompthoz DRIFT módot választott. A DRIFT megfelelő lehet több ugrásos kapcsolati kérdésekhez, de a jelenlegi alkalmazásban nem jelenít meg kattintható csomópontforrásokat ugyanúgy, mint a Local mód. Emiatt számomra nehezebb volt a végső válasz ellenőrzése.

## Saját Következtetés a Következő Lépéshez

A látottak alapján nem ugyanazzal az egy széles Einstein-prompttal folytatnám a validálást. A következő ellenőrzést két külön prompttal végezném:

1. Egy Local-módú tényszerű pontossági promptot, amely konkrét entitásokra és kapcsolatokra összpontosít.
2. Egy szélesebb DRIFT- vagy Global-módú szintézispromptot, amelyet főleg narratív minőség alapján kell értékelni, majd forrástényekkel ellenőrizni.

Ebben a konkrét Einstein-tesztben csak akkor tekinteném sikeresnek a GraphRAG-választ, ha legalább a következőket helyesen ki tudja mondani:

- Einstein 1879-ben Ulmban született.
- Családja Münchenbe költözött, később pedig Svájcban tanult.
- 1905-ös annus mirabilis cikkei a fotoelektromos hatást, a Brown-mozgást, a speciális relativitást és a tömeg-energia ekvivalenciát fedték le.
- Az általános relativitás később teljesedett ki, a kulcsév 1915.
- A Nobel-díjat a fotoelektromos hatásért ítélték oda, nem a relativitásért.
- 1933-ban a nácik hatalomra jutása összefüggött azzal a döntésével, hogy nem tér vissza Németországba, hanem az Egyesült Államokban telepszik le.
- A Roosevelt-levél a nukleáris fegyverek fejlesztésével kapcsolatos félelmekhez kötődik, nem ahhoz, hogy Einstein közvetlenül építette volna az atombombát.

A megfigyelt kimenet alapján a jelenlegi GraphRAG-válasz nem érte el ezt a mércét.
