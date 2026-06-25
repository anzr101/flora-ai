# FloraAI · Module 1 — Classical ML

**Problem:** predict a plant's **health-risk class** (`healthy` / `at_risk` /
`diseased`) from eight structured environmental & care features.

**Why classical ML:** on low-dimensional structured data, gradient-boosted trees
beat deep nets — cheaper, faster, and explainable with SHAP.

## Lifecycle (all runnable)

```
generate_data.py  ─► documented synthetic DGP (no provenance lies)
features.py       ─► leakage-safe preprocessing + domain feature engineering
train.py          ─► stratified CV · bias/variance read · benchmark
                     · hyper-param search · held-out test · SHAP · serialize
explain.py        ─► global + per-prediction SHAP
api.py            ─► FastAPI: /health /info /predict
```

## Run

```bash
pip install -r requirements.txt
python -m floraml.generate_data     # -> data/plant_health.csv
python -m floraml.train             # -> models/health_model.joblib + metrics.json
uvicorn floraml.api:app --port 8001 # -> http://localhost:8001/docs
pytest                              # unit + API tests
```

## Example request

```bash
curl -X POST localhost:8001/predict -H "Content-Type: application/json" -d '{
  "temperature_c": 38, "humidity_pct": 20, "soil_moisture_pct": 8,
  "light_hours": 14, "soil_ph": 8.5, "watering_freq_per_week": 0,
  "fertilizer_freq_per_month": 0, "plant_age_months": 5 }'
```

Returns the risk label, calibrated class probabilities, **and the top SHAP
drivers for that specific plant** — so every prediction is explainable.

## Design notes (interview-ready)

- **No leakage:** imputation/scaling live *inside* the sklearn `Pipeline`, fit on
  CV training folds only.
- **Honest data:** synthetic from an explicit causal process with injected label
  noise → realistic high-70s/80s macro-F1, not a suspicious 100%.
- **Benchmark, not one model:** LogReg (linear baseline) vs RandomForest vs
  HistGBM, with the train-vs-CV gap reported as an overfitting signal.
- **Explainability is first-class:** SHAP global importance in the model card,
  local drivers in every response.
