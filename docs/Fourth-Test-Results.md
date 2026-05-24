**Language / Nyelv:** [English](#english) | [Magyar](#magyar)

<a id="english"></a>

# Fourth Test Results: Full Gemini 3.1 Flash Lite GraphRAG vs Baseline Gemini 3.1 Flash Lite

## Test Context

In this test, I compared two answers to the same source-restricted Albert Einstein prompt.

My goal was to check whether a fully Gemini-based GraphRAG pipeline improves source grounding, factual control, relationship reasoning, and big-picture synthesis compared with using the same Gemini model directly without the indexed GraphRAG context.

## Model And Retrieval Setup

### Baseline Model

- Model: Gemini 3.1 Flash Lite
- Mode: direct model answer
- Retrieval/indexing: none
- Embeddings: none
- Constraint in prompt: answer only from the indexed Albert Einstein Wikipedia article, but the baseline model did not actually receive GraphRAG source excerpts or graph citations.

### GraphRAG Model

- Indexing chat model: Gemini 3.1 Flash Lite
- Indexing embedding model: Gemini embedding
- Query chat model: Gemini 3.1 Flash Lite
- Query embedding model: Gemini embedding
- Retrieval mode: `auto`, routed to `hybrid`
- Indexed source: Albert Einstein Wikipedia article
- Retrieval context: ranked raw source text units plus GraphRAG graph context
- Citation style: source markers such as `[S1]`, `[S2]`, with source excerpts listed after the answer.

## Evaluation Prompt

The prompt required the answer to use only the indexed Albert Einstein Wikipedia article and to avoid outside knowledge. If the source did not support a requested point, the answer had to write: "Not determinable from the source."

The answer also had to include:

- a chronological chain with at least eight dates or years,
- a life-path narrative from Ulm to Munich, Switzerland, Berlin, and the United States,
- separate scientific analysis of the 1905 annus mirabilis, general relativity, and quantum/statistical mechanics,
- a Nobel Prize clarification,
- a political-historical analysis connecting 1933, emigration, the United States, the Roosevelt letter, and the Manhattan Project,
- a final "Source Evidence" section with six concrete claims from the indexed article.

## Baseline Gemini 3.1 Flash Lite

### Strengths

The baseline answer is fluent, compact, and well organized. In my check, it followed the requested heading structure and gave a coherent chronological chain with eight relevant years: 1879, 1896, 1905, 1915, 1919, 1922, 1933, and 1939.

It also provides a stronger narrative flow than the GraphRAG answer in some places. The life-path section explains how Einstein's educational discomfort in Munich, academic development in Switzerland, professional rise in Berlin, and political refuge in the United States connect into one broader life story.

The scientific section is clear and complete. It correctly separates the four 1905 achievements, the later importance of general relativity, and Einstein's quantum/statistical mechanics contributions. The Nobel Prize clarification is also strong: it clearly states that the prize was awarded for the photoelectric effect, not relativity.

The political section is thematically strong. It connects the Nazi rise to power, Einstein's emigration, the Roosevelt letter, and his limited role in the Manhattan Project. It also captures the tension between Einstein's pacifism and his fear of Nazi atomic research.

### Weaknesses

The baseline answer is much weaker as a source-restricted answer. It provides no verifiable source markers, so I could not audit which claims came from the indexed article and which came from the model's general knowledge.

Several details increase hallucination or outside-knowledge risk:

- the claim about "American citizenship (1940)" and civil rights activism,
- gravitational waves being "later confirmed by the observation of gravitational waves",
- "critical opalescence",
- Einstein later expressing "deep regret" for signing the Roosevelt letter,
- Time's Person of the Century in the Source Evidence section.

Some of these may be true or may appear somewhere in the article, but the baseline answer does not prove that they came from the indexed source. This matters because the prompt explicitly required source-only answering.

The final "Source Evidence" section is also only loosely tied to the answer. The sixth item, Time's Person of the Century in 1999, is not important for the requested causal analysis and looks like a generic biographical fact rather than evidence used in the answer.

### Baseline Assessment

My assessment is that the baseline model sees the big-picture narrative well, but behaves like a general-knowledge model. It is better at polished synthesis than at controlled source discipline.

For an open-book essay, it is strong. For a strict indexed-source task, it is not sufficiently auditable.

## GraphRAG-Indexed Gemini 3.1 Flash Lite In Hybrid Mode

### Strengths

The GraphRAG answer is substantially more source-grounded. It uses `[S1]`, `[S2]`, and other source markers throughout the answer, then lists the retrieved source excerpts after the response. This gave me a concrete audit trail during validation.

The answer follows the requested structure cleanly:

- chronological life path,
- life-path narrative,
- scientific analysis,
- Nobel Prize clarification,
- political change and Manhattan Project section,
- Source Evidence section.

The answer correctly identifies the core scientific and historical points:

- Einstein's 1905 work included the photoelectric effect, Brownian motion, special relativity, and mass-energy equivalence.
- General relativity is described as curvature of spacetime.
- Einstein's Nobel Prize is attributed to the law of the photoelectric effect, not relativity.
- The 1939 Roosevelt letter is connected to concern about Nazi atomic bomb research.
- Einstein's direct operational involvement in the Manhattan Project is not asserted beyond what the source supports.

The strongest improvement I noticed over earlier tests is the quality of the retrieved source evidence. The raw source excerpts include the relevant article sections for:

- birth, Swiss move, 1905, Berlin, Nobel Prize,
- 1935 permanent settlement in the United States,
- 1939 Szilard/Roosevelt warning,
- Aarau and citizenship renunciation,
- general relativity,
- 1905 scientific papers,
- 1919 fame and intellectual icon status.

This shows, based on my validation, that the full Gemini indexing and Gemini embedding setup improved retrieval quality and made Hybrid mode much more effective.

### Weaknesses

The GraphRAG answer is more controlled, but less rich than the baseline answer. Its causal and thematic explanations are correct but compact. It often states the connection instead of developing it in depth.

The chronological chain has at least eight dates, but it is not the best possible selection for the prompt. It includes 1935, but omits 1933 from the chronological list, even though the prompt specifically asks to connect the 1933 political change in Germany to emigration and the United States. The political section covers 1933, but the timeline would be stronger if 1933 appeared directly as one of the key chronological milestones.

The life-path narrative mentions Ulm, Switzerland, Berlin, and the United States well, but Munich is underdeveloped. The answer says "Ulm to Munich" in the heading, but the actual explanation of Munich is brief and not as causally meaningful as the baseline answer's discussion of Munich schooling and family movement.

The answer says Einstein "collaborated with fellow refugee scientists" in the Roosevelt-letter context. The retrieved source supports Einstein and Szilard acting along with other refugee scientists, but "collaborated" should be interpreted cautiously. It is acceptable, but a more precise wording would be "Einstein and Szilard, along with other refugee scientists, helped alert Roosevelt."

The retrieved graph entities after the source list still contain some broad or potentially noisy context, such as World War II and Berlin descriptions that generalize Einstein's role. However, the final answer mostly relies on the more reliable `[S]` source excerpts, so this is less damaging than in earlier tests.

### GraphRAG Assessment

The GraphRAG answer is better aligned with the task's source-only requirement. It is not as polished or expansive as the baseline, but I consider it more trustworthy because its main claims are tied to retrievable source evidence.

The answer shows that Hybrid mode is now close to what the project needs it to do: combine raw source excerpts with graph context and produce a controlled, auditable synthesis.

## Direct Comparison

| Criterion | Baseline Gemini 3.1 Flash Lite | GraphRAG Gemini 3.1 Flash Lite Hybrid | Winner |
|---|---|---|---|
| Prompt structure | Strong | Strong | Tie |
| Source grounding | Weak; no audit trail | Strong; explicit `[S]` citations and source excerpts | GraphRAG |
| Chronology | Stronger date selection | Good, but omits 1933 from the timeline | Baseline |
| Life-path narrative | More fluent and explanatory | More source-controlled, but Munich is thin | Baseline for narrative, GraphRAG for source control |
| Scientific analysis | Richer and more detailed | Accurate and source-supported, but compact | Tie, depending on priority |
| Nobel Prize clarification | Strong | Strong and cited | GraphRAG |
| Political-historical synthesis | More nuanced prose | More cautious and source-auditable | GraphRAG for reliability, Baseline for expression |
| Hallucination control | Medium risk | Lower risk | GraphRAG |
| Big-picture synthesis | Stronger narrative flow | Stronger source-grounded synthesis | Split |

## Which Model Performed Better?

For this test, I consider the GraphRAG-indexed Gemini 3.1 Flash Lite model better overall.

The reason is not that it wrote a more fluent essay. The baseline answer is smoother and sometimes better at narrative explanation. However, the prompt was explicitly a source-only task over an indexed article. Under that requirement, the GraphRAG answer is superior because it provides source citations, uses retrieved article excerpts, and avoids unsupported expansion more effectively.

The baseline answer is impressive as a general synthesis, but it cannot prove that its claims came only from the indexed source. That makes it weaker for a GraphRAG evaluation.

## Which Model Sees The Big Picture Better?

There are two different meanings of "big picture."

If big picture means polished historical storytelling, the baseline Gemini model is slightly stronger. It connects the locations, scientific phases, and political decisions with more natural explanatory flow.

If big picture means source-grounded understanding of how the indexed article connects Einstein's life, science, and political decisions, the GraphRAG model is stronger. It identifies the relevant source passages and builds the synthesis from them.

For this project, I treat the second interpretation as more important. The project is not trying to show that a model can write a good Einstein essay from memory. It is trying to show that knowledge-graph-enhanced retrieval can make generative answers more accurate, contextual, and traceable. On that goal, the GraphRAG model performs better.

## My Main Findings

The full Gemini setup appears to be a meaningful improvement over earlier tests. From the output I checked, using Gemini 3.1 Flash Lite for indexing and querying, with Gemini embeddings for both index and query, produced better source retrieval and better answer discipline.

Hybrid mode looked like the most suitable mode for this kind of prompt because the task requires both:

- raw source evidence for factual grounding,
- graph/context synthesis for relationships across biography, science, and politics.

The GraphRAG answer still needs refinement in explanatory depth and timeline selection, but in my view it demonstrates the core value of the project more clearly than the baseline.

## My Follow-Up Conclusions

For future tests, I would keep the full Gemini indexing/query profile when evaluating source-grounded synthesis quality.

Based on this run, I would improve the Hybrid prompt or post-processing expectations in three ways:

1. Require 1933 to appear in the chronological chain when the question asks about political emigration.
2. Require the life-path narrative to explain each named place with at least one concrete source-supported role.
3. Prefer cautious wording for the Roosevelt letter, such as "helped alert" or "helped stimulate U.S. atomic research", rather than stronger causal claims.

For thesis evaluation, I would present this test as strong evidence that GraphRAG improves auditability and source discipline. It is a more successful run than the earlier local-model and Local-mode experiments.

## My Final Verdict

Overall winner: GraphRAG-indexed Gemini 3.1 Flash Lite in Hybrid mode.

Best narrative prose: baseline Gemini 3.1 Flash Lite.

Best source-grounded answer: GraphRAG Gemini 3.1 Flash Lite Hybrid.

Best fit for the thesis project: GraphRAG Gemini 3.1 Flash Lite Hybrid, because in my validation it better demonstrates the intended value of GraphRAG: structured retrieval, source traceability, reduced unsupported claims, and auditable multi-part synthesis.

---

# Fourth Test Rerun: Gemini 3.1 Flash Lite GraphRAG With Gemini Embedding 2

## Rerun Context

I reran the fourth test after switching the Gemini embedding model from `gemini-embedding-001` / Gemini Embedding 1 behavior to `gemini-embedding-2`.

The rerun used:

- Indexing chat model: Gemini 3.1 Flash Lite
- Indexing embedding model: `gemini-embedding-2`
- Query chat model: Gemini 3.1 Flash Lite
- Query embedding model: `gemini-embedding-2`
- Retrieval mode: `auto`, routed to Hybrid-style source-plus-graph answering
- Source document: indexed Albert Einstein Wikipedia article
- Prompt: same source-restricted, multi-part Einstein analysis prompt

My goal with this rerun was to check whether the newer embedding model improves retrieval quality, source grounding, and synthesis quality compared with the earlier fourth-test GraphRAG answer.

## Result Summary

The `gemini-embedding-2` rerun remained clearly source-grounded and auditable, but I did not see it as an unambiguous improvement over the previous Gemini Embedding 1 run.

The retrieved source chunks are mostly the same high-value chunks as before:

- `[S1]` covers the biography overview, Switzerland, 1905, Berlin, Nobel Prize, and emigration.
- `[S2]` covers the United States, Institute for Advanced Study, World War II, Szilard, and the Manhattan Project section.
- `[S3]` covers Aarau, the 1896 graduation, and citizenship renunciation.
- `[S5]` covers general relativity as curvature of spacetime.
- `[S6]` covers the 1905 scientific papers.
- `[S7]` covers 1919 fame and the 1921 U.S. visit.
- `[S8]` covers pacifism and related political views.

This means the retrieval layer is still finding the right article sections. The main differences appeared in answer synthesis, not in raw source availability.

## Strengths Of The Gemini Embedding 2 Rerun

The answer is well structured and follows the requested sections:

- chronological chain,
- life-path narrative,
- scientific analysis,
- Nobel Prize clarification,
- political change and emigration,
- source evidence.

The source discipline is strong. The answer consistently attaches `[S]` citations to most claims and avoids long unsupported expansions. I still see this as a major improvement over a direct baseline answer with no retrieval audit trail.

The Nobel Prize clarification is excellent. It correctly states that Einstein did not receive the Nobel Prize for relativity and cites the photoelectric effect wording from `[S1]`.

The general relativity subsection is stronger than the previous GraphRAG answer in one respect: it uses the retrieved source about spacetime curvature and connects it to 1919 public fame. This gives the reader both the conceptual point and the historical reception point.

The Manhattan Project wording is cautious. The answer says the source supports Einstein and Szilard alerting Americans to Nazi atomic research, but does not assert detailed operational involvement in the Manhattan Project. This is safer than stronger causal claims such as saying Einstein directly launched or participated in the project.

The source evidence section is relevant and directly tied to the answer. It avoids the previous baseline problem I saw, where peripheral facts were listed as evidence.

## Weaknesses And Regressions

The biggest regression I found is in the 1905 annus mirabilis section.

The rerun says the four major works were:

- photoelectric effect,
- Brownian motion,
- special relativity containing `E=mc^2`,
- PhD dissertation on molecular dimensions.

This is not the best source-faithful formulation. The indexed source distinguishes the PhD dissertation from the four other famous 1905 works. In my evaluation, the four annus mirabilis works should be stated as:

- photoelectric effect,
- Brownian motion,
- special relativity,
- mass-energy equivalence.

The PhD dissertation is a relevant 1905 event, but it should not replace mass-energy equivalence as one of the four annus mirabilis achievements. This is a significant scientific-analysis error because the prompt explicitly asks for the four main achievements of 1905.

The chronological chain is acceptable in count but weaker in date selection. It includes eight dates, but it omits:

- `1879`, Einstein's birth in Ulm,
- `1933`, the political turning point in Germany,
- `1939`, the Roosevelt-letter context.

Instead, it includes `1929` pacifism. That date is relevant thematically, but for this exact prompt, `1933` and `1939` are more central. The previous Embedding 1 GraphRAG answer also omitted `1933` from the timeline, but it at least included `1879`; the rerun loses the starting point of the life path.

The Ulm-to-Munich part is still thin. The answer says "Ulm to Munich" in the heading, but it does not meaningfully explain Munich's role. It jumps quickly from the German Empire to Switzerland. This repeats one of the main weaknesses of the earlier GraphRAG answer.

The quantum theory and statistical mechanics subsection is too compressed. It mentions that Einstein made significant contributions and later tried to refute accepted quantum interpretations, but it does not clearly explain the source-supported substance of his quantum/statistical work. The previous Embedding 1 answer was better here because it explicitly mentioned light quanta, the photoelectric effect, molecular physics, statistical descriptions, and Brownian motion.

The political section is cautious but slightly under-complete. It refers to alerting Americans and Washington, but it could more explicitly name President Franklin D. Roosevelt because the prompt specifically asks about the letter to Roosevelt.

## Comparison With The Previous Fourth-Test GraphRAG Answer

| Criterion | Previous GraphRAG With Gemini Embedding 1 | Rerun With Gemini Embedding 2 | Winner |
|---|---|---|---|
| Source retrieval | Strong; retrieved the key Einstein chunks | Strong; retrieved mostly the same key chunks | Tie |
| Source citations | Strong `[S]` citation discipline | Strong `[S]` citation discipline | Tie |
| Chronological chain | Good, but omitted 1933 and 1939 | Good count, but omits 1879, 1933, and 1939 | Embedding 1 |
| Life-path narrative | Source-controlled but Munich was thin | Similar, but Munich is even less developed | Embedding 1 |
| 1905 annus mirabilis | Correctly listed the four main works including mass-energy equivalence | Incorrectly replaces mass-energy equivalence with the PhD dissertation | Embedding 1 |
| General relativity | Accurate, compact | Slightly richer; includes spacetime curvature and 1919 fame | Embedding 2 |
| Quantum/statistical mechanics | More specific | Too compressed | Embedding 1 |
| Nobel Prize clarification | Strong and cited | Strong and cited | Tie |
| 1933/emigration/Roosevelt/Manhattan Project | More explicit about Roosevelt, but slightly stronger wording | More cautious about limits, but less explicit about Roosevelt | Tie, with different strengths |
| Big-picture synthesis | Compact but coherent | Compact, source-grounded, but less complete scientifically | Embedding 1 overall |

## Which Fourth-Test GraphRAG Version Performed Better?

For this exact prompt, I think the previous GraphRAG answer using Gemini Embedding 1 performed slightly better overall.

The reason is the scientific-analysis regression in the `gemini-embedding-2` rerun. The prompt explicitly asks for the four main 1905 achievements, and the rerun gives a weaker answer by replacing mass-energy equivalence with the PhD dissertation.

That does not mean `gemini-embedding-2` is worse as an embedding model. The retrieved source chunks are still highly relevant, and the entity context appears somewhat cleaner in places. The problem is that the final answer synthesis did not use the retrieved 1905 source carefully enough.

In short, my reading of the rerun is:

- `gemini-embedding-2` did not damage source retrieval.
- It did not clearly improve the final answer.
- The final answer regressed on one critical scientific requirement.

## Comparison Across All Four Tests

| Test | Setup | Main Result | Main Limitation |
|---|---|---|---|
| First test | `qwen2.5:3b` baseline vs `qwen2.5:3b` GraphRAG | GraphRAG saw the requested structure better, but factual reliability was poor | Fabricated dates, weak citations, serious source-faithfulness problems |
| Second test | `qwen2.5:3b` indexing, Gemini query, Local mode, split questions | Nobel Prize question worked; some focused retrieval worked | Local retrieval missed obvious source topics such as annus mirabilis and Roosevelt letter |
| Third test | Gemini 3.1 Flash Lite baseline vs GraphRAG-indexed Gemini | GraphRAG became better overall for source-grounded answering | Some language/prompt issues and occasional over-strong political wording |
| Fourth test, Embedding 1 | Full Gemini 3.1 Flash Lite with Gemini embedding, Hybrid mode | Best source-grounded answer so far; strong audit trail | Timeline omitted 1933, Munich was thin, causal depth was compact |
| Fourth test rerun, Embedding 2 | Full Gemini 3.1 Flash Lite with `gemini-embedding-2`, Hybrid mode | Strong source grounding remains; general relativity and Manhattan caution improved | Critical regression in 1905 annus mirabilis; timeline and Munich still weak |

## My Cross-Test Trend

The system improved most when the indexing and query model moved from small local models to Gemini and when Hybrid retrieval was used instead of relying only on Local graph retrieval.

The biggest improvements across the four tests are:

- fewer unsupported claims,
- better source traceability,
- more stable retrieval of the correct Einstein article sections,
- better handling of Nobel Prize and emigration topics,
- more cautious treatment of the Manhattan Project.

The persistent weaknesses are:

- the model still sometimes chooses a weaker timeline even when the source contains better dates,
- Munich remains under-explained,
- broad scientific sections can lose precision,
- the final synthesis can still misclassify a source fact even when the right source chunk is retrieved.

This is important for the thesis argument I would make from these tests: GraphRAG improves traceability and grounding, but retrieval alone does not guarantee perfect synthesis. The generation prompt and evaluation constraints still need to force the model to use the retrieved evidence precisely.

## My Updated Verdict

For the fourth test comparison, I consider the previous Gemini Embedding 1 GraphRAG answer slightly stronger than the new Gemini Embedding 2 rerun.

For the overall project, I would still treat this as the best configuration:

- Gemini 3.1 Flash Lite for indexing,
- Gemini 3.1 Flash Lite for query generation,
- Gemini embeddings for index and query,
- Hybrid retrieval mode,
- strict source-evidence prompting.

However, the current `gemini-embedding-2` rerun shows me that the system needs a stronger answer-generation instruction for scientific enumerations. The prompt or post-processing should explicitly require:

1. Do not count the PhD dissertation as one of the four annus mirabilis papers.
2. List the four 1905 works as photoelectric effect, Brownian motion, special relativity, and mass-energy equivalence.
3. Include `1879`, `1933`, and `1939` when the question asks for life turning points and political emigration.
4. Explain Munich separately in the life-path narrative.
5. Name Roosevelt explicitly when discussing the Roosevelt letter, while keeping Einstein's Manhattan Project role limited to what the source supports.

## My Final Updated Conclusion

The new `gemini-embedding-2` run confirms that the pipeline is source-grounded and retrieves the right evidence, but in my validation it does not outperform the earlier fourth-test GraphRAG answer.

The earlier Embedding 1 GraphRAG answer remains the better final answer because it handled the 1905 scientific section more accurately. The Embedding 2 rerun is still valuable: it shows that the retrieval layer is stable, but it also exposes that final answer quality depends heavily on prompt constraints and evidence-use discipline, not only on embedding model strength.


<a id="magyar"></a>

# Negyedik Teszt Eredményei: Teljes Gemini 3.1 Flash Lite GraphRAG vs Alap Gemini 3.1 Flash Lite

## Tesztkörnyezet

Ebben a tesztben két választ hasonlítottam össze ugyanarra a forráskorlátozott Albert Einstein-promptra.

A célom annak ellenőrzése volt, hogy egy teljesen Gemini-alapú GraphRAG pipeline javítja-e a forrásalapúságot, a tényszerű kontrollt, a kapcsolati következtetést és a nagy kép szintézisét ahhoz képest, amikor ugyanazt a Gemini modellt közvetlenül, indexelt GraphRAG-környezet nélkül használjuk.

## Modell- és Lekérési Beállítás

### Alapmodell

- Modell: Gemini 3.1 Flash Lite
- Mód: közvetlen modellválasz
- Lekérés/indexelés: nincs
- Beágyazások: nincsenek
- Promptbeli korlátozás: csak az indexelt Albert Einstein Wikipédia-cikkből válaszoljon, de az alapmodell ténylegesen nem kapott GraphRAG-forrásrészleteket vagy gráfhivatkozásokat.

### GraphRAG Modell

- Indexelési chat modell: Gemini 3.1 Flash Lite
- Indexelési beágyazási modell: Gemini embedding
- Lekérdezési chat modell: Gemini 3.1 Flash Lite
- Lekérdezési beágyazási modell: Gemini embedding
- Lekérési mód: `auto`, amely `hybrid` módba irányított
- Indexelt forrás: Albert Einstein Wikipédia-cikk
- Lekérési kontextus: rangsorolt nyers forrásszöveg-egységek plusz GraphRAG gráfkontextus
- Hivatkozási stílus: forrásjelölők, például `[S1]`, `[S2]`, a válasz után felsorolt forrásrészletekkel.

## Értékelési Prompt

A prompt előírta, hogy a válasz csak az indexelt Albert Einstein Wikipédia-cikket használja, és kerülje a külső tudást. Ha a forrás nem támaszt alá egy kért pontot, a válasznak ezt kellett írnia: "Not determinable from the source."

A válasznak tartalmaznia kellett továbbá:

- legalább nyolc dátumból vagy évből álló kronológiai láncot,
- életút-narratívát Ulmtól Münchenen, Svájcon és Berlinen át az Egyesült Államokig,
- külön tudományos elemzést az 1905-ös annus mirabilisről, az általános relativitásról és a kvantum-/statisztikus mechanikáról,
- Nobel-díj pontosítást,
- politikai-történelmi elemzést, amely összekapcsolja 1933-at, az emigrációt, az Egyesült Államokat, a Roosevelt-levelet és a Manhattan-tervet,
- egy végső "Source Evidence" szakaszt hat konkrét állítással az indexelt cikkből.

## Alap Gemini 3.1 Flash Lite

### Erősségek

Az alapválasz gördülékeny, tömör és jól szervezett. Az ellenőrzésem alapján követte a kért címsorszerkezetet, és koherens kronológiai láncot adott nyolc releváns évvel: 1879, 1896, 1905, 1915, 1919, 1922, 1933 és 1939.

Néhány helyen erősebb narratív ívet ad, mint a GraphRAG-válasz. Az életút-szakasz elmagyarázza, hogyan kapcsolódik össze Einstein müncheni oktatási kényelmetlensége, svájci akadémiai fejlődése, berlini szakmai felemelkedése és egyesült államokbeli politikai menedéke egy tágabb élettörténetté.

A tudományos szakasz világos és teljes. Helyesen választja szét a négy 1905-ös eredményt, az általános relativitás későbbi jelentőségét, valamint Einstein kvantum- és statisztikus mechanikai hozzájárulásait. A Nobel-díj pontosítása is erős: világosan kimondja, hogy a díjat a fotoelektromos hatásért, nem a relativitásért ítélték oda.

A politikai szakasz tematikusan erős. Összekapcsolja a nácik hatalomra jutását, Einstein emigrációját, a Roosevelt-levelet és korlátozott szerepét a Manhattan-tervben. Megragadja Einstein pacifizmusa és a náci atomkutatástól való félelme közötti feszültséget is.

### Gyengeségek

Az alapválasz forráskorlátozott válaszként sokkal gyengébb. Nem ad ellenőrizhető forrásjelölőket, így én sem tudtam auditálni, mely állítások származtak az indexelt cikkből, és melyek a modell általános tudásából.

Több részlet növeli a hallucináció vagy külső tudás használatának kockázatát:

- az "American citizenship (1940)" és polgárjogi aktivizmus állítása,
- a gravitációs hullámok "later confirmed by the observation of gravitational waves" megfogalmazása,
- "critical opalescence",
- Einstein későbbi "deep regret" érzése a Roosevelt-levél aláírása miatt,
- Time Person of the Century a Source Evidence szakaszban.

Ezek közül néhány igaz lehet, vagy szerepelhet valahol a cikkben, de az alapválasz nem bizonyítja, hogy az indexelt forrásból származtak. Ez azért fontos, mert a prompt kifejezetten csak forrásalapú válaszadást követelt.

A végső "Source Evidence" szakasz is csak lazán kapcsolódik a válaszhoz. A hatodik elem, a Time Person of the Century 1999-ben, nem fontos a kért oksági elemzéshez, és inkább általános életrajzi ténynek tűnik, mint a válaszban felhasznált bizonyítéknak.

### Alapmodell Értékelése

Az értékelésem szerint az alapmodell jól látja a nagy narratív képet, de általános tudású modellként viselkedik. Jobb a csiszolt szintézisben, mint a kontrollált forrásfegyelemben.

Nyílt könyves esszéként erős. Szigorú indexelt-forrás feladatként nem elég ellenőrizhető.

## GraphRAG-Indexelt Gemini 3.1 Flash Lite Hibrid Módban

### Erősségek

A GraphRAG-válasz lényegesen forrásalapúbb. A válaszban végig `[S1]`, `[S2]` és más forrásjelölőket használ, majd a válasz után felsorolja a lekért forrásrészleteket. Ez konkrét ellenőrzési nyomot adott a validálás során.

A válasz tisztán követi a kért szerkezetet:

- kronológiai életút,
- életút-narratíva,
- tudományos elemzés,
- Nobel-díj pontosítás,
- politikai változás és Manhattan-terv szakasz,
- Source Evidence szakasz.

A válasz helyesen azonosítja a fő tudományos és történeti pontokat:

- Einstein 1905-ös munkája tartalmazta a fotoelektromos hatást, a Brown-mozgást, a speciális relativitást és a tömeg-energia ekvivalenciát.
- Az általános relativitást a téridő görbületeként írja le.
- Einstein Nobel-díját a fotoelektromos hatás törvényének tulajdonítja, nem a relativitásnak.
- Az 1939-es Roosevelt-levelet a náci atombomba-kutatással kapcsolatos aggodalomhoz köti.
- Nem állít Einstein közvetlen operatív részvételéről a Manhattan-tervben többet, mint amit a forrás alátámaszt.

A korábbi tesztekhez képest a legerősebb javulást a lekért forrásbizonyíték minőségében láttam. A nyers forrásrészletek tartalmazzák a releváns cikkrészeket a következőkhöz:

- születés, svájci költözés, 1905, Berlin, Nobel-díj,
- 1935-ös végleges letelepedés az Egyesült Államokban,
- 1939-es Szilard/Roosevelt figyelmeztetés,
- Aarau és állampolgárság lemondása,
- általános relativitás,
- 1905-ös tudományos cikkek,
- 1919-es hírnév és az 1921-es amerikai látogatás.

Ez az ellenőrzésem alapján azt mutatja, hogy a teljes Gemini indexelési és Gemini beágyazási beállítás javította a lekérési minőséget, és a Hybrid módot sokkal hatékonyabbá tette.

### Gyengeségek

A GraphRAG-válasz kontrolláltabb, de kevésbé gazdag, mint az alapválasz. Oksági és tematikus magyarázatai helyesek, de tömörek. Gyakran kimondja a kapcsolatot ahelyett, hogy mélyebben kifejtené.

A kronológiai lánc legalább nyolc dátumot tartalmaz, de nem a lehető legjobb dátumválasztással ehhez a prompthoz. Tartalmazza 1935-öt, de kihagyja 1933-at a kronológiai listából, noha a prompt kifejezetten kéri az 1933-as német politikai változás összekapcsolását az emigrációval és az Egyesült Államokkal. A politikai szakasz tárgyalja 1933-at, de az idővonal erősebb lenne, ha 1933 közvetlenül is szerepelne a fő kronológiai mérföldkövek között.

Az életút-narratíva jól említi Ulmot, Svájcot, Berlint és az Egyesült Államokat, de München alulfejlett. A válasz a címsorban azt mondja, hogy "Ulm to Munich", de München tényleges magyarázata rövid, és okságilag kevésbé jelentős, mint az alapválasz Müncheni iskoláztatásról és családi költözésről szóló tárgyalása.

A válasz azt mondja, hogy Einstein "collaborated with fellow refugee scientists" a Roosevelt-levél kontextusában. A lekért forrás támogatja, hogy Einstein és Szilard más menekült tudósokkal együtt figyelmeztették Rooseveltet, de a "collaborated" szót óvatosan kell értelmezni. Elfogadható, de pontosabb megfogalmazás lenne: "Einstein and Szilard, along with other refugee scientists, helped alert Roosevelt."

A forráslista után megjelenő lekért gráfentitások továbbra is tartalmaznak némi széles vagy potenciálisan zajos kontextust, például a második világháború és Berlin olyan leírásait, amelyek általánosítják Einstein szerepét. A végső válasz azonban többnyire a megbízhatóbb `[S]` forrásrészletekre támaszkodik, így ez kevésbé káros, mint a korábbi tesztekben.

### GraphRAG Értékelés

A GraphRAG-válasz jobban illeszkedik a feladat csak-forrás követelményéhez. Nem olyan csiszolt vagy kiterjedt, mint az alapválasz, de megbízhatóbbnak tartom, mert fő állításai lekérhető forrásbizonyítékokhoz kötődnek.

A válasz azt mutatja, hogy a Hybrid mód már közel van ahhoz, amire a projektnek szüksége van: nyers forrásrészleteket kombinál gráfkontextussal, és kontrollált, ellenőrizhető szintézist hoz létre.

## Közvetlen Összehasonlítás

| Kritérium | Alap Gemini 3.1 Flash Lite | GraphRAG Gemini 3.1 Flash Lite Hybrid | Győztes |
|---|---|---|---|
| Promptstruktúra | Erős | Erős | Döntetlen |
| Forrásalapúság | Gyenge; nincs ellenőrzési nyom | Erős; explicit `[S]` hivatkozások és forrásrészletek | GraphRAG |
| Kronológia | Erősebb dátumválasztás | Jó, de kihagyja 1933-at az idővonalból | Alapmodell |
| Életút-narratíva | Gördülékenyebb és magyarázóbb | Forráskontrolláltabb, de München vékony | Alapmodell narratívában, GraphRAG forráskontrollban |
| Tudományos elemzés | Gazdagabb és részletesebb | Pontos és forrással alátámasztott, de tömör | Döntetlen, prioritástól függően |
| Nobel-díj pontosítás | Erős | Erős és idézett | GraphRAG |
| Politikai-történelmi szintézis | Árnyaltabb próza | Óvatosabb és forrás alapján auditálható | GraphRAG megbízhatóságban, alapmodell kifejezésben |
| Hallucinációkontroll | Közepes kockázat | Alacsonyabb kockázat | GraphRAG |
| Nagy kép szintézise | Erősebb narratív ív | Erősebb forrásalapú szintézis | Megosztott |

## Melyik Modell Teljesített Jobban?

Ebben a tesztben a GraphRAG-indexelt Gemini 3.1 Flash Lite modellt tartom összességében jobbnak.

Ennek oka nem az, hogy gördülékenyebb esszét írt. Az alapválasz simább, és néha jobb a narratív magyarázatban. A prompt azonban explicit módon forrásalapú feladat volt egy indexelt cikk felett. Ebben a követelményben a GraphRAG-válasz fölényben van, mert forráshivatkozásokat ad, lekért cikkrészleteket használ, és hatékonyabban kerüli az alá nem támasztott bővítést.

Az alapválasz általános szintézisként lenyűgöző, de nem tudja bizonyítani, hogy állításai kizárólag az indexelt forrásból származtak. Ez gyengébbé teszi GraphRAG-értékelésként.

## Melyik Modell Látja Jobban a Nagy Képet?

A "nagy képnek" két eltérő jelentése van.

Ha a nagy kép csiszolt történeti történetmesélést jelent, az alap Gemini modell kissé erősebb. Természetesebb magyarázó ívvel köti össze a helyszíneket, tudományos szakaszokat és politikai döntéseket.

Ha a nagy kép annak forrásalapú megértését jelenti, hogy az indexelt cikk hogyan kapcsolja össze Einstein életét, tudományát és politikai döntéseit, akkor a GraphRAG modell erősebb. Azonosítja a releváns forrásszakaszokat, és ezekből építi fel a szintézist.

Ehhez a projekthez a második értelmezést tartom fontosabbnak. A projekt nem azt akarja megmutatni, hogy egy modell emlékezetből jó Einstein-esszét tud írni. Azt akarja megmutatni, hogy a tudásgráffal kiegészített lekérés pontosabbá, kontextuálisabbá és nyomon követhetőbbé teheti a generatív válaszokat. Ebben a célban a GraphRAG modell teljesít jobban.

## Saját Fő Megállapítások

A teljes Gemini beállítás jelentős javulásnak tűnik a korábbi tesztekhez képest. A kimenetek alapján a Gemini 3.1 Flash Lite indexeléshez és lekérdezéshez való használata, Gemini beágyazásokkal indexeléshez és lekérdezéshez, jobb forráslekérést és jobb válaszfegyelmet eredményezett.

A Hybrid mód tűnt a legalkalmasabbnak ehhez a prompttípushoz, mert a feladat egyszerre igényel:

- nyers forrásbizonyítékot a tényszerű megalapozáshoz,
- gráf-/kontextusszintézist az életrajz, tudomány és politika közötti kapcsolatokhoz.

A GraphRAG-válasz továbbra is finomításra szorul a magyarázati mélységben és az idővonal-választásban, de szerintem világosabban demonstrálja a projekt alapvető értékét, mint az alapmodell.

## Saját Következtetéseim a Következő Lépésekhez

A jövőbeli tesztekhez megtartanám a teljes Gemini indexelési/lekérdezési profilt, amikor a forrásalapú szintézis minőségét értékelem.

A látottak alapján a Hybrid promptot vagy az utófeldolgozási elvárásokat három módon javítanám:

1. Kötelező legyen 1933 megjelenése a kronológiai láncban, amikor a kérdés politikai emigrációról szól.
2. Az életút-narratíva minden megnevezett helyet legalább egy konkrét, forrással alátámasztott szereppel magyarázzon.
3. A Roosevelt-levélhez óvatosabb megfogalmazást érdemes előnyben részesíteni, például "helped alert" vagy "helped stimulate U.S. atomic research", erősebb oksági állítások helyett.

Szakdolgozati értékeléshez ezt a tesztet erős bizonyítékként mutatnám be arra, hogy a GraphRAG javítja az auditálhatóságot és a forrásfegyelmet. Sikeresebb futásként kezelném, mint a korábbi helyi modell- és Local-módú kísérleteket.

## Saját Végső Ítélet

Átfogó győztes: GraphRAG-indexelt Gemini 3.1 Flash Lite Hybrid módban.

Legjobb narratív próza: alap Gemini 3.1 Flash Lite.

Legjobb forrásalapú válasz: GraphRAG Gemini 3.1 Flash Lite Hybrid.

A szakdolgozati projekthez legjobb illeszkedés: GraphRAG Gemini 3.1 Flash Lite Hybrid, mert az ellenőrzésem alapján jobban demonstrálja a GraphRAG tervezett értékét: strukturált lekérés, forráskövethetőség, kevesebb alá nem támasztott állítás és auditálható, több részből álló szintézis.

---

# Negyedik Teszt Újrafuttatása: Gemini 3.1 Flash Lite GraphRAG Gemini Embedding 2-vel

## Újrafuttatási Környezet

A negyedik tesztet újrafuttattam, miután a Gemini beágyazási modell `gemini-embedding-001` / Gemini Embedding 1 viselkedésről `gemini-embedding-2`-re váltott.

Az újrafuttatás ezt használta:

- Indexelési chat modell: Gemini 3.1 Flash Lite
- Indexelési beágyazási modell: `gemini-embedding-2`
- Lekérdezési chat modell: Gemini 3.1 Flash Lite
- Lekérdezési beágyazási modell: `gemini-embedding-2`
- Lekérési mód: `auto`, amely Hybrid-jellegű forrás-plusz-gráf válaszadásra irányított
- Forrásdokumentum: indexelt Albert Einstein Wikipédia-cikk
- Prompt: ugyanaz a forráskorlátozott, több részből álló Einstein-elemző prompt

Az újrafuttatás célja az volt, hogy ellenőrizzem: az újabb beágyazási modell javítja-e a lekérési minőséget, a forrásalapúságot és a szintézis minőségét a korábbi negyedik teszt GraphRAG-válaszához képest.

## Eredményösszefoglaló

A `gemini-embedding-2` újrafuttatás továbbra is egyértelműen forrásalapú és auditálható, de nem láttam egyértelmű javulásnak az előző Gemini Embedding 1 futáshoz képest.

A lekért forrásrészletek többnyire ugyanazok a nagy értékű részletek, mint korábban:

- `[S1]` lefedi az életrajzi áttekintést, Svájcot, 1905-öt, Berlint, a Nobel-díjat és az emigrációt.
- `[S2]` lefedi az Egyesült Államokat, az Institute for Advanced Study-t, a második világháborút, Szilardot és a Manhattan-terv szakaszt.
- `[S3]` lefedi Aaraut, az 1896-os érettségit és az állampolgárságról való lemondást.
- `[S5]` lefedi az általános relativitást mint a téridő görbületét.
- `[S6]` lefedi az 1905-ös tudományos cikkeket.
- `[S7]` lefedi az 1919-es hírnevet és az 1921-es amerikai látogatást.
- `[S8]` lefedi a pacifizmust és kapcsolódó politikai nézeteket.

Ez azt jelenti, hogy a lekérési réteg továbbra is megtalálja a megfelelő cikkrészeket. A fő különbségek a válaszszintézisben jelentek meg, nem a nyers forráselérhetőségben.

## A Gemini Embedding 2 Újrafuttatás Erősségei

A válasz jól strukturált, és követi a kért szakaszokat:

- kronológiai lánc,
- életút-narratíva,
- tudományos elemzés,
- Nobel-díj pontosítás,
- politikai változás és emigráció,
- forrásbizonyíték.

A forrásfegyelem erős. A válasz a legtöbb állításhoz következetesen `[S]` hivatkozásokat kapcsol, és elkerüli a hosszú, alá nem támasztott bővítéseket. Ezt továbbra is jelentős javulásnak tartom egy közvetlen alapválaszhoz képest, amely nem ad lekérési ellenőrzési nyomot.

A Nobel-díj pontosítása kiváló. Helyesen állítja, hogy Einstein nem a relativitásért kapta a Nobel-díjat, és idézi a fotoelektromos hatásra vonatkozó megfogalmazást az `[S1]` forrásból.

Az általános relativitás alszakasz egy szempontból erősebb, mint az előző GraphRAG-válasz: használja a téridő görbületéről szóló lekért forrást, és összekapcsolja azt az 1919-es nyilvános hírnévvel. Ez egyszerre adja meg az olvasónak a fogalmi pontot és a történeti recepciót.

A Manhattan-terv megfogalmazása óvatos. A válasz azt mondja, hogy a forrás Einstein és Szilard amerikaiaknak szóló figyelmeztetését támasztja alá a náci atomkutatásról, de nem állít részletes operatív részvételt a Manhattan-tervben. Ez biztonságosabb, mint az olyan erősebb oksági állítások, hogy Einstein közvetlenül elindította a projektet vagy részt vett benne.

A forrásbizonyíték-szakasz releváns és közvetlenül kapcsolódik a válaszhoz. Elkerüli azt a korábbi alapválaszbeli problémát, amit láttam: periférikus tényeket sorolt bizonyítékként.

## Gyengeségek és Visszalépések

A legnagyobb visszalépést az 1905-ös annus mirabilis szakaszban találtam.

Az újrafuttatás szerint a négy fő munka:

- fotoelektromos hatás,
- Brown-mozgás,
- speciális relativitás, amely tartalmazza az `E=mc^2`-t,
- PhD-disszertáció a molekuláris dimenziókról.

Ez nem a legjobb forráshű megfogalmazás. Az indexelt forrás megkülönbözteti a PhD-disszertációt a négy másik híres 1905-ös munkától. Az értékelésem szerint a négy annus mirabilis munkát így kellene megadni:

- fotoelektromos hatás,
- Brown-mozgás,
- speciális relativitás,
- tömeg-energia ekvivalencia.

A PhD-disszertáció releváns 1905-ös esemény, de nem helyettesítheti a tömeg-energia ekvivalenciát a négy annus mirabilis eredmény egyikeként. Ez jelentős tudományos elemzési hiba, mert a prompt kifejezetten a négy fő 1905-ös eredményt kéri.

A kronológiai lánc darabszámban elfogadható, de dátumválasztásban gyengébb. Nyolc dátumot tartalmaz, de kihagyja:

- `1879`, Einstein ulmi születését,
- `1933`, a németországi politikai fordulópontot,
- `1939`, a Roosevelt-levél kontextusát.

Ehelyett tartalmazza `1929` pacifizmust. Ez a dátum tematikusan releváns, de ehhez a konkrét prompthoz `1933` és `1939` központibb. Az előző Embedding 1 GraphRAG-válasz is kihagyta `1933`-at az idővonalból, de legalább tartalmazta `1879`-et; az újrafuttatás elveszíti az életút kezdőpontját.

Az Ulm-München rész továbbra is vékony. A válasz a címsorban azt mondja, "Ulm to Munich", de nem magyarázza érdemben München szerepét. Gyorsan ugrik a Német Birodalomból Svájcba. Ez megismétli a korábbi GraphRAG-válasz egyik fő gyengeségét.

A kvantumelmélet és statisztikus mechanika alszakasz túl tömör. Megemlíti, hogy Einstein jelentős hozzájárulásokat tett, és később megpróbálta cáfolni az elfogadott kvantumértelmezéseket, de nem magyarázza világosan kvantum-/statisztikus munkájának forrással alátámasztott tartalmát. Az előző Embedding 1 válasz itt jobb volt, mert expliciten említette a fénykvantumokat, a fotoelektromos hatást, a molekuláris fizikát, a statisztikus leírásokat és a Brown-mozgást.

A politikai szakasz óvatos, de kissé hiányos. Amerikaiak és Washington figyelmeztetésére utal, de explicit módon megnevezhetné Franklin D. Roosevelt elnököt, mert a prompt kifejezetten a Rooseveltnek írt levélről kérdez.

## Összehasonlítás az Előző Negyedik Teszt GraphRAG-Válaszával

| Kritérium | Előző GraphRAG Gemini Embedding 1-gyel | Újrafuttatás Gemini Embedding 2-vel | Győztes |
|---|---|---|---|
| Forráslekérés | Erős; lekérte a kulcsfontosságú Einstein-részleteket | Erős; többnyire ugyanazokat a kulcsfontosságú részleteket kérte le | Döntetlen |
| Forráshivatkozások | Erős `[S]` hivatkozási fegyelem | Erős `[S]` hivatkozási fegyelem | Döntetlen |
| Kronológiai lánc | Jó, de kihagyta 1933-at és 1939-et | Darabszámban jó, de kihagyja 1879-et, 1933-at és 1939-et | Embedding 1 |
| Életút-narratíva | Forráskontrollált, de München vékony volt | Hasonló, de München még kevésbé fejlett | Embedding 1 |
| 1905 annus mirabilis | Helyesen sorolta fel a négy fő munkát, beleértve a tömeg-energia ekvivalenciát | Hibásan a PhD-disszertációval helyettesíti a tömeg-energia ekvivalenciát | Embedding 1 |
| Általános relativitás | Pontos, tömör | Kissé gazdagabb; tartalmazza a téridő görbületét és az 1919-es hírnevet | Embedding 2 |
| Kvantum-/statisztikus mechanika | Konkrétabb | Túl tömör | Embedding 1 |
| Nobel-díj pontosítás | Erős és idézett | Erős és idézett | Döntetlen |
| 1933/emigráció/Roosevelt/Manhattan-terv | Explicitebb Roosevelt kapcsán, de kissé erősebb megfogalmazás | Óvatosabb a korlátokkal kapcsolatban, de kevésbé explicit Roosevelt kapcsán | Döntetlen, eltérő erősségekkel |
| Nagy kép szintézise | Tömör, de koherens | Tömör, forrásalapú, de tudományosan kevésbé teljes | Embedding 1 összességében |

## Melyik Negyedik Tesztes GraphRAG-Verzió Teljesített Jobban?

Erre a konkrét promptra az előző, Gemini Embedding 1-et használó GraphRAG-választ tartom kissé jobbnak összességében.

Ennek oka a `gemini-embedding-2` újrafuttatás tudományos elemzési visszalépése. A prompt kifejezetten a négy fő 1905-ös eredményt kéri, az újrafuttatás pedig gyengébb választ ad azzal, hogy a tömeg-energia ekvivalenciát a PhD-disszertációval helyettesíti.

Ez nem jelenti azt, hogy a `gemini-embedding-2` rosszabb beágyazási modell. A lekért forrásrészletek továbbra is nagyon relevánsak, és az entitáskontextus helyenként tisztábbnak tűnik. A probléma az, hogy a végső válaszszintézis nem használta elég gondosan a lekért 1905-ös forrást.

Röviden, az újrafuttatásról ezt vontam le:

- A `gemini-embedding-2` nem rontotta el a forráslekérést.
- Nem javította egyértelműen a végső választ.
- A végső válasz visszalépett egy kritikus tudományos követelményben.

## Összehasonlítás Mind a Négy Teszten Át

| Teszt | Beállítás | Fő eredmény | Fő korlát |
|---|---|---|---|
| Első teszt | `qwen2.5:3b` alapmodell vs `qwen2.5:3b` GraphRAG | A GraphRAG jobban látta a kért szerkezetet, de a tényszerű megbízhatóság gyenge volt | Kitalált dátumok, gyenge idézetek, súlyos forráshűségi problémák |
| Második teszt | `qwen2.5:3b` indexelés, Gemini lekérdezés, Local mód, bontott kérdések | A Nobel-díj kérdés működött; néhány fókuszált lekérés működött | A Local lekérés kihagyott nyilvánvaló forrástémákat, például az annus mirabilist és a Roosevelt-levelet |
| Harmadik teszt | Gemini 3.1 Flash Lite alapmodell vs GraphRAG-indexelt Gemini | A GraphRAG összességében jobb lett a forrásalapú válaszadásban | Néhány nyelvi/promptprobléma és időnként túl erős politikai megfogalmazás |
| Negyedik teszt, Embedding 1 | Teljes Gemini 3.1 Flash Lite Gemini beágyazással, Hybrid mód | Eddigi legjobb forrásalapú válasz; erős ellenőrzési nyom | Az idővonal kihagyta 1933-at, München vékony volt, az oksági mélység tömör volt |
| Negyedik teszt újrafuttatás, Embedding 2 | Teljes Gemini 3.1 Flash Lite `gemini-embedding-2`-vel, Hybrid mód | Az erős forrásalapúság megmarad; javult az általános relativitás és a Manhattan-óvatosság | Kritikus visszalépés az 1905-ös annus mirabilisben; az idővonal és München továbbra is gyenge |

## Saját Teszteken Átívelő Trend

A rendszer akkor javult a legtöbbet, amikor az indexelési és lekérdezési modell kis helyi modellekről Geminire váltott, és amikor a Local gráflekérés helyett Hybrid lekérésre támaszkodott.

A négy teszten átívelő legnagyobb javulások:

- kevesebb alá nem támasztott állítás,
- jobb forráskövethetőség,
- az Einstein-cikk megfelelő részeinek stabilabb lekérése,
- a Nobel-díj és az emigráció témáinak jobb kezelése,
- óvatosabb kezelés a Manhattan-terv kapcsán.

A tartós gyengeségek:

- a modell néha továbbra is gyengébb idővonalat választ, még akkor is, ha a forrás jobb dátumokat tartalmaz,
- München továbbra is alulmagyarázott,
- a széles tudományos szakaszok veszíthetnek a precizitásból,
- a végső szintézis továbbra is félreosztályozhat egy forrástényt akkor is, ha a megfelelő forrásrészlet le lett kérve.

Ez fontos ahhoz a szakdolgozati érvhez, amit ezekből a tesztekből levonnék: a GraphRAG javítja a követhetőséget és a megalapozottságot, de a lekérés önmagában nem garantál tökéletes szintézist. A generálási promptnak és az értékelési korlátoknak továbbra is ki kell kényszeríteniük, hogy a modell pontosan használja a lekért bizonyítékot.

## Saját Frissített Ítélet

A negyedik teszt összehasonlításában a korábbi Gemini Embedding 1 GraphRAG-választ kissé erősebbnek tartom, mint az új Gemini Embedding 2 újrafuttatást.

Az egész projektre nézve továbbra is ezt kezelném a legjobb konfigurációként:

- Gemini 3.1 Flash Lite indexeléshez,
- Gemini 3.1 Flash Lite lekérdezésgeneráláshoz,
- Gemini beágyazások indexeléshez és lekérdezéshez,
- Hybrid lekérési mód,
- szigorú forrásbizonyítékot kérő promptolás.

Ugyanakkor a jelenlegi `gemini-embedding-2` újrafuttatás megmutatta számomra, hogy a rendszernek erősebb válaszgenerálási instrukcióra van szüksége a tudományos felsorolásokhoz. A promptnak vagy az utófeldolgozásnak explicit módon elő kellene írnia:

1. Ne számolja a PhD-disszertációt a négy annus mirabilis cikk egyikének.
2. A négy 1905-ös munkát így sorolja: fotoelektromos hatás, Brown-mozgás, speciális relativitás és tömeg-energia ekvivalencia.
3. Tartalmazza `1879`-et, `1933`-at és `1939`-et, amikor a kérdés életfordulópontokról és politikai emigrációról szól.
4. Magyarázza el külön Münchent az életút-narratívában.
5. Nevezze meg explicit módon Rooseveltet a Roosevelt-levél tárgyalásakor, miközben Einstein Manhattan-tervben betöltött szerepét a forrás által alátámasztott mértékre korlátozza.

## Saját Végső Frissített Következtetés

Az új `gemini-embedding-2` futás megerősíti, hogy a pipeline forrásalapú és a megfelelő bizonyítékot kéri le, de az ellenőrzésem alapján nem teljesíti felül a korábbi negyedik tesztes GraphRAG-választ.

A korábbi Embedding 1 GraphRAG-válasz marad a jobb végső válasz, mert pontosabban kezelte az 1905-ös tudományos szakaszt. Az Embedding 2 újrafuttatás továbbra is értékes: megmutatja, hogy a lekérési réteg stabil, de azt is feltárja, hogy a végső válasz minősége erősen függ a promptkorlátoktól és a bizonyítékhasználati fegyelemtől, nem csak a beágyazási modell erejétől.
