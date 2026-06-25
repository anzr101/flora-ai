"""Composition logic for the unified flow — kept separate from the web layer so
it is unit-testable without HTTP.
"""

from __future__ import annotations

from flora_common.schemas import HealthPrediction, SpeciesPrediction


def build_advice_query(
    species: SpeciesPrediction | None,
    health: HealthPrediction | None,
    question: str,
) -> str:
    """Fuse the vision + structured-ML outputs into a single prompt for the agent.

    The agent then grounds care advice in the knowledge base (RAG) using this
    context, so the final answer reflects all three AI systems.
    """
    parts: list[str] = []
    if species is not None:
        conf = f"{species.confidence:.0%}"
        if species.low_confidence:
            parts.append(
                f"A vision model tentatively identified the plant as '{species.label}' "
                f"(low confidence, {conf}); treat the species as uncertain."
            )
        else:
            parts.append(f"A vision model identified the plant as '{species.label}' ({conf} confidence).")

    if health is not None:
        drivers = ", ".join(k for d in health.top_drivers for k in d) or "n/a"
        parts.append(
            f"A health model predicts this plant is '{health.risk_label}' "
            f"(risk score {health.risk_score:.2f}); main drivers: {drivers}."
        )

    context = " ".join(parts) if parts else "No model outputs were available."
    return (
        f"{context}\n\nUser question: {question}\n\n"
        "Using the botanical knowledge base, give specific, actionable care advice. "
        "If species is uncertain or no health data was given, give general best-practice guidance."
    )


def fallback_advice(
    species: SpeciesPrediction | None, health: HealthPrediction | None
) -> str:
    """A templated answer used only when the agent service is unreachable."""
    bits = []
    if species is not None:
        bits.append(f"Likely species: {species.label} ({species.confidence:.0%}).")
    if health is not None:
        bits.append(
            f"Predicted health status: {health.risk_label} (risk {health.risk_score:.2f})."
        )
    bits.append(
        "The reasoning assistant is offline, so detailed care guidance is unavailable. "
        "General advice: check watering (let the top 2-3 cm dry for most foliage), "
        "ensure good drainage and bright indirect light, and avoid over-fertilising."
    )
    return " ".join(bits)
