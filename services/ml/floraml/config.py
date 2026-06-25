"""Configuration for the ML service.

Paths are resolved relative to the service root so the module behaves the same
whether it is run from the repo root, the service directory, or inside a
container.
"""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

SERVICE_ROOT = Path(__file__).resolve().parent.parent  # services/ml/
DATA_DIR = SERVICE_ROOT / "data"
MODELS_DIR = SERVICE_ROOT / "models"

# The eight structured features the platform exposes. Defined once here and
# reused by the generator, the trainer, and the API so they can never drift.
FEATURE_COLUMNS = [
    "temperature_c",
    "humidity_pct",
    "soil_moisture_pct",
    "light_hours",
    "soil_ph",
    "watering_freq_per_week",
    "fertilizer_freq_per_month",
    "plant_age_months",
]
TARGET_COLUMN = "health_label"
CLASS_NAMES = ["healthy", "at_risk", "diseased"]


class MLSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FLORA_ML_", extra="ignore")

    random_seed: int = 42
    n_samples: int = 12_000
    test_size: float = 0.2
    cv_folds: int = 5
    # Below this max class probability the API flags the prediction uncertain.
    confidence_floor: float = 0.45


settings = MLSettings()
