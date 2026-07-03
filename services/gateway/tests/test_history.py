"""Diagnosis persistence: /diagnose writes a row, /history reads it back."""

from __future__ import annotations

import io

from fastapi.testclient import TestClient
from flora_common.schemas import AgentResponse, Citation, SpeciesPrediction

from floragateway import api, clients, db
from floragateway.config import settings


def _species():
    return SpeciesPrediction(
        label="monstera", confidence=0.91, top_k=[{"monstera": 0.91}],
        model_version="dl-v1", low_confidence=False,
    )


def test_diagnose_persists_and_history_returns_it(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "database_url", f"sqlite+aiosqlite:///{tmp_path}/gw.db")
    db.reset()

    monkeypatch.setattr(clients, "identify_species", lambda *a, **k: _species())
    monkeypatch.setattr(clients, "predict_health", lambda *a, **k: None)
    monkeypatch.setattr(
        clients,
        "ask_agent",
        lambda *a, **k: AgentResponse(
            answer="Water less.",
            citations=[Citation(source="watering.md", snippet="...")],
            tools_used=[],
        ),
    )

    client = TestClient(api.app)
    resp = client.post(
        "/diagnose",
        data={"question": "Is it healthy?"},
        files={"file": ("leaf.jpg", io.BytesIO(b"img"), "image/jpeg")},
    )
    assert resp.status_code == 200

    hist = client.get("/history").json()["diagnoses"]
    assert len(hist) == 1
    entry = hist[0]
    assert entry["species_label"] == "monstera"
    assert entry["question"] == "Is it healthy?"
    assert entry["advice"] == "Water less."
    assert entry["services_called"] == ["dl", "agent"]
    assert entry["health_label"] is None  # ML was down — recorded honestly


def test_db_failure_does_not_break_diagnosis(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "database_url", "sqlite+aiosqlite:///Z:/nonexistent/x.db")
    db.reset()

    monkeypatch.setattr(clients, "identify_species", lambda *a, **k: _species())
    monkeypatch.setattr(clients, "predict_health", lambda *a, **k: None)
    monkeypatch.setattr(clients, "ask_agent", lambda *a, **k: None)

    client = TestClient(api.app)
    resp = client.post(
        "/diagnose", files={"file": ("a.jpg", io.BytesIO(b"x"), "image/jpeg")}
    )
    assert resp.status_code == 200  # diagnosis still succeeds
    db.reset()
