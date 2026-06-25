"""Train, benchmark, and serialize the plant health-risk model.

Pipeline followed (the professional ML lifecycle, made executable):

    load data -> stratified split -> build candidate pipelines
      -> stratified K-fold CV -> bias/variance read -> benchmark
      -> select best -> light hyper-parameter search -> fit
      -> held-out test evaluation -> global SHAP -> serialize + metrics

Everything that touches data statistics lives inside the sklearn Pipeline, so
cross-validation is leakage-free. Run:  python -m floraml.train
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline

from floraml.config import (
    CLASS_NAMES,
    DATA_DIR,
    FEATURE_COLUMNS,
    MODELS_DIR,
    TARGET_COLUMN,
    settings,
)
from floraml.explain import global_importance
from floraml.features import build_preprocessor
from floraml.generate_data import generate

MODEL_PATH = MODELS_DIR / "health_model.joblib"
METRICS_PATH = MODELS_DIR / "metrics.json"


@dataclass
class Candidate:
    name: str
    pipeline: Pipeline
    param_grid: dict


def _load_data() -> pd.DataFrame:
    csv = DATA_DIR / "plant_health.csv"
    if csv.exists():
        return pd.read_csv(csv)
    print("No dataset on disk; generating one now.")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df = generate()
    df.to_csv(csv, index=False)
    return df


def _candidates() -> list[Candidate]:
    """Three models spanning the bias/variance spectrum, for an honest benchmark."""
    return [
        Candidate(
            name="logreg",  # high bias / linear baseline — should LOSE to trees
            pipeline=Pipeline(
                [
                    ("pre", build_preprocessor(scale=True)),
                    ("model", LogisticRegression(max_iter=2000)),
                ]
            ),
            param_grid={"model__C": [0.1, 1.0, 3.0]},
        ),
        Candidate(
            name="random_forest",
            pipeline=Pipeline(
                [
                    ("pre", build_preprocessor(scale=False)),
                    ("model", RandomForestClassifier(random_state=settings.random_seed, n_jobs=-1)),
                ]
            ),
            param_grid={
                "model__n_estimators": [300],
                "model__max_depth": [None, 16],
                "model__min_samples_leaf": [1, 4],
            },
        ),
        Candidate(
            name="hist_gbm",  # expected winner on this DGP
            pipeline=Pipeline(
                [
                    ("pre", build_preprocessor(scale=False)),
                    ("model", HistGradientBoostingClassifier(random_state=settings.random_seed)),
                ]
            ),
            param_grid={
                "model__max_depth": [None, 8],
                "model__learning_rate": [0.05, 0.1],
                "model__max_iter": [300],
            },
        ),
    ]


def _benchmark(candidates, X_train, y_train, cv) -> list[dict]:
    """Cross-validate every candidate and read off bias/variance signals."""
    rows = []
    for cand in candidates:
        res = cross_validate(
            cand.pipeline,
            X_train,
            y_train,
            cv=cv,
            scoring=["accuracy", "f1_macro"],
            return_train_score=True,
            n_jobs=-1,
        )
        cv_f1 = res["test_f1_macro"].mean()
        train_f1 = res["train_f1_macro"].mean()
        rows.append(
            {
                "model": cand.name,
                "cv_f1_macro": round(float(cv_f1), 4),
                "cv_f1_std": round(float(res["test_f1_macro"].std()), 4),
                "cv_accuracy": round(float(res["test_accuracy"].mean()), 4),
                "train_f1_macro": round(float(train_f1), 4),
                # train-minus-CV gap is a direct overfitting (variance) signal.
                "overfit_gap": round(float(train_f1 - cv_f1), 4),
            }
        )
        print(
            f"  {cand.name:<14} cv_f1={cv_f1:.4f} (±{res['test_f1_macro'].std():.3f})  "
            f"train_f1={train_f1:.4f}  overfit_gap={train_f1 - cv_f1:+.4f}"
        )
    return rows


def main() -> None:
    t0 = time.time()
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    df = _load_data()
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN].astype(str)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=settings.test_size, stratify=y, random_state=settings.random_seed
    )
    cv = StratifiedKFold(n_splits=settings.cv_folds, shuffle=True, random_state=settings.random_seed)

    candidates = _candidates()

    print("\n=== Cross-validated benchmark (leakage-safe; train folds only) ===")
    bench = _benchmark(candidates, X_train, y_train, cv)
    best_row = max(bench, key=lambda r: r["cv_f1_macro"])
    best = next(c for c in candidates if c.name == best_row["model"])
    print(f"\nBest by CV macro-F1: {best.name} ({best_row['cv_f1_macro']:.4f})")

    print("\n=== Hyper-parameter search on best model ===")
    search = GridSearchCV(
        best.pipeline, best.param_grid, scoring="f1_macro", cv=cv, n_jobs=-1
    )
    search.fit(X_train, y_train)
    print(f"  Best params: {search.best_params_}")
    print(f"  Best CV macro-F1: {search.best_score_:.4f}")
    model = search.best_estimator_

    print("\n=== Held-out test evaluation ===")
    y_pred = model.predict(X_test)
    test_acc = accuracy_score(y_test, y_pred)
    test_f1 = f1_score(y_test, y_pred, average="macro")
    print(f"  accuracy={test_acc:.4f}  macro_f1={test_f1:.4f}")
    print(classification_report(y_test, y_pred, target_names=sorted(set(y))))
    cm = confusion_matrix(y_test, y_pred, labels=CLASS_NAMES)

    print("\n=== Global feature importance (SHAP) ===")
    try:
        importance = global_importance(model, X_train.sample(min(1000, len(X_train)),
                                        random_state=settings.random_seed))
        for feat, val in list(importance.items())[:8]:
            print(f"  {feat:<18} {val:.4f}")
    except Exception as exc:  # SHAP is best-effort; never block training on it
        print(f"  SHAP unavailable ({exc}); skipping global importance.")
        importance = {}

    joblib.dump(model, MODEL_PATH)
    metrics = {
        "model_version": f"{best.name}-v{__import__('floraml').__version__}",
        "selected_model": best.name,
        "best_params": {k: str(v) for k, v in search.best_params_.items()},
        "cv_benchmark": bench,
        "test_accuracy": round(float(test_acc), 4),
        "test_macro_f1": round(float(test_f1), 4),
        "confusion_matrix": {"labels": CLASS_NAMES, "matrix": cm.tolist()},
        "global_importance": {k: round(float(v), 5) for k, v in importance.items()},
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "trained_seconds": round(time.time() - t0, 1),
    }
    METRICS_PATH.write_text(json.dumps(metrics, indent=2))
    print(f"\nSaved model  -> {MODEL_PATH}")
    print(f"Saved metrics -> {METRICS_PATH}")
    print(f"Done in {metrics['trained_seconds']}s.")


if __name__ == "__main__":
    main()
