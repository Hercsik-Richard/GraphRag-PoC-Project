# Fourth Test Results: Full Gemini 3.1 Flash Lite GraphRAG vs Baseline Gemini 3.1 Flash Lite

## Test Context

This test compared two answers to the same source-restricted Albert Einstein prompt.

The goal was to evaluate whether a fully Gemini-based GraphRAG pipeline improves source grounding, factual control, relationship reasoning, and big-picture synthesis compared with using the same Gemini model directly without the indexed GraphRAG context.

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

The baseline answer is fluent, compact, and well organized. It follows the requested heading structure and gives a coherent chronological chain with eight relevant years: 1879, 1896, 1905, 1915, 1919, 1922, 1933, and 1939.

It also provides a stronger narrative flow than the GraphRAG answer in some places. The life-path section explains how Einstein's educational discomfort in Munich, academic development in Switzerland, professional rise in Berlin, and political refuge in the United States connect into one broader life story.

The scientific section is clear and complete. It correctly separates the four 1905 achievements, the later importance of general relativity, and Einstein's quantum/statistical mechanics contributions. The Nobel Prize clarification is also strong: it clearly states that the prize was awarded for the photoelectric effect, not relativity.

The political section is thematically strong. It connects the Nazi rise to power, Einstein's emigration, the Roosevelt letter, and his limited role in the Manhattan Project. It also captures the tension between Einstein's pacifism and his fear of Nazi atomic research.

### Weaknesses

The baseline answer is much weaker as a source-restricted answer. It provides no verifiable source markers, so the reader cannot audit which claims came from the indexed article and which came from the model's general knowledge.

Several details increase hallucination or outside-knowledge risk:

- the claim about "American citizenship (1940)" and civil rights activism,
- gravitational waves being "later confirmed by the observation of gravitational waves",
- "critical opalescence",
- Einstein later expressing "deep regret" for signing the Roosevelt letter,
- Time's Person of the Century in the Source Evidence section.

Some of these may be true or may appear somewhere in the article, but the baseline answer does not prove that they came from the indexed source. This matters because the prompt explicitly required source-only answering.

The final "Source Evidence" section is also only loosely tied to the answer. The sixth item, Time's Person of the Century in 1999, is not important for the requested causal analysis and looks like a generic biographical fact rather than evidence used in the answer.

### Baseline Assessment

The baseline model sees the big-picture narrative well, but it behaves like a general-knowledge model. It is better at polished synthesis than at controlled source discipline.

For an open-book essay, it is strong. For a strict indexed-source task, it is not sufficiently auditable.

## GraphRAG-Indexed Gemini 3.1 Flash Lite In Hybrid Mode

### Strengths

The GraphRAG answer is substantially more source-grounded. It uses `[S1]`, `[S2]`, and other source markers throughout the answer, then lists the retrieved source excerpts after the response. This gives the user a concrete audit trail.

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

The strongest improvement over earlier tests is the quality of the retrieved source evidence. The raw source excerpts include the relevant article sections for:

- birth, Swiss move, 1905, Berlin, Nobel Prize,
- 1935 permanent settlement in the United States,
- 1939 Szilard/Roosevelt warning,
- Aarau and citizenship renunciation,
- general relativity,
- 1905 scientific papers,
- 1919 fame and intellectual icon status.

This shows that the full Gemini indexing and Gemini embedding setup improved retrieval quality and made Hybrid mode much more effective.

### Weaknesses

The GraphRAG answer is more controlled, but less rich than the baseline answer. Its causal and thematic explanations are correct but compact. It often states the connection instead of developing it in depth.

The chronological chain has at least eight dates, but it is not the best possible selection for the prompt. It includes 1935, but omits 1933 from the chronological list, even though the prompt specifically asks to connect the 1933 political change in Germany to emigration and the United States. The political section covers 1933, but the timeline would be stronger if 1933 appeared directly as one of the key chronological milestones.

The life-path narrative mentions Ulm, Switzerland, Berlin, and the United States well, but Munich is underdeveloped. The answer says "Ulm to Munich" in the heading, but the actual explanation of Munich is brief and not as causally meaningful as the baseline answer's discussion of Munich schooling and family movement.

The answer says Einstein "collaborated with fellow refugee scientists" in the Roosevelt-letter context. The retrieved source supports Einstein and Szilard acting along with other refugee scientists, but "collaborated" should be interpreted cautiously. It is acceptable, but a more precise wording would be "Einstein and Szilard, along with other refugee scientists, helped alert Roosevelt."

