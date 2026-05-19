# Second-Test-Local-Results

## Test Setup

This test evaluated a GraphRAG pipeline using:

- Indexing model: `qwen2.5:3b`
- Query model: `gemini-2.5-flash-lite`
- Query mode: `Local`
- Source document: indexed Albert Einstein Wikipedia article

The goal was to understand whether breaking the original broad evaluation prompt into smaller Local-mode questions would improve retrieval quality and answer accuracy.

## Test Prompts

The original broad prompt had asked for a source-bound, chronological and causal analysis of Einstein's life, scientific work, and political-historical decisions.

Because Local mode is better suited to focused entity/relationship questions, the broad prompt was split into five smaller questions:

1. What are the key dated life events connecting Einstein from Ulm to Munich, Switzerland, Berlin, and the United States?
2. What does the source say about Einstein's 1905 annus mirabilis papers?
3. Why did Einstein receive the Nobel Prize, and why was it not for relativity?
4. How does the source connect the 1933 Nazi rise to power with Einstein's move to the United States?
5. What does the source say about Einstein's letter to Roosevelt?

## Result Summary

The results were mixed.

The system answered the Nobel Prize question well, and it partially answered the broad life-route question, especially around the 1933 transition from Europe to the United States.

However, it failed on several questions where the relevant information should exist in the underlying Wikipedia article. In particular, it claimed that there was no information about the 1905 annus mirabilis papers, the 1933 Nazi rise to power connection, and Einstein's letter to Roosevelt.

This should be interpreted as a retrieval failure, not as evidence that the source document lacks the information.

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

This was a clear failure.

The system answered that the provided data did not contain information about Einstein's 1905 annus mirabilis papers. It only mentioned that Einstein published his first paper in 1901 and completed his doctoral dissertation in 1905.

This is incorrect as a source-level expectation: the Einstein Wikipedia article does contain the annus mirabilis topic. The failure indicates that Local retrieval did not surface the relevant text or graph nodes.

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

This was the strongest answer.

The system correctly stated that Einstein received the 1921 Nobel Prize in Physics for his services to theoretical physics and especially for discovering the law of the photoelectric effect.

It also correctly explained why the prize was not awarded for relativity: relativity was still controversial and less directly settled for the Nobel committee, while the photoelectric effect was more experimentally grounded and important for quantum theory.

This question worked because it maps well to a concrete entity/relationship:

```text
Einstein -> Nobel Prize -> photoelectric effect
```

This is the kind of task Local mode handles well.

### 4. 1933 Nazi Rise to Power and Move to the United States

This was a retrieval inconsistency.

The system answered that the provided text did not contain information about the 1933 Nazi rise to power or its connection to Einstein's move to the United States.

This contradicts the answer to question 1, where the system had already retrieved relevant 1933 information from `Sources (4)`.

This means the failure was not due to missing source data. The relevant source exists, but Local retrieval did not return it consistently for this phrasing of the question.

### 5. Einstein's Letter to Roosevelt

This also failed.

The system answered that the source material did not contain information about a letter from Einstein to Roosevelt.

This is very likely a retrieval failure. The broader previous test had retrieved and used the Roosevelt-letter topic, and the Einstein article is expected to contain this event.

The retrieved context was again dominated by unrelated Einstein-adjacent graph elements rather than Roosevelt, Szilard, nuclear weapons, uranium, or the Manhattan Project.

## What Worked

Local mode worked when the question was tightly bound to a well-represented graph relationship.

The Nobel Prize question is the clearest example. The system found the relevant Nobel Prize context and answered accurately.

The 1933 migration story also appeared in one answer when the right source chunk was retrieved. This proves the underlying indexed data contains at least some relevant material.

The Gemini query model behaved relatively responsibly. When the retrieved context did not contain enough evidence, it often refused to answer instead of freely hallucinating. This is better than inventing unsupported details.

## What Did Not Work

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

The current pipeline is limited by retrieval quality and graph quality, not primarily by the query model.

The query model upgrade to `gemini-2.5-flash-lite` helped significantly. However, a strong query model cannot reliably answer source-grounded questions if the retrieved graph context is incomplete or noisy.

Local mode is not ideal for all five questions:

- It is good for direct entity relationships, such as Nobel Prize and photoelectric effect.
- It is weaker for source-span questions, such as "what does the article say about the Roosevelt letter?"
- It is weaker for historical chronology, such as Ulm -> Munich -> Switzerland -> Berlin -> United States.
- It is weaker for broad event synthesis, such as the 1933 Nazi rise and emigration story.

## Recommendations

### 1. Re-index With a Stronger Indexing Model

The highest-impact improvement is likely to re-index the article with a stronger model.

Recommended setup:

- Index chat model: `gemini-2.5-flash-lite` or another stronger model
- Query chat model: `gemini-2.5-flash-lite`
- Embedding model: keep a stable embedding model, but ensure index and query embedding models match

The current `qwen2.5:3b` index appears to produce a noisy graph.

### 2. Add a Source or Hybrid Retrieval Mode

For questions like annus mirabilis, 1933 emigration, and the Roosevelt letter, graph-local retrieval is not enough.

A better strategy would be:

```text
Step 1: retrieve relevant raw text units
Step 2: retrieve local graph entities and relationships
Step 3: rerank evidence against the question
Step 4: answer only from the filtered evidence
```

This would combine the benefits of text retrieval and graph retrieval.

### 3. Improve Routing

The router should send different question types to different retrieval modes:

| Question type | Best mode |
|---|---|
| Direct entity relationship | Local |
| "What does the source say about..." | Source |
| Chronological life path | Source or Global |
| Broad synthesis | Global or DRIFT |
| Multi-hop causal relation | DRIFT or Hybrid |
| Source-grounded factual evidence | Source + Local |

### 4. Rerank Retrieved Nodes

Before the final answer, retrieved nodes and relationships should be filtered by relevance to the user question.

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

For this Einstein test, the system should be considered successful only if it can reliably retrieve and answer:

- 1905 annus mirabilis papers
- Nobel Prize reason
- 1933 Nazi rise to power and emigration
- Roosevelt letter
- Ulm -> Munich -> Switzerland -> Berlin -> United States route

If any of these cannot be retrieved, the issue should be investigated at the index/retrieval level.

## Final Conclusion

The second Local-mode test shows that the GraphRAG system is partially working, but not yet reliable for broad historical-scientific synthesis.

The strongest result was the Nobel Prize question, where Local mode matched a clear entity relationship.

The weakest results were the annus mirabilis and Roosevelt-letter questions, where the system incorrectly claimed the source did not contain information. These failures point to retrieval and graph-index quality problems.

The most important next step is not another query-model upgrade. The query model is already good enough to expose the problem clearly. The next step is to improve the indexed graph and add source/hybrid retrieval so that relevant text evidence is available before answer generation.
