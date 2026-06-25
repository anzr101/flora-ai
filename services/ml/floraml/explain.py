"""Model explainability with SHAP.

Two audiences:
- `global_importance` — for the model card / stakeholders: which features matter
  on average. Used at training time and surfaced in metrics.json.
- `local_drivers` — for the end user: which features pushed THIS plant toward its
  predicted risk. Used by the API so every prediction is explainable.

SHAP is treated as best-effort: tree models get an exact, fast `TreeExplainer`;
if anything goes wrong we degrade gracefully rather than failing a prediction.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from floraml.features import engineered_feature_names


def _transform(model: Pipeline, X: pd.DataFrame) -> np.ndarray:
    """Apply every step except the final estimator, returning the model matrix."""
    return model[:-1].transform(X)


def _shap_values(model: Pipeline, X: pd.DataFrame):
    """Return SHAP values array shaped (n_samples, n_features, n_classes)."""
    import shap  # imported lazily so the package is optional at import time

    estimator = model.named_steps["model"]
    Xt = _transform(model, X)
    explainer = shap.TreeExplainer(estimator)
    vals = explainer.shap_values(Xt)

    # Normalise across SHAP versions: older returns a list (one array per class),
    # newer returns a single (n, features, classes) array.
    if isinstance(vals, list):
        vals = np.stack(vals, axis=-1)
    elif vals.ndim == 2:  # binary fallback -> add a class axis
        vals = vals[:, :, None]
    return vals  # (n, features, classes)


def global_importance(model: Pipeline, X: pd.DataFrame) -> dict[str, float]:
    """Mean absolute SHAP value per feature, aggregated over classes, sorted desc."""
    vals = _shap_values(model, X)
    names = engineered_feature_names()
    mean_abs = np.abs(vals).mean(axis=(0, 2))  # average over samples and classes
    order = np.argsort(mean_abs)[::-1]
    return {names[i]: float(mean_abs[i]) for i in order}


def local_drivers(model: Pipeline, x_row: pd.DataFrame, class_index: int, top_k: int = 4):
    """Top signed feature contributions for one sample's PREDICTED class.

    Positive => pushed the plant toward the predicted (worse) class. Returns a
    list of {feature: value} dicts ready to drop into the API response.
    """
    try:
        vals = _shap_values(model, x_row)  # (1, features, classes)
        names = engineered_feature_names()
        contrib = vals[0, :, min(class_index, vals.shape[2] - 1)]
        order = np.argsort(np.abs(contrib))[::-1][:top_k]
        return [{names[i]: round(float(contrib[i]), 4)} for i in order]
    except Exception:
        return []  # explanations are a bonus, never a hard dependency
