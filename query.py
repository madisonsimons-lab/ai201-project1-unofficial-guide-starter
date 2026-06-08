"""
Grounded generation for the Campus Dining Unofficial Guide.

Spec source: planning.md — Grounded Generation section.
  LLM:   Groq llama-3.3-70b-versatile (free tier)
  Rule:  answer ONLY from retrieved context; cite document numbers
  Fallback: "I don't have enough information on that in my sources."

Usage (CLI test):
    python query.py "What do Cornell students think about Okenshields?"
"""

import os
import sys

from dotenv import load_dotenv
from groq import Groq

from embed import retrieve

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"
TOP_K = 3

# ---------------------------------------------------------------------------
# System prompt — grounding is enforced here, not left to the model's goodwill.
# The three key elements:
#   1. Explicit ban on training knowledge
#   2. Exact fallback phrase for missing information (makes it testable)
#   3. Requirement to cite document numbers (auditable)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are the Campus Dining Unofficial Guide, a retrieval-based Q&A assistant \
that answers questions about student experiences with campus dining at US universities.

STRICT RULES — follow these exactly, without exception:

1. Answer ONLY using information explicitly stated in the CONTEXT DOCUMENTS \
provided in the user message. Do not use your general training knowledge about \
universities, dining halls, food, or anything else.

2. If the context documents do not contain enough information to answer the \
question, respond with this exact phrase and nothing else:
   "I don't have enough information on that in my sources."

3. For every factual claim you make, indicate which document it came from \
using the format [Doc N] where N is the document number from the context.

4. Never speculate, infer, or extrapolate beyond what the documents explicitly say.

5. Keep answers concise — 2 to 5 sentences is usually enough.\
"""

# ---------------------------------------------------------------------------
# ask() — the end-to-end function called by the Gradio app and the CLI
# ---------------------------------------------------------------------------

def ask(question: str) -> dict:
    """
    Retrieve relevant chunks and generate a grounded answer.

    Returns:
        {
          "answer":  str,         # LLM response grounded in retrieved context
          "sources": list[str],   # deduplicated source URLs (programmatic, not LLM-generated)
          "chunks":  list[dict],  # raw retrieved chunks for debugging
        }
    """
    chunks = retrieve(question, k=TOP_K)

    # Build context block passed to the LLM
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[Doc {i} | source: {chunk['source_url']}]\n{chunk['text']}"
        )
    context = "\n\n".join(context_parts)

    user_message = (
        f"CONTEXT DOCUMENTS:\n{context}\n\n"
        f"QUESTION: {question}\n\n"
        "Answer using only the context documents above. "
        "Cite [Doc N] for each claim you make."
    )

    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.1,   # near-deterministic — grounding works against creativity
        max_tokens=400,
    )

    answer = response.choices[0].message.content.strip()

    # Source attribution is programmatic: we always append the retrieved URLs,
    # regardless of whether the LLM remembered to cite them.
    sources = list(dict.fromkeys(c["source_url"] for c in chunks))

    return {"answer": answer, "sources": sources, "chunks": chunks}


# ---------------------------------------------------------------------------
# CLI test — python query.py "your question here"
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else \
        "What do University of Miami students say about vegan options?"

    print(f"\nQuestion: {question}\n")
    result = ask(question)

    print("Answer:")
    print(result["answer"])
    print("\nSources:")
    for s in result["sources"]:
        print(f"  • {s}")
    print("\nRetrieved chunks (for grounding audit):")
    for i, chunk in enumerate(result["chunks"], 1):
        print(f"  [Doc {i}] dist={chunk['distance']:.4f} | {chunk['source_url'].split('//')[1].split('/')[0]}")
        print(f"           {chunk['text'][:120]}...")
