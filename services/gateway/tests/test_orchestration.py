"""Tests for the orchestration logic and the /diagnose flow.

Downstream services are monkeypatched, so these run with no network and prove
the composition + graceful-degradation behaviour in isolation.
"""

from __future__ import annotations

import io

from fastapi.testclient import TestClient
from flora_common.schemas import AgentResponse, Citation, HealthPrediction, SpeciesPrediction

from floragateway import api, clients
from floragateway.orchestration import build_advice_query, fallback_advice


def _species(low=False):
    return SpeciesPrediction(
        label="monstera", confidence=0.91, top_k=[{"monstera": 0.91}],
        model_version="dl-v1", low_confidence=low,
    )


def _health():
    return HealthPrediction(
        risk_label="at_risk", risk_score=0.62,
        class_probabilities={"healthy": 0.38, "at_risk": 0.5, "diseased": 0.12},
        top_drivers=[{"soil_moisture_pct": 0.4}], model_version="ml-v1",
    )


def test_build_advice_query_includes_both_signals():
    q = build_advice_query(_species(), _health(), "why is it sick?")
    assert "monstera" in q
    assert "at_risk" in q
    assert "soil_moisture_pct" in q
    assert "why is it sick?" in q


def test_build_advice_query_flags_low_confidence_species():
    q = build_advice_query(_species(low=True), None, "help")
    assert "uncertain" in q.lower()


def test_fallback_advice_used_without_agent():
    txt = fallback_advice(_species(), _health())
    assert "monstera" in txt and "at_risk" in txt


def test_diagnose_fuses_all_three(monkeypatch):
    monkeypatch.setattr(clients, "identify_species", lambda *a, **k: _species())
    monkeypatch.setattr(clients, "predict_health", lambda *a, **k: _health())
    monkeypatch.setattr(
        clients,
        "ask_agent",
        lambda *a, **k: AgentResponse(
            answer="Reduce watering and improve drainage.",
            citations=[Citation(source="watering.md", snippet="overwatering...")],
            tools_used=["search_botanical_knowledge"],
        ),
    )
    client = TestClient(api.app)
    img = io.BytesIO(b"fake-image-bytes")
    resp = client.post(
        "/diagnose",
        data={
            "question": "What's wrong?",
            "temperature_c": 24, "humidity_pct": 40, "soil_moisture_pct": 80,
            "light_hours": 6, "soil_ph": 6.5, "watering_freq_per_week": 7,
            "fertilizer_freq_per_month": 1, "plant_age_months": 12,
        },
        files={"file": ("leaf.jpg", img, "image/jpeg")},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["species"]["label"] == "monstera"
    assert body["health"]["risk_label"] == "at_risk"
    assert "drainage" in body["advice"]
    assert set(body["services_called"]) == {"dl", "ml", "agent"}


def test_diagnose_degrades_when_agent_down(monkeypatch):
    monkeypatch.setattr(clients, "identify_species", lambda *a, **k: _species())
    monkeypatch.setattr(clients, "predict_health", lambda *a, **k: None)  # ML down too
    monkeypatch.setattr(clients, "ask_agent", lambda *a, **k: None)       # agent down
    client = TestClient(api.app)
    img = io.BytesIO(b"x")
    resp = client.post("/diagnose", files={"file": ("a.jpg", img, "image/jpeg")})
    assert resp.status_code == 200
    body = resp.json()
    # Still returns a useful response from the vision result + fallback advice.
    assert body["species"]["label"] == "monstera"
    assert body["services_called"] == ["dl"]
    assert "offline" in body["advice"].lower()
