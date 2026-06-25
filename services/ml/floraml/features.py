"""Feature engineering and preprocessing — all leakage-safe.

Every transformation here is *stateless w.r.t. the target* and is wrapped in a
scikit-learn `Pipeline`, so when used inside cross-validation the fit happens on
training folds only. This is the single most important defence against the most
common silent bug in tabular ML: leaking test-set statistics (means, scales)
into training.

The engineered features encode domain knowledge (the same interactions the
data-generating process uses) — this is legitimate: they are deterministic
functions of the raw inputs available at inference time, not of the label.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from floraml.config import FEATURE_COLUMNS


def engineer(df: pd.DataFrame) -> pd.DataFrame:
    """Add domain-informed derived features. Pure function of raw inputs."""
    df = df[FEATURE_COLUMNS].copy()

    # Heat-in-dry-soil interaction — the key non-linearity.
    dryness = (50 - df["soil_moisture_pct"]).clip(lower=0) / 50
    heat = (df["temperature_c"] - 25).clip(lower=0) / 10
    df["heat_dry_stress"] = dryness * heat

    # Departures from horticultural ideals (absolute, so both directions count).
    df["ph_deviation"] = (df["soil_ph"] - 6.5).abs()
    df["temp_deviation"] = (df["temperature_c"] - 22).abs()
    df["light_deviation"] = (df["light_hours"] - 9).abs()

    # Care-balance proxies.
    df["water_per_age"] = df["watering_freq_per_week"] / (df["plant_age_months"] + 1)
    df["vpd_proxy"] = df["temperature_c"] * (1 - df["humidity_pct"] / 100)  # ~vapour pressure deficit

    return df.replace([np.inf, -np.inf], np.nan)


def engineered_feature_names() -> list[str]:
    """Column order produced by `engineer` — used for SHAP labelling."""
    return FEATURE_COLUMNS + [
        "heat_dry_stress",
        "ph_deviation",
        "temp_deviation",
        "light_deviation",
        "water_per_age",
        "vpd_proxy",
    ]


def build_preprocessor(scale: bool) -> Pipeline:
    """Return the preprocessing stage.

    `scale=True` for distance/linear models (LogReg); `scale=False` for tree
    ensembles, which are scale-invariant and faster without it.
    """
    feature_builder = FunctionTransformer(engineer, validate=False)
    names = engineered_feature_names()

    numeric_steps: list = [("impute", SimpleImputer(strategy="median"))]
    if scale:
        numeric_steps.append(("scale", StandardScaler()))

    numeric = Pipeline(numeric_steps)
    coltf = ColumnTransformer([("num", numeric, names)], remainder="drop")

    return Pipeline([("engineer", feature_builder), ("prep", coltf)])
