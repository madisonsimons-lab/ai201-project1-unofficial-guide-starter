"""
Document ingestion and chunking for the Campus Dining Unofficial Guide.

Spec source: planning.md — Documents table, Chunking Strategy section.
  chunk_size = 200 characters
  overlap    = 50 characters

Usage:
    python ingest.py

Outputs:
    documents/<name>.txt  — cleaned text for each fetched source
    documents/chunks.json — all chunks with source_url metadata
"""

import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Sources — matches planning.md Documents table
# ---------------------------------------------------------------------------

SOURCES = [
    {
        "name": "columbia_spectator_dining_guide",
        "url": "https://www.columbiaspectator.com/spectrum/2024/08/21/the-ultimate-guide-to-columbias-dining-halls/",
    },
    {
        "name": "harvard_crimson_dining_rankings",
        "url": "https://www.thecrimson.com/article/2022/10/4/A-Truly-Unbiased-Ranking-of-the-12-Harvard-Dining-Halls/",
    },
    {
        "name": "harvard_crimson_huds_food_influence",
        "url": "https://www.thecrimson.com/article/2024/10/11/huds-food-influence/",
    },
    {
        "name": "harvard_crimson_huds_menu_updates",
        "url": "https://www.thecrimson.com/article/2025/2/12/huds-menu-updates/",
    },
    {
        "name": "cornell_daily_sun_best_dining_hall",
        "url": "https://www.cornellsun.com/article/2025/09/abou-alfa-cornells-best-dining-hall",
    },
    {
        "name": "cornell_daily_sun_freshman_dining",
        "url": "https://cornellsun.com/2020/09/18/the-freshman-dining-hall-experience/",
    },
    {
        "name": "daily_cal_berkeley_power_rankings",
        "url": "https://dailycal.org/2017/02/23/dining-hall-power-rankings/",
    },
    {
        "name": "amherst_student_umass_dining_review",
        "url": "https://amherststudent.com/article/umass-dining-a-comprehensive-review/",
    },
    {
        "name": "miami_hurricane_vegan_options",
        "url": "https://themiamihurricane.com/2018/09/25/vegan-friendly-options-increasing-in-campus-dining-halls/",
    },
    {
        "name": "yelp_evk_usc",
        "url": "https://www.yelp.com/biz/evk-dining-hall-usc-los-angeles-2",
    },
    {
        "name": "yelp_ucsc_college_nine_ten",
        "url": "https://www.yelp.com/biz/college-nine-and-ten-dining-hall-santa-cruz",
    },
    {
        "name": "yelp_sbisa_texas_am",
        "url": "https://www.yelp.com/biz/sbisa-dining-hall-college-station",
    },
    {
        "name": "her_campus_bu_dining_ranked",
        "url": "https://www.hercampus.com/school/bu/bu-dining-halls-ranked/",
    },
    {
        "name": "bu_today_late_night_food",
        "url": "https://www.bu.edu/articles/2019/late-night-food-boston-university-campus/",
    },
    {
        "name": "niche_best_college_food",
        "url": "https://www.niche.com/colleges/search/best-college-food/",
    },
]

DOCUMENTS_DIR = Path("documents")
CHUNK_SIZE = 200
OVERLAP = 50
MIN_CHUNK_LENGTH = 30  # discard fragments shorter than this

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# ---------------------------------------------------------------------------
# Fetch and clean
# ---------------------------------------------------------------------------

