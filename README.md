# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

Student experiences with campus dining halls across multiple US universities. Official dining pages list hours and menus but never capture the real student view — which dining halls are worth swiping into, which are overpriced, what the vegetarian options actually taste like, or how brutal the lunch rush is. That knowledge is scattered across student newspapers, Yelp reviews, and blog posts, making it nearly impossible to find in one place.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Columbia Spectator | Student newspaper | https://www.columbiaspectator.com/spectrum/2024/08/21/the-ultimate-guide-to-columbias-dining-halls/ |
| 2 | Harvard Crimson | Student newspaper | https://www.thecrimson.com/article/2022/10/4/A-Truly-Unbiased-Ranking-of-the-12-Harvard-Dining-Halls/ |
| 3 | Harvard Crimson | Student newspaper | https://www.thecrimson.com/article/2024/10/11/huds-food-influence/ |
| 4 | Harvard Crimson | Student newspaper | https://www.thecrimson.com/article/2025/2/12/huds-menu-updates/ |
| 5 | Cornell Daily Sun | Student newspaper | https://www.cornellsun.com/article/2025/09/abou-alfa-cornells-best-dining-hall |
| 6 | Cornell Daily Sun | Student newspaper | https://cornellsun.com/2020/09/18/the-freshman-dining-hall-experience/ |
| 7 | Daily Californian | Student newspaper | https://dailycal.org/2017/02/23/dining-hall-power-rankings/ |
| 8 | Amherst Student | Student newspaper | https://amherststudent.com/article/umass-dining-a-comprehensive-review/ |
| 9 | The Miami Hurricane | Student newspaper | https://themiamihurricane.com/2018/09/25/vegan-friendly-options-increasing-in-campus-dining-halls/ |
| 10 | Yelp — EVK @ USC | User reviews | https://www.yelp.com/biz/evk-dining-hall-usc-los-angeles-2 |
| 11 | Yelp — UCSC College Nine & Ten | User reviews | https://www.yelp.com/biz/college-nine-and-ten-dining-hall-santa-cruz |
| 12 | Yelp — Sbisa Dining, Texas A&M | User reviews | https://www.yelp.com/biz/sbisa-dining-hall-college-station |
| 13 | Her Campus BU | Student blog | https://www.hercampus.com/school/bu/bu-dining-halls-ranked/ |
| 14 | BU Today | University news | https://www.bu.edu/articles/2019/late-night-food-boston-university-campus/ |
| 15 | Niche.com | Aggregated reviews | https://www.niche.com/colleges/search/best-college-food/ |

---

## Chunking Strategy

**Chunk size:** 200 characters

**Overlap:** 50 characters

**Why these choices fit your documents:** The corpus mixes short Yelp reviews (often 100–300 characters total) and long student newspaper articles (many paragraphs). At 200 characters, a complete short review fits in one or two chunks and stays intact, while newspaper articles get split into roughly paragraph-sized pieces that remain topically focused. The 50-character overlap ensures a key claim sitting at a chunk boundary — a sentence that starts in one chunk and finishes in the next — can still be retrieved by either chunk. Without overlap, a split sentence produces two useless fragments.

Before chunking, each document was cleaned by stripping HTML boilerplate tags (`script`, `style`, `nav`, `footer`, `header`, `aside`, `form`, `button`, `iframe`) using BeautifulSoup, preferring `<article>` or `<main>` containers over the full page body, decoding HTML entities (`&amp;`, `&nbsp;`, `&#39;`), and collapsing all whitespace to single spaces. Chunks shorter than 30 characters were discarded as trailing fragments.

