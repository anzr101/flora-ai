"""Exploratory Data Analysis for the plant-health dataset.

Prints summary statistics, class balance, and feature/target signal, and saves a
correlation heatmap + class-distribution plot to `reports/`. EDA is part of the
lifecycle: you look before you model, to catch imbalance, leakage, and which
features carry signal.

Run:  python -m floraml.eda
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from floraml.config import DATA_DIR, FEATURE_COLUMNS, SERVICE_ROOT, TARGET_COLUMN
from floraml.generate_data import generate

REPORTS_DIR = SERVICE_ROOT / "reports"


def _load() -> pd.DataFrame:
    csv = DATA_DIR / "plant_health.csv"
    return pd.read_csv(csv) if csv.exists() else generate()


def main() -> None:
    df = _load()
    print("=== Shape ===")
    print(df.shape)

    print("\n=== Class balance ===")
    print(df[TARGET_COLUMN].value_counts(normalize=True).round(3).to_string())

    print("\n=== Feature summary ===")
    print(df[FEATURE_COLUMNS].describe().round(2).T.to_string())

    print("\n=== Missing values ===")
    print(df.isna().sum().to_string())

    # Signal check: mean of each feature per class (ANOVA-style eyeball).
    print("\n=== Feature means by class (signal check) ===")
    print(df.groupby(TARGET_COLUMN, observed=True)[FEATURE_COLUMNS].mean().round(2).T.to_string())

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        # Class distribution
        ax = df[TARGET_COLUMN].value_counts().plot(kind="bar", title="Class distribution")
        ax.figure.tight_layout()
        ax.figure.savefig(REPORTS_DIR / "class_distribution.png", dpi=110)
        plt.close(ax.figure)

        # Correlation heatmap
        corr = df[FEATURE_COLUMNS].corr()
        fig, ax = plt.subplots(figsize=(7, 6))
        im = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
        ax.set_xticks(range(len(FEATURE_COLUMNS)))
        ax.set_xticklabels(FEATURE_COLUMNS, rotation=90, fontsize=7)
        ax.set_yticks(range(len(FEATURE_COLUMNS)))
        ax.set_yticklabels(FEATURE_COLUMNS, fontsize=7)
        ax.set_title("Feature correlation")
        fig.colorbar(im, fraction=0.046, pad=0.04)
        fig.tight_layout()
        fig.savefig(REPORTS_DIR / "correlation_heatmap.png", dpi=110)
        plt.close(fig)

        print(f"\nSaved plots -> {REPORTS_DIR}")
    except Exception as exc:
        print(f"\n(Plotting skipped: {exc})")


if __name__ == "__main__":
    main()
