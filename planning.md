# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

Student experiences with campus dining halls across multiple US universities. Official dining pages list hours and menus but never capture the real student view — which dining halls are worth swiping into, which are overpriced, what the vegetarian options actually taste like, or how brutal the lunch rush is. That knowledge is scattered across student newspapers, Yelp reviews, and Reddit threads, making it nearly impossible to find at a glance.

**Sample questions this system should handle:**
1. Which dining halls do students at Harvard actually recommend?
2. Are the vegetarian/vegan options at major universities getting better?
3. What do students say about meal plan value vs. cost?
4. Which dining hall has the best late-night food?
5. What are the most common complaints about campus dining across schools?

---

## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Columbia Spectator | Ultimate guide to Columbia's dining halls — covers all options with student perspective | https://www.columbiaspectator.com/spectrum/2024/08/21/the-ultimate-guide-to-columbias-dining-halls/ |
| 2 | Harvard Crimson | Ranking of all 12 Harvard dining halls with student reviews | https://www.thecrimson.com/article/2022/10/4/A-Truly-Unbiased-Ranking-of-the-12-Harvard-Dining-Halls/ |
| 3 | Harvard Crimson | How Harvard dining services influence what students actually eat | https://www.thecrimson.com/article/2024/10/11/huds-food-influence/ |
| 4 | Harvard Crimson | Student complaints about HUDS menu updates | https://www.thecrimson.com/article/2025/2/12/huds-menu-updates/ |
| 5 | Cornell Daily Sun | "Cornell's Best Dining Hall" — student opinion piece | https://www.cornellsun.com/article/2025/09/abou-alfa-cornells-best-dining-hall |
| 6 | Cornell Daily Sun | Freshman dining hall experience with student perspectives | https://cornellsun.com/2020/09/18/the-freshman-dining-hall-experience/ |
| 7 | Daily Californian | UC Berkeley dining hall power rankings | https://dailycal.org/2017/02/23/dining-hall-power-rankings/ |
| 8 | Amherst Student | UMass Dining comprehensive review | https://amherststudent.com/article/umass-dining-a-comprehensive-review/ |
| 9 | The Miami Hurricane | Vegan-friendly options at University of Miami dining halls | https://themiamihurricane.com/2018/09/25/vegan-friendly-options-increasing-in-campus-dining-halls/ |
| 10 | Yelp | EVK Dining Hall @ USC — student reviews | https://www.yelp.com/biz/evk-dining-hall-usc-los-angeles-2 |
| 11 | Yelp | College Nine & Ten Dining Hall, UC Santa Cruz — student reviews | https://www.yelp.com/biz/college-nine-and-ten-dining-hall-santa-cruz |
| 12 | Yelp | Sbisa Dining Hall, Texas A&M — student reviews | https://www.yelp.com/biz/sbisa-dining-hall-college-station |
| 13 | Her Campus BU | Boston University dining halls ranked by students | https://www.hercampus.com/school/bu/bu-dining-halls-ranked/ |
| 14 | BU Today | Late-night food options at Boston University | https://www.bu.edu/articles/2019/late-night-food-boston-university-campus/ |
| 15 | Niche.com | Best college food & dining in America — aggregated student reviews | https://www.niche.com/colleges/search/best-college-food/ |

---

## Chunking Strategy

**Chunk size:** 200 characters

**Overlap:** 50 characters

**Reasoning:** The corpus is mixed: short Yelp reviews (often 1–4 sentences, ~100–300 characters total) and longer student newspaper articles (many paragraphs). At 200 characters, a complete short review fits in one or two chunks and stays intact. Newspaper articles get split into roughly paragraph-sized pieces that remain topically focused. The 50-character overlap ensures that a key claim sitting at a chunk boundary — e.g., a sentence that starts in one chunk and finishes in the next — can still be retrieved by either chunk. Without overlap, a split sentence produces two useless fragments that neither retrieves well.

The main risk of 200-character chunks: some Yelp reviews are longer than 200 characters, so a review's main claim (e.g., "The food is terrible") may land in chunk N while the supporting detail (e.g., "everything is overcooked and overpriced") lands in chunk N+1. The 50-character overlap partially mitigates this but doesn't fully solve it. If retrieval quality is low during evaluation, increasing chunk size to 400–500 characters is the first adjustment to try.

---

## Retrieval Approach

**Embedding model:** `all-MiniLM-L6-v2` via `sentence-transformers`

**Top-k:** 3

**Reasoning:** `all-MiniLM-L6-v2` is fast, runs locally with no API cost, and handles general-purpose semantic similarity well. At 200-character chunks, its 256-token context limit is not a constraint — all chunks fit comfortably. top-3 gives the LLM enough context to synthesize an answer without flooding the prompt with off-topic chunks. Since sources cover 10+ distinct schools, a single query is unlikely to be answered by more than 3 chunks anyway.

**Production tradeoff reflection:** For real users I would evaluate two alternatives. First, `text-embedding-3-large` (OpenAI) — higher dimensional embeddings that tend to perform better on informal, opinion-rich text like dining hall reviews, where slang ("swipe," "meal plan," "dining dollars") can confuse a general-purpose model. Cost: ~$0.13/1M tokens, negligible at this corpus size but non-trivial at scale. Second, a model with longer context (e.g., `nomic-embed-text`, 8192-token limit) would matter if I switched to larger chunks — but at 200 characters it's irrelevant. Multilingual support is not a priority here since all sources are English. Latency: local inference with MiniLM is ~5–20ms per query; OpenAI API adds ~100–300ms per call, which matters for an interactive interface.

