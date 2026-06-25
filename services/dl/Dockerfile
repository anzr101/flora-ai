# Module 2 — DL service image. Build context = repo root.
#   docker build -f services/dl/Dockerfile -t floraai-dl .
#
# Ships CPU torch to keep the image runnable anywhere. The image expects a
# trained checkpoint at services/dl/models/species.pt (mounted via compose or
# baked in by uncommenting the training step below).
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

COPY shared/ /app/shared/
COPY services/dl/requirements.txt /app/services/dl/requirements.txt
# Install CPU torch explicitly to avoid pulling huge CUDA wheels.
RUN pip install -e /app/shared && \
    pip install --index-url https://download.pytorch.org/whl/cpu torch torchvision && \
    pip install -r /app/services/dl/requirements.txt

COPY services/dl/ /app/services/dl/
WORKDIR /app/services/dl

# To bake a model into the image instead of mounting one, uncomment:
# RUN python -m floradl.data --synthetic && python -m floradl.data --prepare && python -m floradl.train

EXPOSE 8002
CMD ["uvicorn", "floradl.api:app", "--host", "0.0.0.0", "--port", "8002"]
