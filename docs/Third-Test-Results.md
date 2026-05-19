# Third Test Results

## Test Context

This test compares two answers generated with the same underlying model family, **Gemini 3.1 Flash Lite**, under two different usage modes:

- **Baseline model:** Gemini 3.1 Flash Lite used directly for the query.
- **GraphRAG-indexed model:** Gemini 3.1 Flash Lite used both for indexing and for querying through the GraphRAG pipeline.

The indexed source was the Albert Einstein Wikipedia article. The goal of the test was to evaluate not only factual recall, but also source grounding, prompt following, causal reasoning, and the ability to synthesize a broad historical-scientific picture.

## Original Prompt

```text
Answer strictly and exclusively from the indexed Albert Einstein Wikipedia article. Do not use outside knowledge, assumptions, or facts not supported by the indexed source. If the indexed source does not contain enough information for any requested point, write: “Not determinable from the source.”

Write a concise but detailed analytical answer explaining how the turning points in Albert Einstein’s life, his scientific achievements, and his political-historical decisions are connected.

Your answer must include:

1. A chronological chain with at least 8 specific dates or years.
   - For each date/year, explain why it matters.
   - Do not merely list events; explain the causal or thematic connection to Einstein’s broader life path.

2. A clear life-path narrative:
   - Explain how Einstein’s path leads from Ulm to Munich, then to Switzerland, Berlin, and finally the United States.
   - For each location, explain its role in his personal, intellectual, professional, or political development.

3. A separate scientific analysis with three clearly labeled subsections:
   a. The four main achievements of the 1905 annus mirabilis.
   b. The later role and historical significance of general relativity.
   c. Einstein’s contributions to quantum theory and statistical mechanics.

4. A Nobel Prize clarification:
   - Explain why it is misleading to say that Einstein received the Nobel Prize for relativity.
   - State what the source says the prize was awarded for.
   - Explain the connection between this distinction and the scientific reception of relativity, if supported by the source.

5. A political-historical analysis:
   - Connect the 1933 political change in Germany to Einstein’s emigration and settlement in the United States.
   - Explain how this connects to the letter addressed to President Franklin D. Roosevelt.
   - Clarify Einstein’s role and limits in relation to the Manhattan Project, if the source supports this.
```

## Evaluation Criteria

The answers were evaluated according to the following criteria:

- **Prompt compliance:** Whether the answer follows all required sections and constraints.
- **Source grounding:** Whether the answer avoids unsupported claims and stays within the indexed Wikipedia article.
- **Chronological reasoning:** Whether the timeline is coherent and each date is connected to Einstein’s broader life path.
- **Causal and thematic synthesis:** Whether the answer explains relationships rather than merely listing facts.
- **Scientific separation:** Whether the answer clearly distinguishes the 1905 annus mirabilis, general relativity, quantum theory, and statistical mechanics.
- **Political-historical synthesis:** Whether the 1933 German political turn, emigration, the Roosevelt letter, and the Manhattan Project are connected accurately.
- **Big-picture understanding:** Whether the answer presents Einstein’s life as an integrated historical, scientific, and political trajectory.

## Model 1: Baseline Gemini 3.1 Flash Lite

### Strengths

- The baseline answer is fluent, coherent, and reads like a polished analytical essay.
- It gives a strong chronological chain with eight dates: 1879, 1896, 1905, 1914, 1919, 1922, 1933, and 1955.
- It gives a better narrative explanation of Einstein’s geographical path than the GraphRAG answer. The movement from Ulm and Munich to Switzerland, Berlin, and the United States is described as a search for academic freedom and intellectual environments.
- It clearly separates the main scientific categories requested by the prompt:
  - the 1905 annus mirabilis,
  - general relativity,
  - quantum theory and statistical mechanics.
- It gives a strong Nobel Prize clarification and correctly states that the award was for the photoelectric effect, not relativity.
- It gives a nuanced political section by explaining that Einstein signed the Roosevelt letter but did not directly participate in the Manhattan Project.
- It captures the broader tension between Einstein’s pacifism and his fear of Nazi nuclear research.

### Weaknesses

- The answer is less visibly source-grounded. It does not provide inline source references, even though the prompt emphasizes exclusive reliance on the indexed article.
- Several details increase hallucination risk or at least make the answer harder to audit:
  - “American meritocracy and freedom of speech”
  - Einstein as a critic of “the nation’s racism”
  - gravitational waves “confirmed in 2016”
  - the phrase “God does not play dice”
  - the “one great mistake” quote
  - Time’s Person of the Century in 1999
- Some of these facts may be true or may appear in the article, but they are not necessary for the prompt and make the answer feel less disciplined.
- The “Source Evidence” section contains some claims that are peripheral to the requested analysis, especially Time’s Person of the Century.
- It does not explicitly say “Not determinable from the source” anywhere, even in areas where source support could be uncertain.
- The answer sometimes prioritizes breadth over controlled source fidelity.

## Model 2: GraphRAG-Indexed Gemini 3.1 Flash Lite

### Strengths

- The GraphRAG answer is more explicitly source-grounded through references such as `[Data: Sources (0)]`, `[Data: Sources (2)]`, and similar source markers.
- It follows the required structure closely:
  - chronological milestones,
  - geographic and professional development,
  - scientific analysis,
  - Nobel Prize clarification,
  - political-historical analysis,
  - source evidence.
