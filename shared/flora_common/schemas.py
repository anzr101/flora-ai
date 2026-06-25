"""Cross-service Pydantic schemas.

These are the contracts that the gateway relies on when it stitches the modules
together. Keeping them in one shared place means the ML, DL, agent, and gateway
services cannot silently drift apart — a change to a contract is a change to a
single file that everyone imports.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


# ── ML service ────────────────────────────────────────────────────────────
class PlantConditions(BaseModel):
    """Structured environmental + care conditions for a single plant."""

    temperature_c: float = Field(..., ge=-20, le=60, description="Ambient temperature (°C)")
    humidity_pct: float = Field(..., ge=0, le=100, description="Relative humidity (%)")
    soil_moisture_pct: float = Field(..., ge=0, le=100, description="Soil moisture (%)")
    light_hours: float = Field(..., ge=0, le=24, description="Daily light exposure (hours)")
    soil_ph: float = Field(..., ge=3.0, le=10.0, description="Soil pH")
    watering_freq_per_week: float = Field(..., ge=0, le=21, description="Waterings per week")
    fertilizer_freq_per_month: float = Field(..., ge=0, le=30, description="Fertilizings per month")
    plant_age_months: float = Field(..., ge=0, le=600, description="Plant age (months)")


class HealthPrediction(BaseModel):
    risk_label: Literal["healthy", "at_risk", "diseased"]
    risk_score: float = Field(..., ge=0, le=1, description="P(not healthy)")
    class_probabilities: dict[str, float]
    top_drivers: list[dict[str, float]] = Field(
        default_factory=list,
        description="Most influential features for THIS prediction (local SHAP).",
    )
    model_version: str


# ── DL service ────────────────────────────────────────────────────────────
class SpeciesPrediction(BaseModel):
    label: str
    confidence: float = Field(..., ge=0, le=1)
    top_k: list[dict[str, float]]
    model_version: str
    low_confidence: bool = Field(
        default=False,
        description="True when confidence is below the abstention threshold — the "
        "caller should treat the label as unreliable (e.g. out-of-distribution photo).",
    )


# ── Agent service ─────────────────────────────────────────────────────────
class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class AgentRequest(BaseModel):
    message: str
    history: list[ChatMessage] = Field(default_factory=list)


class Citation(BaseModel):
    source: str
    snippet: str


class AgentResponse(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    tools_used: list[str] = Field(default_factory=list)


# ── Gateway (unified flow) ────────────────────────────────────────────────
class DiagnoseResponse(BaseModel):
    """The end-to-end result: vision + structured ML + agent reasoning."""

    species: SpeciesPrediction | None = None
    health: HealthPrediction | None = None
    advice: str
    citations: list[Citation] = Field(default_factory=list)
    services_called: list[str] = Field(default_factory=list)
