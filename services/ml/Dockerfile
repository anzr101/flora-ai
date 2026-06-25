# Module 1 — ML service image.
# Build context is the REPO ROOT so we can install the shared library.
#   docker build -f services/ml/Dockerfile -t floraai-ml .
FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System libs needed by numpy/scipy/shap wheels.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 && rm -rf /var/lib/apt/lists/*

# Install the shared lib first, then service deps (better layer caching).
COPY shared/ /app/shared/
COPY services/ml/requirements.txt /app/services/ml/requirements.txt
RUN pip install -e /app/shared && \
    pip install -r /app/services/ml/requirements.txt

COPY services/ml/ /app/services/ml/

WORKDIR /app/services/ml
EXPOSE 8001

# Train at build time so the image ships a ready-to-serve model. (For large
# real datasets you would instead bake in a pre-trained artifact.)
RUN python -m floraml.generate_data && python -m floraml.train

CMD ["uvicorn", "floraml.api:app", "--host", "0.0.0.0", "--port", "8001"]