- It gives a clear timeline with eight relevant dates: 1879, 1895, 1900, 1905, 1915, 1922, 1933, and 1939.
- It provides a compact but coherent life-path synthesis from Ulm and Munich through Switzerland and Berlin to the United States.
- It directly connects 1933, Nazi political power, antisemitism, emigration, the Roosevelt letter, and the Manhattan Project.
- It correctly states the core Nobel Prize distinction: Einstein was not awarded the Nobel Prize for relativity, but especially for the law of the photoelectric effect.
- It gives a better audit trail than the baseline model because major claims are tied to indexed source chunks.

### Weaknesses

- The answer is in Hungarian, even though the prompt was in English. This is a significant formatting and prompt-compliance issue.
- The causal analysis is more compressed than in the baseline answer. It often states connections correctly but does not always develop them deeply.
- Some source markers are attached only to certain claims, while other detailed claims are left without explicit citations.
- It omits the 1919 solar eclipse confirmation, which would have strengthened the discussion of the historical significance of general relativity.
- It states that the Roosevelt letter “launched” the Manhattan Project, which is somewhat stronger than the more cautious formulation that it helped stimulate or catalyze the project.
- The statement that Einstein later considered the letter one of his great mistakes may be source-supported, but it is not tied clearly enough to the evidence section.
- The “Source Evidence” section is stronger than the baseline answer’s evidence section, but it is still relatively minimal.

## Direct Comparison

### Prompt Compliance

The **GraphRAG-indexed model** performs better structurally because it follows the requested sections more consistently and includes source markers. However, it fails one important implicit expectation: the prompt is written in English, but the answer is in Hungarian.

The **baseline model** answers in English and has a polished structure, but it is less disciplined about source restriction and includes more potentially unsupported details.

Overall winner for prompt compliance: **GraphRAG, with a language penalty**.

### Source Grounding

The **GraphRAG-indexed model** is clearly stronger. Its claims are tied to indexed source references, which makes the output more auditable and better aligned with a retrieval-augmented workflow.

The **baseline model** may contain many correct facts, but it does not show where they come from and includes details that feel less constrained by the indexed article.

Overall winner for source grounding: **GraphRAG**.

### Chronology

Both answers provide at least eight dates and connect them to Einstein’s life path.

The baseline timeline includes 1919 and 1955, which are valuable for understanding Einstein’s public fame and final intellectual-political phase. The GraphRAG timeline includes 1939, which is highly relevant to the Roosevelt letter and the Manhattan Project.

Overall winner for chronology: **Tie**, with different strengths.

### Scientific Analysis

Both answers correctly identify the four main 1905 achievements:

- photoelectric effect,
- Brownian motion,
- special relativity,
- mass-energy equivalence.

The baseline answer gives more scientific detail, especially about general relativity and quantum theory. However, some of that detail increases the risk of unsupported expansion.

The GraphRAG answer is more compact and controlled, but less rich.

Overall winner for scientific depth: **Baseline Gemini**.

Overall winner for source-controlled scientific summary: **GraphRAG**.

### Political-Historical Analysis

Both answers connect 1933, Nazi Germany, emigration, the Roosevelt letter, and the Manhattan Project.

The baseline answer is more nuanced because it explicitly says that Einstein did not directly participate in the Manhattan Project and frames the Roosevelt letter as a conflict with his pacifist principles.

The GraphRAG answer also includes this distinction, but its wording that the letter “started” the Manhattan Project is slightly too strong.

Overall winner for political nuance: **Baseline Gemini**.

Overall winner for source-auditable political synthesis: **GraphRAG**.

## Which Model Performed Better?

The **GraphRAG-indexed Gemini 3.1 Flash Lite model performed better overall** for this specific test because the prompt was designed to test source-grounded reasoning from an indexed article. GraphRAG’s answer is more controlled, better structured, and easier to audit against the indexed source.

However, the margin is not absolute. The baseline Gemini answer is more fluent, more explanatory, and sometimes better at expressing the causal and thematic “big picture.” Its main weakness is that it behaves more like a general-knowledge model than a strictly source-grounded retrieval answer.

## Which Model Sees the Big Picture Better?

The answer depends on what “big picture” means:

- If “big picture” means **narrative synthesis, explanatory flow, and thematic richness**, the **baseline Gemini model** is slightly better.
- If “big picture” means **a source-grounded, structured synthesis of life, science, and politics**, the **GraphRAG-indexed model** is better.

For this test, the more important criterion is the second one, because the prompt explicitly demands strict reliance on the indexed article. Therefore, the **GraphRAG-indexed model sees the relevant big picture better in the intended test setting**.

## Final Verdict

**Overall winner: GraphRAG-indexed Gemini 3.1 Flash Lite.**

The GraphRAG answer is better aligned with the purpose of the test: controlled, source-based synthesis over free-form general explanation. It is less expressive than the baseline answer, and it should have answered in English, but it gives a more reliable retrieval-augmented response.

The baseline Gemini answer is stronger as a standalone essay, but weaker as a strict indexed-source answer. It includes richer reasoning, but also introduces more material that may be unsupported or unnecessary.

## Practical Takeaways

- GraphRAG improves source discipline and auditability.
- The baseline model is better at producing smooth explanatory prose.
- The test prompt successfully exposes the difference between general model knowledge and retrieval-grounded synthesis.
- A future version of the prompt should explicitly require: “Answer in English.”
- A future version should also require claim-level source evidence for all major historical and scientific claims.
- The GraphRAG answer would improve if it added slightly deeper causal explanations and avoided overly strong claims such as saying the Roosevelt letter directly “launched” the Manhattan Project.
