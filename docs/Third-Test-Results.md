**Language / Nyelv:** [English](#english) | [Magyar](#magyar)

<a id="english"></a>

# Third Test Results

## Test Context

In this test, I compared two answers generated with the same underlying model family, **Gemini 3.1 Flash Lite**, under two different usage modes:

- **Baseline model:** Gemini 3.1 Flash Lite used directly for the query.
- **GraphRAG-indexed model:** Gemini 3.1 Flash Lite used both for indexing and for querying through the GraphRAG pipeline.

The indexed source was the Albert Einstein Wikipedia article. I used this test to check not only factual recall, but also source grounding, prompt following, causal reasoning, and the ability to synthesize a broad historical-scientific picture.

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

I evaluated the answers according to the following criteria:

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

In my comparison, the **GraphRAG-indexed model** performed better structurally because it followed the requested sections more consistently and included source markers. However, it failed one important implicit expectation: the prompt was written in English, but the answer was in Hungarian.

The **baseline model** answered in English and had a polished structure, but it was less disciplined about source restriction and included more potentially unsupported details.

Overall winner for prompt compliance: **GraphRAG, with a language penalty**.

### Source Grounding

The **GraphRAG-indexed model** was clearly stronger here. Its claims were tied to indexed source references, which made the output more auditable and better aligned with a retrieval-augmented workflow.

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

I consider the **GraphRAG-indexed Gemini 3.1 Flash Lite model better overall** for this specific test because the prompt was designed to test source-grounded reasoning from an indexed article. GraphRAG’s answer was more controlled, better structured, and easier to audit against the indexed source.

However, the margin was not absolute. The baseline Gemini answer was more fluent, more explanatory, and sometimes better at expressing the causal and thematic “big picture.” Its main weakness was that it behaved more like a general-knowledge model than a strictly source-grounded retrieval answer.

## Which Model Sees the Big Picture Better?

From my reading, the answer depends on what “big picture” means:

- If “big picture” means **narrative synthesis, explanatory flow, and thematic richness**, the **baseline Gemini model** is slightly better.
- If “big picture” means **a source-grounded, structured synthesis of life, science, and politics**, the **GraphRAG-indexed model** is better.

For this test, I treated the second criterion as more important because the prompt explicitly demands strict reliance on the indexed article. Therefore, the **GraphRAG-indexed model sees the relevant big picture better in the intended test setting**.

## My Final Verdict

**Overall winner in my validation: GraphRAG-indexed Gemini 3.1 Flash Lite.**

The GraphRAG answer was better aligned with the purpose of the test: controlled, source-based synthesis over free-form general explanation. It was less expressive than the baseline answer, and it should have answered in English, but it gave a more reliable retrieval-augmented response.

The baseline Gemini answer was stronger as a standalone essay, but weaker as a strict indexed-source answer. It included richer reasoning, but also introduced more material that may be unsupported or unnecessary.

## My Practical Takeaways

- I saw a clear improvement in source discipline and auditability when GraphRAG was used.
- The baseline model still produced smoother explanatory prose.
- This prompt was useful because it exposed the difference between general model knowledge and retrieval-grounded synthesis.
- In the next version of this test, I would explicitly require: “Answer in English.”
- I would also require claim-level source evidence for all major historical and scientific claims.
- The GraphRAG answer would be stronger if it added slightly deeper causal explanations and avoided overly strong claims such as saying the Roosevelt letter directly “launched” the Manhattan Project.


<a id="magyar"></a>

# Harmadik Teszt Eredményei

## Tesztkörnyezet

Ebben a tesztben két, ugyanazzal az alapmodell-családdal, **Gemini 3.1 Flash Lite**-tal generált választ hasonlítottam össze két különböző használati módban:

- **Alapmodell:** Gemini 3.1 Flash Lite közvetlenül használva a lekérdezéshez.
- **GraphRAG-indexelt modell:** Gemini 3.1 Flash Lite indexeléshez és lekérdezéshez is használva a GraphRAG pipeline-on keresztül.

Az indexelt forrás az Albert Einstein Wikipédia-cikk volt. Ezzel a teszttel nemcsak a tényszerű felidézést akartam ellenőrizni, hanem a forrásalapúságot, a promptkövetést, az oksági következtetést és egy széles történeti-tudományos kép szintetizálásának képességét is.

## Eredeti Prompt

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

## Értékelési Kritériumok

A válaszokat a következő kritériumok szerint értékeltem:

- **Promptnak való megfelelés:** követi-e a válasz az összes kért szakaszt és korlátozást.
- **Forrásalapúság:** elkerüli-e a válasz az alá nem támasztott állításokat, és az indexelt Wikipédia-cikken belül marad-e.
- **Kronológiai következtetés:** koherens-e az idővonal, és minden dátum kapcsolódik-e Einstein tágabb életútjához.
- **Oksági és tematikus szintézis:** magyaráz-e kapcsolatokat a válasz ahelyett, hogy csak tényeket sorolna fel.
- **Tudományos elkülönítés:** világosan megkülönbözteti-e az 1905-ös annus mirabilist, az általános relativitást, a kvantumelméletet és a statisztikus mechanikát.
- **Politikai-történelmi szintézis:** pontosan kapcsolja-e össze az 1933-as német politikai fordulatot, az emigrációt, a Roosevelt-levelet és a Manhattan-tervet.
- **Nagy kép megértése:** Einstein életét integrált történeti, tudományos és politikai pályaként mutatja-e be.

## 1. Modell: Alap Gemini 3.1 Flash Lite

### Erősségek

- Az alapválasz gördülékeny, koherens, és csiszolt elemző esszéként olvasható.
- Erős kronológiai láncot ad nyolc dátummal: 1879, 1896, 1905, 1914, 1919, 1922, 1933 és 1955.
- Jobb narratív magyarázatot ad Einstein földrajzi útjáról, mint a GraphRAG-válasz. Az Ulmtól és Münchentől Svájcig, Berlinig és az Egyesült Államokig tartó mozgást az akadémiai szabadság és szellemi környezetek kereséseként írja le.
- Világosan szétválasztja a prompt által kért fő tudományos kategóriákat:
  - az 1905-ös annus mirabilist,
  - az általános relativitást,
  - a kvantumelméletet és a statisztikus mechanikát.
- Erős Nobel-díj pontosítást ad, és helyesen állítja, hogy a díjat a fotoelektromos hatásért, nem a relativitásért kapta.
- Árnyalt politikai szakaszt ad azzal, hogy elmagyarázza: Einstein aláírta a Roosevelt-levelet, de nem vett részt közvetlenül a Manhattan-tervben.
- Megragadja Einstein pacifizmusa és a náci nukleáris kutatástól való félelme közötti tágabb feszültséget.

### Gyengeségek

- A válasz kevésbé láthatóan forrásalapú. Nem ad soron belüli forráshivatkozásokat, noha a prompt hangsúlyozza az indexelt cikkre való kizárólagos támaszkodást.
- Több részlet növeli a hallucinációs kockázatot, vagy legalábbis nehezebbé teszi az ellenőrzést:
  - “American meritocracy and freedom of speech”
  - Einstein mint “the nation’s racism” kritikusa
  - gravitációs hullámok “confirmed in 2016”
  - a “God does not play dice” kifejezés
  - az “one great mistake” idézet
  - Time Person of the Century 1999-ben
- Ezek közül néhány tény lehet igaz, vagy szerepelhet a cikkben, de nem szükséges a prompthoz, és kevésbé fegyelmezetté teszi a választ.
- A “Source Evidence” szakasz néhány állítása periférikus a kért elemzéshez, különösen a Time Person of the Century.
- Nem mondja ki sehol explicit módon, hogy “Not determinable from the source”, még olyan területeken sem, ahol a forrástámogatás bizonytalan lehet.
- A válasz időnként a szélességet helyezi előtérbe a kontrollált forráshűséggel szemben.

## 2. Modell: GraphRAG-Indexelt Gemini 3.1 Flash Lite

### Erősségek

- A GraphRAG-válasz sokkal explicitebben forrásalapú olyan hivatkozásokon keresztül, mint `[Data: Sources (0)]`, `[Data: Sources (2)]` és hasonló forrásjelölők.
- Szorosan követi a kért szerkezetet:
  - kronológiai mérföldkövek,
  - földrajzi és szakmai fejlődés,
  - tudományos elemzés,
  - Nobel-díj pontosítás,
  - politikai-történelmi elemzés,
  - forrásbizonyíték.
- Világos idővonalat ad nyolc releváns dátummal: 1879, 1895, 1900, 1905, 1915, 1922, 1933 és 1939.
- Tömör, de koherens életút-szintézist ad Ulmtól és Münchentől Svájcon és Berlinen át az Egyesült Államokig.
- Közvetlenül összekapcsolja 1933-at, a náci politikai hatalmat, az antiszemitizmust, az emigrációt, a Roosevelt-levelet és a Manhattan-tervet.
- Helyesen állítja a Nobel-díj alapvető megkülönböztetését: Einstein nem a relativitásért kapta a Nobel-díjat, hanem különösen a fotoelektromos hatás törvényéért.
- Jobb ellenőrzési nyomot ad, mint az alapmodell, mert a fő állításokat indexelt forrásrészletekhez köti.

### Gyengeségek

- A válasz magyar nyelvű, noha a prompt angolul volt. Ez jelentős formátum- és promptmegfelelési probléma.
- Az oksági elemzés tömörebb, mint az alapválaszban. Gyakran helyesen állít kapcsolatokat, de nem mindig fejti ki őket mélyen.
- Egyes forrásjelölők csak bizonyos állításokhoz kapcsolódnak, míg más részletes állítások explicit idézet nélkül maradnak.
- Kihagyja az 1919-es napfogyatkozási megerősítést, amely erősítette volna az általános relativitás történeti jelentőségének tárgyalását.
- Azt állítja, hogy a Roosevelt-levél “elindította” a Manhattan-tervet, ami valamivel erősebb, mint az óvatosabb megfogalmazás, miszerint segített ösztönözni vagy katalizálni a projektet.
- Az az állítás, hogy Einstein később a levelet egyik nagy hibájának tekintette, lehet forrásalapú, de nincs elég világosan az evidencia-szakaszhoz kötve.
- A “Source Evidence” szakasz erősebb, mint az alapválasz evidencia-szakasza, de még mindig viszonylag minimális.

## Közvetlen Összehasonlítás

### Promptnak Való Megfelelés

Az összehasonlításom szerint a **GraphRAG-indexelt modell** szerkezetileg jobban teljesít, mert következetesebben követi a kért szakaszokat, és forrásjelölőket tartalmaz. Ugyanakkor egy fontos implicit elvárást megszeg: a prompt angolul íródott, de a válasz magyarul van.

Az **alapmodell** angolul válaszol, és csiszolt szerkezete van, de kevésbé fegyelmezett a forráskorlátozásban, és több potenciálisan alá nem támasztott részletet tartalmaz.

Átfogó győztes promptmegfelelésben: **GraphRAG, nyelvi büntetéssel**.

### Forrásalapúság

A **GraphRAG-indexelt modell** itt egyértelműen erősebb volt. Állításai indexelt forráshivatkozásokhoz kötődnek, ami ellenőrizhetőbbé teszi a kimenetet, és jobban illeszkedik egy retrieval-augmented munkafolyamathoz.

Az **alapmodell** sok helyes tényt tartalmazhat, de nem mutatja meg, honnan származnak, és olyan részleteket is tartalmaz, amelyek kevésbé tűnnek az indexelt cikk által korlátozottnak.

Átfogó győztes forrásalapúságban: **GraphRAG**.

### Kronológia

Mindkét válasz legalább nyolc dátumot ad, és összekapcsolja őket Einstein életútjával.

Az alapidővonal tartalmazza 1919-et és 1955-öt, amelyek értékesek Einstein nyilvános hírnevének és végső szellemi-politikai szakaszának megértéséhez. A GraphRAG-idővonal tartalmazza 1939-et, amely nagyon releváns a Roosevelt-levélhez és a Manhattan-tervhez.

Átfogó győztes kronológiában: **Döntetlen**, eltérő erősségekkel.

### Tudományos Elemzés

Mindkét válasz helyesen azonosítja a négy fő 1905-ös eredményt:

- fotoelektromos hatás,
- Brown-mozgás,
- speciális relativitás,
- tömeg-energia ekvivalencia.

Az alapválasz több tudományos részletet ad, különösen az általános relativitásról és a kvantumelméletről. Ugyanakkor e részletek egy része növeli az alátámasztatlan bővítés kockázatát.

A GraphRAG-válasz tömörebb és kontrolláltabb, de kevésbé gazdag.

Átfogó győztes tudományos mélységben: **Alap Gemini**.

Átfogó győztes forráskontrollált tudományos összefoglalóban: **GraphRAG**.

### Politikai-Történelmi Elemzés

Mindkét válasz összekapcsolja 1933-at, a náci Németországot, az emigrációt, a Roosevelt-levelet és a Manhattan-tervet.

Az alapválasz árnyaltabb, mert expliciten kimondja, hogy Einstein nem vett részt közvetlenül a Manhattan-tervben, és a Roosevelt-levelet pacifista elveivel való konfliktusként keretezi.

A GraphRAG-válasz is tartalmazza ezt a megkülönböztetést, de az a megfogalmazása, hogy a levél “elindította” a Manhattan-tervet, kissé túl erős.

Átfogó győztes politikai árnyaltságban: **Alap Gemini**.

Átfogó győztes forrás alapján ellenőrizhető politikai szintézisben: **GraphRAG**.

## Melyik Modell Teljesített Jobban?

Ebben a konkrét tesztben a **GraphRAG-indexelt Gemini 3.1 Flash Lite modellt tartom összességében jobbnak**, mert a promptot indexelt cikkből történő, forrásalapú következtetés tesztelésére használtam. A GraphRAG válasza kontrolláltabb, jobban strukturált és könnyebben ellenőrizhető az indexelt forráshoz képest.

Ez az előny azonban nem abszolút. Az alap Gemini-válasz gördülékenyebb, magyarázóbb, és néha jobban fejezi ki az oksági és tematikus “nagy képet”. Fő gyengesége, hogy inkább általános tudású modellként viselkedik, nem pedig szigorúan forrásalapú retrieval-válaszként.

## Melyik Modell Látja Jobban a Nagy Képet?

Az ellenőrzésem alapján ez attól függ, mit jelent a “nagy kép”:

- Ha a “nagy kép” **narratív szintézist, magyarázó folyamatosságot és tematikus gazdagságot** jelent, akkor az **alap Gemini modell** kissé jobb.
- Ha a “nagy kép” **Einstein életének, tudományának és politikájának forrásalapú, strukturált szintézisét** jelenti, akkor a **GraphRAG-indexelt modell** jobb.

Ebben a tesztben a második kritériumot tartottam fontosabbnak, mert a prompt kifejezetten az indexelt cikkre való szigorú támaszkodást követeli meg. Ezért a **GraphRAG-indexelt modell látja jobban a releváns nagy képet a tervezett tesztkörnyezetben**.

## Saját Végső Ítélet

**Átfogó győztes az ellenőrzésem alapján: GraphRAG-indexelt Gemini 3.1 Flash Lite.**

A GraphRAG-válasz jobban illeszkedik a teszt céljához: kontrollált, forrásalapú szintézis szabad formájú általános magyarázat helyett. Kevésbé kifejező, mint az alapválasz, és angolul kellett volna válaszolnia, de megbízhatóbb retrieval-augmented választ adott.

Az alap Gemini-válasz erősebb önálló esszéként, de gyengébb szigorú indexelt-forrás válaszként. Gazdagabb következtetést tartalmaz, de több olyan anyagot is bevezet, amely alátámasztatlan vagy szükségtelen lehet.

## Saját Gyakorlati Tanulságok

- A GraphRAG használatával egyértelműen javult a forrásfegyelem és az ellenőrizhetőség.
- Az alapmodell továbbra is jobb volt a gördülékeny magyarázó próza előállításában.
- Ez a tesztprompt hasznos volt, mert jól láthatóvá tette az általános modellismeret és a retrieval-alapú szintézis közti különbséget.
- A következő promptverzióban explicit módon előírnám: “Answer in English.”
- Emellett állításszintű forrásbizonyítékot is kérnék minden fő történeti és tudományos állításhoz.
- A GraphRAG-válasz akkor lenne erősebb, ha valamivel mélyebb oksági magyarázatokat adna, és elkerülné az olyan túl erős állításokat, mint hogy a Roosevelt-levél közvetlenül “elindította” a Manhattan-tervet.