The retrieved graph entities after the source list still contain some broad or potentially noisy context, such as World War II and Berlin descriptions that generalize Einstein's role. However, the final answer mostly relies on the more reliable `[S]` source excerpts, so this is less damaging than in earlier tests.

### GraphRAG Assessment

The GraphRAG answer is better aligned with the task's source-only requirement. It is not as polished or expansive as the baseline, but it is more trustworthy because its main claims are tied to retrievable source evidence.

The answer shows that Hybrid mode is now doing what the project needs it to do: combine raw source excerpts with graph context and produce a controlled, auditable synthesis.

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

The GraphRAG-indexed Gemini 3.1 Flash Lite model performed better overall for this test.

The reason is not that it wrote a more fluent essay. The baseline answer is smoother and sometimes better at narrative explanation. However, the prompt was explicitly a source-only task over an indexed article. Under that requirement, the GraphRAG answer is superior because it provides source citations, uses retrieved article excerpts, and avoids unsupported expansion more effectively.

The baseline answer is impressive as a general synthesis, but it cannot prove that its claims came only from the indexed source. That makes it weaker for a GraphRAG evaluation.

## Which Model Sees The Big Picture Better?

There are two different meanings of "big picture."

If big picture means polished historical storytelling, the baseline Gemini model is slightly stronger. It connects the locations, scientific phases, and political decisions with more natural explanatory flow.

If big picture means source-grounded understanding of how the indexed article connects Einstein's life, science, and political decisions, the GraphRAG model is stronger. It identifies the relevant source passages and builds the synthesis from them.

For this project, the second interpretation matters more. The project is not trying to show that a model can write a good Einstein essay from memory. It is trying to show that knowledge-graph-enhanced retrieval can make generative answers more accurate, contextual, and traceable. On that goal, the GraphRAG model performs better.

## Main Findings

The full Gemini setup appears to be a meaningful improvement over earlier tests. Using Gemini 3.1 Flash Lite for indexing and querying, with Gemini embeddings for both index and query, produced better source retrieval and better answer discipline.

Hybrid mode is now the most suitable mode for this kind of prompt because the task requires both:

- raw source evidence for factual grounding,
- graph/context synthesis for relationships across biography, science, and politics.

The GraphRAG answer still needs refinement in explanatory depth and timeline selection, but it demonstrates the core value of the project more clearly than the baseline.

## Recommendations

For future tests, keep the full Gemini indexing/query profile when evaluating source-grounded synthesis quality.

Improve the Hybrid prompt or post-processing expectations in three ways:

1. Require 1933 to appear in the chronological chain when the question asks about political emigration.
2. Require the life-path narrative to explain each named place with at least one concrete source-supported role.
3. Prefer cautious wording for the Roosevelt letter, such as "helped alert" or "helped stimulate U.S. atomic research", rather than stronger causal claims.

For thesis evaluation, this test is strong evidence that GraphRAG improves auditability and source discipline. It should be presented as a more successful run than the earlier local-model and Local-mode experiments.

## Final Verdict

Overall winner: GraphRAG-indexed Gemini 3.1 Flash Lite in Hybrid mode.

Best narrative prose: baseline Gemini 3.1 Flash Lite.

Best source-grounded answer: GraphRAG Gemini 3.1 Flash Lite Hybrid.

Best fit for the thesis project: GraphRAG Gemini 3.1 Flash Lite Hybrid, because it better demonstrates the intended value of GraphRAG: structured retrieval, source traceability, reduced unsupported claims, and auditable multi-part synthesis.

---

# Fourth Test Rerun: Gemini 3.1 Flash Lite GraphRAG With Gemini Embedding 2

## Rerun Context

The fourth test was rerun after switching the Gemini embedding model from `gemini-embedding-001` / Gemini Embedding 1 behavior to `gemini-embedding-2`.

The rerun used:

- Indexing chat model: Gemini 3.1 Flash Lite
- Indexing embedding model: `gemini-embedding-2`
- Query chat model: Gemini 3.1 Flash Lite
- Query embedding model: `gemini-embedding-2`
- Retrieval mode: `auto`, routed to Hybrid-style source-plus-graph answering
- Source document: indexed Albert Einstein Wikipedia article
- Prompt: same source-restricted, multi-part Einstein analysis prompt

The goal of this rerun was to check whether the newer embedding model improves retrieval quality, source grounding, and synthesis quality compared with the earlier fourth-test GraphRAG answer.

## Result Summary

The `gemini-embedding-2` rerun remains clearly source-grounded and auditable, but it is not an unambiguous improvement over the previous Gemini Embedding 1 run.

The retrieved source chunks are mostly the same high-value chunks as before:

