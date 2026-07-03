"""FastAPI orchestration gateway — the single public entrypoint to FloraAI.

  GET  /health     liveness + aggregated downstream health
  POST /diagnose   THE unified flow: image + conditions + question
                   -> species (DL) + health (ML) + grounded advice (Agent)

The gateway holds no model. It calls the three services, fuses their outputs,
and degrades gracefully when any of them is unavailable.
"""

from __future__ import annotations

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from flora_common import get_logger
from flora_common.schemas import (
    AgentRequest,
    AgentResponse,
    DiagnoseResponse,
    HealthPrediction,
    PlantConditions,
    SpeciesPrediction,
)

from floragateway import clients, db
from floragateway.config import settings
from floragateway.orchestration import build_advice_query, fallback_advice

log = get_logger("floragateway.api")
app = FastAPI(
    title="FloraAI · Gateway",
    version="1.0.0",
    description="Orchestrates the ML, DL, and Agent services into one botanical AI flow.",
)

# Allow the Next.js frontend (dev + common local ports) to call the gateway.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

_CONDITION_FIELDS = [
    "temperature_c",
    "humidity_pct",
    "soil_moisture_pct",
    "light_hours",
    "soil_ph",
    "watering_freq_per_week",
    "fertilizer_freq_per_month",
    "plant_age_months",
]


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "gateway", "downstream": clients.downstream_health()}


# ── Single-origin proxy routes (frontend talks only to the gateway) ───────────
@app.post("/api/predict", response_model=HealthPrediction)
def api_predict(conditions: PlantConditions) -> HealthPrediction:
    """Proxy → ML service. Lets the frontend use one base URL + one CORS origin."""
    result = clients.predict_health(conditions.model_dump())
    if result is None:
        raise HTTPException(502, "ML service is unavailable.")
    return result


@app.post("/api/identify", response_model=SpeciesPrediction)
async def api_identify(file: UploadFile = File(...)) -> SpeciesPrediction:
    """Proxy → DL service (image classification)."""
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(400, "Uploaded file must be an image.")
    image_bytes = await file.read()
    result = clients.identify_species(
        image_bytes, file.filename or "upload.jpg", file.content_type or "image/jpeg"
    )
    if result is None:
        raise HTTPException(502, "Vision service is unavailable.")
    return result


@app.post("/api/chat", response_model=AgentResponse)
def api_chat(req: AgentRequest) -> AgentResponse:
    """Proxy → Agent service (RAG chat with history)."""
    result = clients.ask_agent(req.message, [m.model_dump() for m in req.history])
    if result is None:
        raise HTTPException(502, "Assistant service is unavailable.")
    return result


@app.post("/diagnose", response_model=DiagnoseResponse)
async def diagnose(
    file: UploadFile | None = File(default=None),
    question: str = Form(default="Give me care advice for this plant."),
    temperature_c: float | None = Form(default=None),
    humidity_pct: float | None = Form(default=None),
    soil_moisture_pct: float | None = Form(default=None),
    light_hours: float | None = Form(default=None),
    soil_ph: float | None = Form(default=None),
    watering_freq_per_week: float | None = Form(default=None),
    fertilizer_freq_per_month: float | None = Form(default=None),
    plant_age_months: float | None = Form(default=None),
) -> DiagnoseResponse:
    services_called: list[str] = []

    # 1) Vision — identify species/disease from the image (if provided).
    species = None
    if file is not None:
        image_bytes = await file.read()
        species = clients.identify_species(
            image_bytes, file.filename or "upload.jpg", file.content_type or "image/jpeg"
        )
        if species is not None:
            services_called.append("dl")

    # 2) Structured ML — health risk (only if ALL conditions supplied).
    local_vals = locals()
    conditions = {f: local_vals[f] for f in _CONDITION_FIELDS}
    health_pred = None
    if all(v is not None for v in conditions.values()):
        health_pred = clients.predict_health(conditions)
        if health_pred is not None:
            services_called.append("ml")

    # 3) Agent — fuse everything into grounded, actionable advice.
    query = build_advice_query(species, health_pred, question)
    agent_resp = clients.ask_agent(query)
    if agent_resp is not None:
        services_called.append("agent")
        advice, citations = agent_resp.answer, agent_resp.citations
    else:
        advice, citations = fallback_advice(species, health_pred), []

    response = DiagnoseResponse(
        species=species,
        health=health_pred,
        advice=advice,
        citations=citations,
        services_called=services_called,
    )

    # Persist best-effort: a database hiccup must never fail a diagnosis.
    try:
        await db.save_diagnosis(
            question=question,
            species_label=species.label if species else None,
            species_confidence=species.confidence if species else None,
            health_label=health_pred.risk_label if health_pred else None,
            health_risk_score=health_pred.risk_score if health_pred else None,
            advice=advice,
            citations=[c.model_dump() for c in citations],
            services_called=services_called,
        )
    except Exception as exc:
        log.warning(f"diagnosis persistence failed: {exc}")

    return response


@app.get("/history")
async def history(limit: int = 20) -> dict:
    """Recent persisted diagnoses — the gateway's database-backed feature."""
    limit = max(1, min(limit, 100))
    return {"diagnoses": await db.list_recent(limit)}