---

## Evaluation Plan

> **Note:** Expected answers below are drafted from known article titles and topics. Verify each against the actual fetched document text in Milestone 3 and update if the source says something different.

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What dining hall does the Cornell Daily Sun name as Cornell's best? | The article specifically names Abou-Alfa as Cornell's best dining hall. |
| 2 | What do University of Miami students say about vegan options on campus? | The Miami Hurricane reports that vegan-friendly options at UM have been increasing, with students noting improvements at Hecht-Stanford dining. |
| 3 | What late-night food options does BU Today describe for hungry students after hours? | BU Today lists specific on-campus locations (e.g., The George Sherman Union late-night options) available after normal dining hall hours. |
| 4 | How do Harvard students describe the food quality changes after HUDS updated its menu? | The Crimson article captures student complaints about specific menu changes — dishes removed or altered — that students considered a downgrade. |
| 5 | What does the Columbia Spectator recommend for students who want a late-night snack on campus? | The Spectator's ultimate guide mentions JJ's Place as Columbia's late-night dining option, open when other dining halls are closed. |

---

## Anticipated Challenges

1. **Chunk boundary splits within short Yelp reviews.** At 200 characters, a Yelp review like "The food is genuinely terrible — long lines, small portions, and nothing is fresh" will get split. The first chunk retrieves on "terrible" but doesn't include the reasons. The second chunk has the reasons but no strong negative signal. Neither chunk alone fully answers "what do students complain about at EVK?" The 50-character overlap helps but doesn't fully solve it. Mitigation: if retrieval quality is low for Yelp-sourced questions, consider chunking Yelp reviews as atomic units (one review = one chunk) regardless of character count.

2. **Corpus skew toward Harvard sources (3 articles) causing over-retrieval from one school.** Queries about general dining trends may pull all 3 returned chunks from Harvard documents, leaving questions about Cornell, USC, or Texas A&M unanswered even though those documents exist. The LLM will then give a Harvard-centric answer to a general question. Mitigation: track source distribution in retrieved chunks during evaluation. If skew is severe, add a metadata filter to cap chunks per source URL to 1 per query.

---

## Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  1. DOCUMENT INGESTION                                      │
│     Tool: requests + BeautifulSoup (Python)                 │
│     Input:  15 URLs (student newspapers, Yelp, blogs)       │
│     Output: raw text files saved to documents/              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  2. CHUNKING                                                │
│     Tool: custom chunk_text() in Python                     │
│     chunk_size=200 characters, overlap=50 characters        │
│     Output: list of (chunk_text, source_url) pairs          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  3. EMBEDDING + VECTOR STORE                                │
│     Embedding model: all-MiniLM-L6-v2 (sentence-transformers│
│     Vector store:    ChromaDB (local, persistent)           │
│     Metadata stored: source URL per chunk                   │
│     Output: persisted ChromaDB collection on disk           │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────┘  ← query embedded with same model
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│  4. RETRIEVAL                                               │
│     Tool: ChromaDB .query() — cosine similarity             │
│     Returns: top-3 chunks + source URLs as metadata         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  5. GENERATION                                              │
│     LLM: Groq API (llama-3 or mixtral, fast inference)      │
│     System prompt: grounded — answer only from chunks,      │
│                    cite source URL for each claim           │
│     Output: answer with inline source citations             │
└─────────────────────────────────────────────────────────────┘
```

---

## AI Tool Plan

**Milestone 3 — Ingestion and chunking:**
I'll give Claude this planning.md's Documents table and Chunking Strategy section, plus the requirement that each chunk must store its source URL as metadata. I'll ask it to implement `ingest.py` containing two functions: `fetch_document(url) -> str` (fetches and strips HTML from a URL using requests + BeautifulSoup) and `chunk_text(text, source_url, chunk_size=200, overlap=50) -> list[dict]` (returns a list of `{text, source_url}` dicts). I'll verify by running it on one URL, printing the first 5 chunks, and manually checking that each chunk is ~200 characters with ~50-character overlap visible at boundaries.

**Milestone 4 — Embedding and retrieval:**
I'll give Claude the Retrieval Approach section and Architecture diagram, and ask it to implement `embed_and_store(chunks: list[dict])` (embeds all chunks with `all-MiniLM-L6-v2` and stores them in a local ChromaDB collection with source URL as metadata) and `retrieve(query: str, k: int = 3) -> list[dict]` (returns top-k chunks with text and source URL). I'll verify by running a known query ("what do students think about Cornell dining") and checking that at least one of the returned chunks is from the Cornell Daily Sun source.

**Milestone 5 — Generation and interface:**
I'll give Claude the full planning.md plus the Groq SDK docs, and ask it to implement `generate_response(query: str, chunks: list[dict]) -> str` using Groq. The system prompt must: (1) instruct the model to answer only from the provided chunks, (2) refuse to answer if the chunks are not relevant, and (3) cite the source URL for every factual claim. I'll verify by running a query whose answer is NOT in the corpus (e.g., "What is the food like at MIT?") and confirming the model does not hallucinate an answer.