**Final chunk count:** 301 chunks across 9 successfully ingested documents.

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`, running locally with no API key or rate limits. Chosen because it is fast (~1–2s to embed 301 chunks), handles the 200-character chunk size well within its 256-token context limit, and performs strong general-purpose semantic similarity — sufficient for matching student opinion queries to student opinion text.

**Production tradeoff reflection:** For real users I would evaluate `text-embedding-3-large` (OpenAI). It produces higher-dimensional embeddings and tends to perform better on informal, opinion-rich text where slang ("swipe", "meal plan", "dining dollars", "unlimited swipes") can confuse a general-purpose model. The cost is approximately $0.13 per million tokens — negligible at this corpus size but meaningful at scale. A second tradeoff is latency: local inference with MiniLM runs in ~5–20ms per query, while an OpenAI API call adds ~100–300ms, which matters for an interactive interface. Multilingual support is not a priority since all current sources are English, but would matter if expanding to international campus communities. A model with a longer context limit (e.g., `nomic-embed-text` at 8,192 tokens) would only matter if chunk size were increased substantially.

---

## Grounded Generation

**System prompt grounding instruction:** The system prompt in `query.py` contains five explicit rules:

```
STRICT RULES — follow these exactly, without exception:

1. Answer ONLY using information explicitly stated in the CONTEXT DOCUMENTS
   provided in the user message. Do not use your general training knowledge about
   universities, dining halls, food, or anything else.

2. If the context documents do not contain enough information to answer the
   question, respond with this exact phrase and nothing else:
   "I don't have enough information on that in my sources."

3. For every factual claim you make, indicate which document it came from
   using the format [Doc N] where N is the document number from the context.

4. Never speculate, infer, or extrapolate beyond what the documents explicitly say.

