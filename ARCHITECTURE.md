# FloraAI — Architecture & Engineering Decisions

This document is the "why" behind FloraAI. It is written to be read **before an
interview**: every section pairs a decision with the trade-off it resolves.

## 1. System topology

```
                          ┌────────────┐
            User ───────► │  Gateway   │  FastAPI  (:8000)
                          │ /diagnose  │
                          └─────┬──────┘
            ┌───────────────────┼────────────────────┐
            ▼                   ▼                     ▼
      ┌───────────┐       ┌───────────┐         ┌───────────┐
      │  ML svc   │       │  DL svc   │         │ Agent svc │
      │  (:8001)  │       │  (:8002)  │         │  (:8003)  │
      │ sklearn   │       │ PyTorch   │         │ RAG+Claude│
      └───────────┘       └───────────┘         └─────┬─────┘
                                                      ▼
                                            ┌──────────────────┐
                                            │ local vectorstore │
                                            │  (Chroma + MiniLM)│
                                            └──────────────────┘
```

Each box is an independently deployable FastAPI app with its own Dockerfile and
dependency set. The gateway is a **thin orchestrator** — it holds no model, only
typed HTTP clients and the composition logic. This is the microservice trade-off
made deliberately: more moving parts, but each module can be scaled, deployed,
and reasoned about in isolation, and a failure in one degrades gracefully
instead of taking the platform down.

## 2. Why three paradigms, not three models of the same thing

The most common portfolio anti-pattern is "I tried Logistic Regression, a CNN,
and an LLM on the same task and compared accuracy." That demonstrates none of
the three well. FloraAI assigns each paradigm the problem class it is actually
best at:

- **Tabular structured prediction → gradient-boosted trees / sklearn.** On
  low-dimensional structured data, tree ensembles beat deep nets and are
  cheaper, faster, and explainable (SHAP). 
- **High-dimensional perceptual input → CNN transfer learning.** Images have
  spatial structure that convolution exploits; classical ML cannot.
- **Open-ended reasoning over text knowledge → LLM + RAG.** Neither of the above
  can explain *why* a plant is at risk or answer "is this plant safe for cats?"

## 3. Module contracts

All inter-service payloads are defined once in
[`shared/flora_common/schemas.py`](shared/flora_common/schemas.py). The gateway
imports the same models the services emit, so the contract cannot drift.

| Endpoint | Service | Request → Response |
|----------|---------|--------------------|
| `POST /predict` | ML | `PlantConditions` → `HealthPrediction` |
| `POST /identify` | DL | image file → `SpeciesPrediction` |
| `POST /chat` | Agent | `AgentRequest` → `AgentResponse` |
| `POST /diagnose` | Gateway | image + conditions + question → `DiagnoseResponse` |

## 4. Leakage & evaluation — the decisions that make this "engineering"

### ML module
- **Preprocessing inside the Pipeline.** Imputation/scaling/encoding are fit on
  training folds only, *inside* `sklearn.Pipeline`, so cross-validation cannot
  leak test statistics into training. This is the #1 silent bug in tabular ML.
- **Synthetic data, declared.** Public "plant health" tabular datasets are
  almost all synthetic toy sets. Rather than pass one off as real, FloraAI ships
  a **documented generative process** (`generate_data.py`) with an explicit
  causal structure and injected noise. The honest framing — "I generated data
  with a known causal DGP so I could validate that my pipeline recovers it" — is
  a *stronger* interview story than a dubious Kaggle CSV.
- **Stratified K-fold CV + held-out test**, bias/variance read from
  train-vs-CV gap, model benchmarking across LogReg / RandomForest / HistGBM.

### DL module
- **Group-aware split.** PlantVillage has multiple photos of the *same* leaf;
  a naive random split leaks near-duplicates into the test set and inflates
  accuracy to ~99%. FloraAI splits by source group so a leaf never spans sets.
- **Out-of-distribution test.** PlantVillage models are known to cheat off
  uniform backgrounds. We keep a small **field-photo OOD set** and report the
  accuracy drop. Surfacing that gap is the point — it is honest ML.
- **Abstention.** The API returns `low_confidence=True` below a threshold rather
  than confidently mislabelling an out-of-distribution image.

### Agent module
- **RAG, not memorisation.** Answers are grounded in retrieved knowledge-base
  chunks and return **citations**. An eval harness (`eval.py`) measures
  retrieval hit-rate and answer groundedness on a small labelled set, so "the
  chatbot works" becomes a number.

## 5. Cost & model choices

- **Embeddings run locally** (`all-MiniLM-L6-v2`, 80MB, CPU-fine). Claude has no
  embeddings endpoint, and paying per-token to embed a static KB would be waste.
- **Generation uses `claude-haiku-4-5`** — the cheapest capable Claude model —
  so an entire development cycle of RAG queries costs cents, not dollars.
- The model id is config-driven; swap to a larger Claude model in `.env` for
  production without touching code.

## 6. Production concerns addressed

- **Config** via `pydantic-settings` + `.env` (12-factor); no hardcoded secrets.
- **Structured logging** shared across services.
- **Health checks** (`/health`) on every service for orchestrators/load balancers.
- **Graceful degradation:** the gateway returns partial results if a downstream
  service is unavailable, rather than failing the whole request.
- **Containerised** per service + `docker-compose` for the full platform.
- **CI** (GitHub Actions) runs linting and the test suite on every push.

## 7. What is intentionally left as "next steps"

Honesty about scope is itself a signal of seniority:
- Model + data **monitoring/drift detection** is stubbed, not wired to a live
  dashboard (would add Evidently/Prometheus in a real deployment).
- The DL model ships as a **pipeline you train**, not pretrained weights — the
  repo is reproducible rather than shipping a 100MB binary.
- A real deployment would add auth, rate limiting, and a managed vector DB.