def fetch_document(url: str) -> Optional[str]:
    """Fetch a URL and return cleaned plain text, or None on failure."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"  FETCH FAILED: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Strip boilerplate tags that are never substantive content
    for tag in soup(["script", "style", "nav", "footer", "header",
                     "aside", "form", "button", "iframe", "noscript",
                     "figure", "figcaption"]):
        tag.decompose()

    # Prefer a focused content container over the full page body
    main = (
        soup.find("article")
        or soup.find("main")
        or _find_by_class_keywords(soup, ["article", "content", "story", "post-body", "entry"])
        or soup.find("body")
    )

    raw = main.get_text(separator=" ", strip=True) if main else soup.get_text(separator=" ", strip=True)
    return _clean_text(raw)


def _find_by_class_keywords(soup: BeautifulSoup, keywords: List[str]) -> Optional[object]:
    """Find the first tag whose class attribute contains any of the given keywords."""
    for tag in soup.find_all(True):
        classes = " ".join(tag.get("class", [])).lower()
        if any(kw in classes for kw in keywords):
            return tag
    return None


def _clean_text(text: str) -> str:
    """Normalize whitespace and remove common HTML artifacts."""
    # Decode common HTML entities left behind by get_text
    text = text.replace("&amp;", "&").replace("&nbsp;", " ").replace("&#39;", "'")
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
    # Collapse all whitespace runs into a single space
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Chunking — spec: 200-char chunks, 50-char overlap
# ---------------------------------------------------------------------------

def chunk_text(text: str, source_url: str,
               chunk_size: int = CHUNK_SIZE,
               overlap: int = OVERLAP) -> List[Dict]:
    """
    Split text into overlapping fixed-character-size chunks.

    Each chunk dict: {"text": str, "source_url": str}
    Chunks shorter than MIN_CHUNK_LENGTH are discarded (trailing fragments).
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if len(chunk) >= MIN_CHUNK_LENGTH:
            chunks.append({"text": chunk, "source_url": source_url})
        start += chunk_size - overlap
    return chunks


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    DOCUMENTS_DIR.mkdir(exist_ok=True)
    all_chunks: List[Dict] = []
    skipped = []

    for source in SOURCES:
        name = source["name"]
        url = source["url"]
        txt_path = DOCUMENTS_DIR / f"{name}.txt"

        print(f"\n[{name}]")

        # Prefer a manually saved file so Yelp / JS-heavy pages can be
        # added by hand without re-running the fetcher.
        if txt_path.exists():
            text = txt_path.read_text(encoding="utf-8")
            print(f"  Loaded from disk ({len(text)} chars)")
        else:
            print(f"  Fetching {url}")
            text = fetch_document(url)
            if text is None or len(text) < 100:
                print(f"  SKIPPED — save text manually to: {txt_path}")
                skipped.append(name)
                continue
            txt_path.write_text(text, encoding="utf-8")
            print(f"  Saved to {txt_path} ({len(text)} chars)")
            time.sleep(1.5)  # be polite to servers

        chunks = chunk_text(text, url)
        all_chunks.extend(chunks)
        print(f"  {len(chunks)} chunks produced")

    # ------------------------------------------------------------------
    # Save all chunks
    # ------------------------------------------------------------------
    chunks_path = DOCUMENTS_DIR / "chunks.json"
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------------
    # Inspection report
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print(f"TOTAL CHUNKS: {len(all_chunks)}")
    print(f"Saved to:     {chunks_path}")

    if skipped:
        print(f"\nSKIPPED ({len(skipped)}) — add these manually as .txt files in documents/:")
        for name in skipped:
            print(f"  documents/{name}.txt")

    print("\n--- 5 Sample Chunks (random) ---")
    import random
    random.seed(42)
    samples = random.sample(all_chunks, min(5, len(all_chunks)))
    for i, chunk in enumerate(samples, 1):
        source_short = chunk["source_url"].split("//")[-1].split("/")[0]
        print(f"\n[{i}] source: {source_short}")
        print(f"    length: {len(chunk['text'])} chars")
        print(f"    text:   {chunk['text']}")

    print("\n--- Chunk length distribution ---")
    lengths = [len(c["text"]) for c in all_chunks]
    if lengths:
        print(f"    min: {min(lengths)}  max: {max(lengths)}  avg: {sum(lengths)//len(lengths)}")


if __name__ == "__main__":
    main()
