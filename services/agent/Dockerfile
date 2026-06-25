# Module 3 — Agent (RAG) service image. Build context = repo root.
#   docker build -f services/agent/Dockerfile -t floraai-agent .
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY shared/ /app/shared/
COPY services/agent/requirements.txt /app/services/agent/requirements.txt
RUN pip install -e /app/shared && \
    pip install -r /app/services/agent/requirements.txt

COPY services/agent/ /app/services/agent/
WORKDIR /app/services/agent

# Build the vector store at image build time so the container is ready to serve.
# (Downloads the ONNX embedding model once during build.)
RUN python -m floraagent.ingest

EXPOSE 8003
CMD ["uvicorn", "floraagent.api:app", "--host", "0.0.0.0", "--port", "8003"]
