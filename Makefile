# FloraAI developer shortcuts.
# On Windows without `make`, run the underlying commands shown for each target,
# or use Git Bash / WSL. Each service is also runnable standalone.

PY ?= python

.PHONY: help install lint test \
        ml-train ml-serve dl-data dl-train dl-serve \
        agent-ingest agent-serve gateway-serve compose-up

help:
	@echo "FloraAI targets:"
	@echo "  install        install shared lib + all service deps"
	@echo "  test           run the full pytest suite"
	@echo "  ml-train       generate data, train, evaluate, serialize the ML model"
	@echo "  ml-serve       run the ML FastAPI service       (:8001)"
	@echo "  dl-data        prepare the image dataset"
	@echo "  dl-train       transfer-learn the vision model"
	@echo "  dl-serve       run the DL FastAPI service        (:8002)"
	@echo "  agent-ingest   build the RAG vector store"
	@echo "  agent-serve    run the Agent FastAPI service     (:8003)"
	@echo "  gateway-serve  run the orchestration gateway     (:8000)"
	@echo "  compose-up     docker compose up --build (whole platform)"

install:
	$(PY) -m pip install -e shared
	$(PY) -m pip install -r services/ml/requirements.txt
	$(PY) -m pip install -r services/dl/requirements.txt
	$(PY) -m pip install -r services/agent/requirements.txt
	$(PY) -m pip install -r services/gateway/requirements.txt

lint:
	$(PY) -m ruff check . || true

test:
	$(PY) -m pytest -q

# ── Module 1: ML ──────────────────────────────────────────────────────────
ml-train:
	cd services/ml && $(PY) -m floraml.generate_data
	cd services/ml && $(PY) -m floraml.train
ml-serve:
	cd services/ml && $(PY) -m uvicorn floraml.api:app --host 0.0.0.0 --port 8001 --reload

# ── Module 2: DL ──────────────────────────────────────────────────────────
dl-data:
	cd services/dl && $(PY) -m floradl.data --prepare
dl-train:
	cd services/dl && $(PY) -m floradl.train
dl-serve:
	cd services/dl && $(PY) -m uvicorn floradl.api:app --host 0.0.0.0 --port 8002 --reload

# ── Module 3: Agent ───────────────────────────────────────────────────────
agent-ingest:
	cd services/agent && $(PY) -m floraagent.ingest
agent-serve:
	cd services/agent && $(PY) -m uvicorn floraagent.api:app --host 0.0.0.0 --port 8003 --reload

# ── Gateway ───────────────────────────────────────────────────────────────
gateway-serve:
	cd services/gateway && $(PY) -m uvicorn floragateway.api:app --host 0.0.0.0 --port 8000 --reload

compose-up:
	docker compose up --build
