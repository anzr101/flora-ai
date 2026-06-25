# FloraAI · Gateway — Orchestration Layer

The single public entrypoint. It holds **no model** — it calls the three
services, fuses their outputs, and returns one coherent result. This is the
component that turns three separate demos into a *platform*.

## The unified flow — `POST /diagnose`

```
image      ─►  DL /identify   ─► species / disease  ┐
conditions ─►  ML /predict    ─► health risk + drivers ├─► Agent /chat (RAG)
question   ───────────────────────────────────────────┘     ─► grounded advice
```

All inputs are optional, and the flow **degrades gracefully**:
- no image → skip vision; no conditions → skip health model; agent down →
  templated fallback advice. Partial results always beat a hard failure.

## Run
```bash
pip install -r requirements.txt
uvicorn floragateway.api:app --port 8000     # http://localhost:8000/docs
pytest
```
The downstream service URLs are config-driven (`FLORA_ML_URL`, `FLORA_DL_URL`,
`FLORA_AGENT_URL`) — localhost by default, service names under docker-compose.

## Example
```bash
curl -X POST localhost:8000/diagnose \
  -F "file=@leaf.jpg" \
  -F "question=Why are the leaves yellowing?" \
  -F "temperature_c=24" -F "humidity_pct=40" -F "soil_moisture_pct=80" \
  -F "light_hours=6" -F "soil_ph=6.5" -F "watering_freq_per_week=7" \
  -F "fertilizer_freq_per_month=1" -F "plant_age_months=12"
```

Returns `{ species, health, advice, citations, services_called }`.

## `GET /health`
Aggregates the health of all three downstream services so an orchestrator can
see the whole platform's status from one call.
