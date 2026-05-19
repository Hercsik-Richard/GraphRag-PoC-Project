# Futtatott Teszt Eredmeny

## Test Context

The test compared two responses to the same prompt about the indexed Wikipedia article on Albert Einstein:

- Baseline model: plain `qwen2.5:3b`
- GraphRAG model: `qwen2.5:3b` using the indexed Albert Einstein article

The prompt asked for a source-bound, structured analysis of Einstein's life trajectory, scientific work, and political-historical decisions. It specifically required chronology, causal or thematic links, the 1905 annus mirabilis papers, the Nobel Prize distinction, the 1933 political shift, the Roosevelt letter, and a short source-evidence section.

## Baseline `qwen2.5:3b` Response

### Strengths

The plain model produced a coherent, readable high-level summary. It identified some broadly relevant Einstein topics, including relativity, the photoelectric effect, the Nobel Prize, public fame after 1919, nuclear weapons, and his death in Princeton.

It avoided some of the more extreme fabricated citation patterns seen in the GraphRAG response. The answer is generic, but it is relatively stable as a short biographical overview.

### Weaknesses

The baseline response did not follow the requested task. It did not build an eight-date chronological chain, did not explain the path from Ulm through Munich, Switzerland, Berlin, and the United States, and did not separate the 1905 papers from general relativity and quantum/statistical mechanics contributions.

It also missed the key Nobel Prize distinction: Einstein did not receive the Nobel Prize for relativity, but for his explanation of the photoelectric effect. The response mentions the Nobel Prize only generally.

There are also factual and source-faithfulness issues. For example, it says Einstein was born in "Ulm, Germany (now part of Austria)", which is incorrect. Ulm is in Germany. It also claims he had "three daughters", while the well-known biographical record is more complex and includes two sons and a daughter. Because the prompt explicitly requested use of the indexed source only, these mistakes matter.

### Overall Assessment

The baseline model is safer in tone and simpler, but it mostly ignored the analytical structure requested by the prompt. It did not demonstrate strong relationship reasoning. It answered as if the task were "summarize Albert Einstein", not "analyze source-grounded connections across Einstein's life, science, and politics."

## GraphRAG `qwen2.5:3b` Response

### Strengths

The GraphRAG response attempted to follow the requested structure more directly. It used headings, tried to organize the answer around chronology, scientific contributions, the Nobel Prize, the 1933 political shift, the Roosevelt letter, and source evidence.

This means it recognized more of the shape of the task than the baseline model. It also attempted to make connections between Einstein's scientific work and political-historical events, especially around the Roosevelt letter and nuclear weapons.

### Weaknesses

Despite being structurally closer to the prompt, the GraphRAG response is much weaker in factual reliability.

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

The GraphRAG answer better understood the requested format, but it failed at the most important requirement: source-grounded accuracy. It appears to "see" that the question asks for relationships, chronology, and evidence, but it does not reliably map those requirements to correct facts from the indexed article.

This makes the GraphRAG response more dangerous than the baseline response in this run. It is more confident, more structured, and more citation-like, but also more misleading.

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

For this specific test run, the plain `qwen2.5:3b` response is the stronger answer overall, not because it is good, but because it is less misleading.

The GraphRAG response is stronger only in surface-level task recognition. It tries to produce the requested analytical structure and tries to connect biography, science, and politics. However, those connections are often built on incorrect facts, fabricated dates, and unusable pseudo-citations.

If the question is "which model sees the requested structure better?", the answer is GraphRAG.

If the question is "which answer should a user trust more?", the answer is the plain model.

If the question is "which model currently demonstrates the real strength of GraphRAG?", the answer is neither. The GraphRAG pipeline is not yet converting retrieved context into accurate, verifiable, clickable, source-grounded answers for this kind of broad multi-hop prompt.

## Main Diagnosis

This result suggests that the retrieval/indexing layer is not the only issue. The answer-generation step is likely struggling with a broad, multi-part prompt on a small local model (`qwen2.5:3b`).

The model receives or reconstructs some GraphRAG context, but it does not reliably preserve the factual details. It also appears to fabricate citation labels instead of using the actual retrieved entities and relationships in a controlled way.

The earlier log also showed that the auto router selected DRIFT mode for this prompt. DRIFT is appropriate for multi-hop relationship questions, but in the current application it does not expose clickable node sources the same way Local mode does. This makes the final answer harder to inspect and verify.

## Recommendation

For future tests, use two separate evaluation prompts:

1. A Local-mode factual precision prompt focused on specific entities and relationships.
2. A broader DRIFT or Global-mode synthesis prompt, but evaluated mainly for narrative quality and then checked against source facts.

For this exact Einstein test, GraphRAG should only be considered successful if it can correctly state at least the following:

- Einstein was born in Ulm in 1879.
- His family moved to Munich, and he later studied in Switzerland.
- His 1905 annus mirabilis papers covered the photoelectric effect, Brownian motion, special relativity, and mass-energy equivalence.
- General relativity was completed later, with 1915 as the key year.
- The Nobel Prize was awarded for the photoelectric effect, not relativity.
- In 1933, the Nazi rise to power was connected to his decision not to return to Germany and to settle in the United States.
- The Roosevelt letter relates to fears about nuclear weapons development, not to Einstein directly building the atomic bomb.

Based on the observed output, the current GraphRAG response did not meet this bar.
