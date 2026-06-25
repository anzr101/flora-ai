# FloraAI · Module 3 — Agentic RAG

A botanical assistant that **reasons and acts**, not just chats. It grounds every
answer in a curated knowledge base (RAG) and can call the other FloraAI services
as tools.

## What it does
- **RAG:** retrieves from a local vector store built from the `knowledge/` docs
  and answers with **citations**.
- **Tool calling:** `search_botanical_knowledge` (retrieval) and
  `predict_plant_health` (calls the ML service for a structured prediction).
- **Multi-step reasoning:** Claude decides which tools to use and in what order,
  up to `max_tool_iterations`.

## Cost-aware design
- **Embeddings run locally** via `fastembed` (ONNX, torch-free) — Claude has no
  embeddings API and embedding a static KB per-token would be wasteful.
- **Generation uses `claude-haiku-4-5`** (config-driven) — cents per dev cycle.
- **No LLM key?** The service degrades to a retrieval-only answer so RAG still
  demonstrably works.

## Run
```bash
pip install -r requirements.txt
python -m floraagent.ingest        # build the vector store
python -m floraagent.eval          # retrieval hit@k + MRR
uvicorn floraagent.api:app --port 8003
FLORA_EMBED_BACKEND=hash pytest     # offline tests (no downloads)
```

## Example
```bash
curl -X POST localhost:8003/chat -H "Content-Type: application/json" \
  -d '{"message": "My monstera has yellow lower leaves and the soil is always wet. What do I do?"}'
```

## Evaluation
`eval.py` scores retrieval against a hand-labelled gold set (question → expected
source doc) with **hit@k** and **MRR** — so retrieval quality is a number, not a
vibe.