5. Keep answers concise — 2 to 5 sentences is usually enough.
```

The model temperature is set to 0.1 (near-deterministic) to reduce the creative variation that leads to hallucination. The user message formats each retrieved chunk as `[Doc N | source: URL]` followed by its text, making it straightforward for the model to cite by number.

**How source attribution is surfaced in the response:** Source attribution is programmatic — the `ask()` function always appends the deduplicated list of source URLs from the retrieved chunks to the return value, regardless of whether the LLM cited them in its prose. This means the "Retrieved from" panel in the Gradio app is guaranteed to show which documents were used, even if the model produces a response that omits inline citations.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What dining hall does the Cornell Daily Sun name as Cornell's best? | Abou-Alfa | Okenshields, citing [Doc 3] which contained the article title alongside a sentence about Okenshields being "subject to constant ridicule" | Relevant (all chunks from cornellsun.com, dist 0.35–0.39) | Inaccurate |
| 2 | What do University of Miami students say about vegan options on campus? | The vegan menu is described as "unappetizing and repetitive"; students object to overuse of tofu | Vegan menu remains "unappetizing and repetitive" [Doc 2]; students say "doing tofu all the time is not sufficient" | Relevant (all chunks from themiamihurricane.com, dist 0.28–0.39) | Accurate |
| 3 | What late-night food options does BU Today describe for hungry students after hours? | Specific BU late-night locations open after dining hall hours | "I don't have enough information on that in my sources." | Off-target (Cornell + Harvard chunks, dist 0.39–0.42; BU Today was never ingested) | Inaccurate |
| 4 | How do Harvard students describe the food quality changes after HUDS updated its menu? | Students called the new options "junk food"; HUDS reversed the changes | HUDS walked back spring 2025 menu changes after students called them "junk food" [Doc 1]; reversed after receiving feedback [Doc 3] | Relevant (all chunks from thecrimson.com, dist 0.27–0.39) | Accurate |
| 5 | What does the Columbia Spectator recommend for students who want a late-night snack on campus? | JJ's Place, open when other dining halls are closed | "I don't have enough information on that in my sources." | Off-target (Harvard + Berkeley chunks, dist 0.46–0.47; Columbia Spectator was never ingested) | Inaccurate |

---

## Failure Case Analysis

**Question that failed:** "What dining hall does the Cornell Daily Sun name as Cornell's best?" (Eval Q1)

**What the system returned:** "The Cornell Daily Sun names Okenshields as Cornell's best dining hall." This is wrong — the article argues that Abou-Alfa is the best hall.

**Root cause (tied to a specific pipeline stage — chunking):** The article's title, "ABOU-ALFA | Cornell's Best Dining Hall," was placed in the same 200-character chunk as the article's opening sentence: "Among all of Cornell's dining halls, Okenshields is the only one subject to constant ridicule." At 200 characters, the chunk was long enough to include both the title and the opening sentence, but not long enough to reach the paragraphs where the author explains why Abou-Alfa is superior. The model retrieved this chunk with the lowest distance score (0.39) and read the sentence about Okenshields being ridiculed as the answer to "which is the best" — inverting the article's actual argument. The failure is at the chunking stage: fixed-character splitting cut off the article at the worst possible place, leaving the thesis statement in a different chunk than the evidence that explains it.

**What you would change to fix it:** Two options. First, increase chunk size to 400–500 characters so the opening paragraph has room to complete its argument before the chunk boundary. Second, split by paragraph instead of fixed character count — the first full paragraph of the article contains both the title and the initial argument, and keeping it intact would give the model enough context to answer correctly. A paragraph-aware splitter (split on `\n\n`) would prevent this category of error entirely for article-structured documents.

---

## Spec Reflection

**One way the spec helped you during implementation:** The architecture diagram in planning.md labeled each pipeline stage with its specific tool — BeautifulSoup for ingestion, a custom `chunk_text()` for splitting, `all-MiniLM-L6-v2` for embedding, ChromaDB for storage, Groq for generation. When prompting Claude to implement each stage, I pasted the relevant diagram section alongside the corresponding planning.md section (e.g., the Chunking Strategy section when asking for `ingest.py`). This kept the generated code focused and matching the spec rather than producing a generic implementation that would have needed heavy revision. Without the diagram, the AI prompt would have been vague and the output would have been generic.

**One way your implementation diverged from the spec, and why:** The evaluation plan in planning.md included two test questions (Q3 and Q5) that depended on the BU Today and Columbia Spectator documents — both of which failed to ingest because their pages are JavaScript-rendered and returned empty or unusable content. The spec assumed all 15 sources would be successfully ingested before evaluation questions were finalized; I did not verify ingestion success before writing the test questions. As a result, 40% of the evaluation plan tested documents that were never in the corpus, producing "I don't have enough information" responses that look like grounding successes but are actually ingestion failures. The fix would have been to confirm every source was successfully saved to `documents/` before writing evaluation questions that depend on it.

---

## AI Usage

**Instance 1 — Generating `ingest.py`**

- *What I gave the AI:* The Documents table from planning.md (15 URLs with source names), the Chunking Strategy section (200-char chunks, 50-char overlap, reason tied to mixed corpus), and the Architecture diagram showing BeautifulSoup as the ingestion tool and the requirement that each chunk store its source URL as metadata.
- *What it produced:* `ingest.py` with `fetch_document(url)` (using requests + BeautifulSoup to strip boilerplate and extract main text) and `chunk_text(text, source_url, chunk_size, overlap)` (fixed-character splitter returning `{text, source_url}` dicts).
- *What I changed or overrode:* Added a fallback-to-disk branch: before fetching, the script checks if `documents/<name>.txt` already exists and loads from disk if so. This was necessary because Yelp returns 403 errors and some sites require manual text collection — without the fallback, re-running the script would fail or skip those sources every time. I also raised the minimum chunk length from 0 to 30 characters to filter trailing fragments that the original implementation included.

**Instance 2 — Generating the grounding system prompt in `query.py`**

- *What I gave the AI:* The Grounded Generation section from planning.md (requirement: answer only from retrieved context, cite source, exact fallback phrase for missing information), the Architecture diagram showing Groq as the LLM, and the requirement that source attribution be programmatically guaranteed rather than left to the model.
- *What it produced:* A system prompt with grounding instructions and an `ask()` function that formatted retrieved chunks as numbered documents and passed them to the Groq API.
- *What I changed or overrode:* Set `temperature=0.1` — the generated version used the default `0.7`, which produced responses that occasionally extrapolated beyond the retrieved text. Lowering temperature made the model stick more closely to verbatim content from the chunks. I also added source attribution as a separate programmatic step (`dict.fromkeys` over retrieved chunk URLs) rather than relying on the LLM to include citations in its response text. During testing, the model sometimes omitted `[Doc N]` inline citations at higher temperature even when instructed to include them; the programmatic fallback guarantees the source list is always shown.