- `[S1]` covers the biography overview, Switzerland, 1905, Berlin, Nobel Prize, and emigration.
- `[S2]` covers the United States, Institute for Advanced Study, World War II, Szilard, and the Manhattan Project section.
- `[S3]` covers Aarau, the 1896 graduation, and citizenship renunciation.
- `[S5]` covers general relativity as curvature of spacetime.
- `[S6]` covers the 1905 scientific papers.
- `[S7]` covers 1919 fame and the 1921 U.S. visit.
- `[S8]` covers pacifism and related political views.

This means the retrieval layer is still finding the right article sections. The main differences appear in answer synthesis, not in raw source availability.

## Strengths Of The Gemini Embedding 2 Rerun

The answer is well structured and follows the requested sections:

- chronological chain,
- life-path narrative,
- scientific analysis,
- Nobel Prize clarification,
- political change and emigration,
- source evidence.

The source discipline is strong. The answer consistently attaches `[S]` citations to most claims and avoids long unsupported expansions. This is still a major improvement over a direct baseline answer with no retrieval audit trail.

The Nobel Prize clarification is excellent. It correctly states that Einstein did not receive the Nobel Prize for relativity and cites the photoelectric effect wording from `[S1]`.

The general relativity subsection is stronger than the previous GraphRAG answer in one respect: it uses the retrieved source about spacetime curvature and connects it to 1919 public fame. This gives the reader both the conceptual point and the historical reception point.

The Manhattan Project wording is cautious. The answer says the source supports Einstein and Szilard alerting Americans to Nazi atomic research, but does not assert detailed operational involvement in the Manhattan Project. This is safer than stronger causal claims such as saying Einstein directly launched or participated in the project.

The source evidence section is relevant and directly tied to the answer. It avoids the previous baseline problem of listing peripheral facts as evidence.

## Weaknesses And Regressions

The biggest regression is in the 1905 annus mirabilis section.

The rerun says the four major works were:

- photoelectric effect,
- Brownian motion,
- special relativity containing `E=mc^2`,
- PhD dissertation on molecular dimensions.

This is not the best source-faithful formulation. The indexed source distinguishes the PhD dissertation from the four other famous 1905 works. The four annus mirabilis works should be stated as:

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

The previous GraphRAG answer using Gemini Embedding 1 performed slightly better overall as an answer to this exact prompt.

The reason is the scientific-analysis regression in the `gemini-embedding-2` rerun. The prompt explicitly asks for the four main 1905 achievements, and the rerun gives a weaker answer by replacing mass-energy equivalence with the PhD dissertation.

That does not mean `gemini-embedding-2` is worse as an embedding model. The retrieved source chunks are still highly relevant, and the entity context appears somewhat cleaner in places. The problem is that the final answer synthesis did not use the retrieved 1905 source carefully enough.

In short:

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

## Cross-Test Trend

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

This is important for the thesis argument: GraphRAG improves traceability and grounding, but retrieval alone does not guarantee perfect synthesis. The generation prompt and evaluation constraints still need to force the model to use the retrieved evidence precisely.

## Updated Verdict

For the fourth test comparison, the previous Gemini Embedding 1 GraphRAG answer is slightly stronger than the new Gemini Embedding 2 rerun.

For the overall project, the best configuration is still:

- Gemini 3.1 Flash Lite for indexing,
- Gemini 3.1 Flash Lite for query generation,
- Gemini embeddings for index and query,
- Hybrid retrieval mode,
- strict source-evidence prompting.

However, the current `gemini-embedding-2` rerun shows that the system needs a stronger answer-generation instruction for scientific enumerations. The prompt or post-processing should explicitly require:

1. Do not count the PhD dissertation as one of the four annus mirabilis papers.
2. List the four 1905 works as photoelectric effect, Brownian motion, special relativity, and mass-energy equivalence.
3. Include `1879`, `1933`, and `1939` when the question asks for life turning points and political emigration.
4. Explain Munich separately in the life-path narrative.
5. Name Roosevelt explicitly when discussing the Roosevelt letter, while keeping Einstein's Manhattan Project role limited to what the source supports.

## Final Updated Conclusion

The new `gemini-embedding-2` run confirms that the pipeline is source-grounded and retrieves the right evidence, but it does not outperform the earlier fourth-test GraphRAG answer.

The earlier Embedding 1 GraphRAG answer remains the better final answer because it handled the 1905 scientific section more accurately. The Embedding 2 rerun is still valuable: it shows that the retrieval layer is stable, but it also exposes that final answer quality depends heavily on prompt constraints and evidence-use discipline, not only on embedding model strength.
