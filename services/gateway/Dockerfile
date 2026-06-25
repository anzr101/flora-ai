# Orchestration gateway image. Build context = repo root.
#   docker build -f services/gateway/Dockerfile -t floraai-gateway .
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY shared/ /app/shared/
COPY services/gateway/requirements.txt /app/services/gateway/requirements.txt
RUN pip install -e /app/shared && \
    pip install -r /app/services/gateway/requirements.txt

COPY services/gateway/ /app/services/gateway/
WORKDIR /app/services/gateway

EXPOSE 8000
CMD ["uvicorn", "floragateway.api:app", "--host", "0.0.0.0", "--port", "8000"]
