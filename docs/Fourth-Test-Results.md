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
