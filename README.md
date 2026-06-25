# 🌿 FloraAI — Botanical AI Ecosystem

> An end-to-end AI platform for botanical intelligence. **Classical ML** for
> structured prediction, **Deep Learning** for visual understanding, and an
> **Agentic RAG** assistant for reasoning — each independently deployable and
> orchestrated behind a single FastAPI gateway.

FloraAI is intentionally **not** "three models solving the same problem." Each
paradigm owns the part of the platform it is genuinely best at, mirroring how
production AI systems are actually composed:

| Module | Paradigm | Problem it owns | Input |
|--------|----------|-----------------|-------|
| **`services/ml`** | Classical ML (scikit-learn) | Plant **health-risk** prediction | Structured/tabular conditions |
| **`services/dl`** | Deep Learning (PyTorch) | Plant **disease / species** recognition | Leaf images |
| **`services/agent`** | Agentic RAG (Claude + local embeddings) | Botanical **reasoning & care advice** | Natural language |
| **`services/gateway`** | Orchestration (FastAPI) | The **unified flow** that combines all three | Image + conditions + question |
| **`frontend/`** | Next.js 14 + TypeScript | Premium product UI over the whole platform | Browser |

## The unified flow (what makes this more than three demos)

```
User uploads leaf photo  ─►  DL service identifies species / disease
        + conditions     ─►  ML service scores health risk + drivers
        + question       ─►  Agent retrieves care knowledge (RAG)
                          ─►  Agent synthesises ONE grounded recommendation
```

That orchestration is implemented in [`services/gateway`](services/gateway/) at
`POST /diagnose`.

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full diagram, contracts, and the
**engineering decisions + trade-offs** (this is the document to read before an
interview).

## Quick start

```bash
# 0. Python 3.10+  ·  copy env  ·  install the shared lib everywhere
cp .env.example .env          # then paste your ANTHROPIC_API_KEY

# 1. ML module — generates data, trains, and serves real predictions
make ml-train                 # writes models/health_model.joblib + metrics
make ml-serve                 # http://localhost:8001/docs

# 2. DL module — build the dataset, then train (GPU recommended)
make dl-data                  # downloads/links PlantVillage into data/
make dl-train                 # transfer learning; writes models/species.pt
make dl-serve                 # http://localhost:8002/docs

# 3. Agent — ingest knowledge base, then serve
make agent-ingest             # builds the local vector store
make agent-serve              # http://localhost:8003/docs

# 4. Gateway — orchestrates everything
make gateway-serve            # http://localhost:8000/docs

# 5. Frontend — the premium product UI (talks to the gateway)
cd frontend && npm install && npm run dev   # http://localhost:3000

# …or run the whole backend in containers:
docker compose up --build
```

## Engineering standards enforced here

- **No data leakage:** all preprocessing lives inside the sklearn `Pipeline`
  (fit on train folds only); the DL split is **group-aware** so the same plant
  never spans train and test.
- **Honest metrics:** the ML data is *synthetic with a documented causal
  process* (never claimed to be real); the DL pipeline ships an **out-of-distribution
  test** so reported accuracy reflects real-world photos, not dataset artifacts.
- **API-first:** every model is a FastAPI service with typed Pydantic contracts,
  health checks, and OpenAPI docs — never a notebook.
- **Reproducible:** fixed seeds, pinned deps, `make` targets, Dockerfiles, CI.
- **Cost-aware:** the agent uses **free local embeddings** and a cheap Claude
  model for generation, so RAG runs comfortably under a $5 budget.

## Repository layout

```
flora_ai/
├── shared/flora_common/     # config, logging, cross-service Pydantic schemas
├── services/
│   ├── ml/                  # Module 1 — classical ML (trains + serves)
│   ├── dl/                  # Module 2 — computer vision
│   ├── agent/               # Module 3 — agentic RAG
│   └── gateway/             # orchestration layer
├── docker-compose.yml       # run the whole platform
├── ARCHITECTURE.md          # decisions, contracts, trade-offs
└── RESUME_AND_INTERVIEW.md  # how to present this + likely interview questions
```

## License

MIT — see [LICENSE](LICENSE).
