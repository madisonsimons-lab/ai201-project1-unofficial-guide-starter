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

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
