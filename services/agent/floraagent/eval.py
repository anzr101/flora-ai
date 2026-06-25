"""A small RAG evaluation harness.

"The chatbot works" is not a metric. This measures **retrieval quality** — the
foundation of any RAG system — on a hand-labelled set mapping questions to the
knowledge document that should answer them:

  - hit@k : fraction of questions whose correct source appears in the top-k
  - MRR   : mean reciprocal rank of the correct source

Run (needs an ingested store):  python -m floraagent.eval
"""

from __future__ import annotations

from floraagent.config import settings
from floraagent.retriever import retrieve

# (question, expected source document) — the labelled gold set.
GOLD: list[tuple[str, str]] = [
    ("My plant's lower leaves are yellow and the soil is always wet", "watering.md"),
    ("How often should I water a succulent?", "watering.md"),
    ("My monstera is stretching toward the window with small leaves", "light_and_temperature.md"),
    ("What temperature range do houseplants like?", "light_and_temperature.md"),
    ("There is white powdery coating on my leaves", "diseases_and_pests.md"),
    ("How do I treat spider mites?", "diseases_and_pests.md"),
    ("What soil pH do most houseplants prefer?", "soil_ph_nutrition.md"),
    ("Brown leaf tips and a white crust on the soil", "soil_ph_nutrition.md"),
    ("Should I fertilise my plants in winter?", "seasonal_care.md"),
    ("Is a peace lily toxic to cats?", "species_profiles.md"),
    ("How do I care for a snake plant?", "species_profiles.md"),
]


def evaluate(top_k: int | None = None) -> dict:
    k = top_k or settings.top_k
    hits, reciprocal_ranks = 0, []
    for question, expected in GOLD:
        sources = [src for _, src, _ in retrieve(question, top_k=k)]
        if expected in sources:
            hits += 1
            reciprocal_ranks.append(1.0 / (sources.index(expected) + 1))
        else:
            reciprocal_ranks.append(0.0)
    n = len(GOLD)
    return {
        "n_questions": n,
        "top_k": k,
        "hit_at_k": round(hits / n, 3),
        "mrr": round(sum(reciprocal_ranks) / n, 3),
    }


def main() -> None:
    results = evaluate()
    print("RAG retrieval evaluation")
    print(f"  questions : {results['n_questions']}")
    print(f"  top_k     : {results['top_k']}")
    print(f"  hit@k     : {results['hit_at_k']}")
    print(f"  MRR       : {results['mrr']}")


if __name__ == "__main__":
    main()
