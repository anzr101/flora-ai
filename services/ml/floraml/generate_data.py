"""Synthetic-but-honest dataset generator for plant health-risk prediction.

WHY SYNTHETIC, AND WHY THIS IS DEFENSIBLE
-----------------------------------------
Publicly available "plant health" *tabular* datasets are almost all synthetic
toy sets of unknown provenance. Rather than download one and silently present it
as real observational data, FloraAI generates its own data from an **explicit,
documented causal process** (a "data-generating process", DGP). This is a
deliberate engineering choice with two honest advantages:

1. We know the ground-truth causal structure, so we can *verify* that the
   trained pipeline recovers it (e.g. SHAP should rank the features we know
   matter). That is a real validation, not a vanity metric.
2. There is zero risk of misrepresenting data provenance in interviews.

The DGP below is non-trivial: the target depends on *non-linear interactions*
(e.g. high temperature is only harmful when soil moisture is also low), there is
class imbalance, and a calibrated amount of label noise so the problem is not
perfectly separable — realistic accuracies land in the high-70s/80s, not 100%.

Run:  python -m floraml.generate_data
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from floraml.config import CLASS_NAMES, DATA_DIR, FEATURE_COLUMNS, TARGET_COLUMN, settings


def _sample_conditions(rng: np.random.Generator, n: int) -> pd.DataFrame:
    """Draw plausibly-distributed environmental + care conditions."""
    return pd.DataFrame(
        {
            "temperature_c": rng.normal(23, 6, n).clip(0, 45),
            "humidity_pct": rng.normal(55, 18, n).clip(5, 100),
            "soil_moisture_pct": rng.normal(45, 20, n).clip(0, 100),
            "light_hours": rng.normal(8, 3, n).clip(0, 18),
            "soil_ph": rng.normal(6.5, 0.9, n).clip(3.5, 9.5),
            "watering_freq_per_week": rng.integers(0, 14, n).astype(float),
            "fertilizer_freq_per_month": rng.integers(0, 12, n).astype(float),
            "plant_age_months": rng.gamma(shape=2.0, scale=18, size=n).clip(0, 480),
        }
    )


def _stress_index(df: pd.DataFrame) -> np.ndarray:
    """Latent physiological stress — the true cause of the health label.

    Each term is a soft penalty for departing from a healthy operating range.
    The temperature×moisture term is a genuine INTERACTION: heat stress is much
    worse when the soil is dry. Tree models should pick this up; a purely linear
    model should underperform — which is exactly what we want to demonstrate.
    """
    # Distance-from-ideal penalties (ideal values chosen from horticulture norms).
    temp_pen = ((df["temperature_c"] - 22) / 10) ** 2
    hum_pen = ((df["humidity_pct"] - 55) / 30) ** 2
    moist_pen = ((df["soil_moisture_pct"] - 50) / 30) ** 2
    light_pen = ((df["light_hours"] - 9) / 5) ** 2
    ph_pen = ((df["soil_ph"] - 6.5) / 1.2) ** 2

    # Care penalties: both neglect and over-care hurt.
    water_pen = ((df["watering_freq_per_week"] - 4) / 4) ** 2
    fert_pen = ((df["fertilizer_freq_per_month"] - 2) / 3) ** 2

    # Non-linear interaction: heat is far more damaging in dry soil.
    dryness = (50 - df["soil_moisture_pct"]).clip(lower=0) / 50
    heat = (df["temperature_c"] - 25).clip(lower=0) / 10
    interaction = 2.5 * dryness * heat

    # Older plants are slightly more resilient to transient stress.
    age_resilience = 0.15 * np.tanh(df["plant_age_months"] / 120)

    stress = (
        temp_pen + hum_pen + moist_pen + light_pen + ph_pen
        + 0.8 * water_pen + 0.6 * fert_pen + interaction - age_resilience
    )
    return stress.to_numpy()


def generate(n: int | None = None, seed: int | None = None) -> pd.DataFrame:
    n = n or settings.n_samples
    seed = settings.random_seed if seed is None else seed
    rng = np.random.default_rng(seed)

    df = _sample_conditions(rng, n)
    stress = _stress_index(df)

    # Inject label noise so the decision boundary is not perfectly learnable
    # (realistic), then bucket by QUANTILE so the marginal class prevalence is a
    # sensible, mildly-imbalanced [~45% healthy, ~35% at_risk, ~20% diseased].
    # Quantile thresholds keep the causal ordering (more stress -> worse class)
    # while decoupling it from the arbitrary absolute scale of the stress index.
    noise = rng.normal(0, 0.5, n) * stress.std()
    score = stress + noise
    t_healthy, t_atrisk = np.quantile(score, [0.45, 0.80])
    labels = np.where(score < t_healthy, 0, np.where(score < t_atrisk, 1, 2))

    df[TARGET_COLUMN] = pd.Categorical.from_codes(labels, categories=CLASS_NAMES)
    return df[FEATURE_COLUMNS + [TARGET_COLUMN]]


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df = generate()
    out = DATA_DIR / "plant_health.csv"
    df.to_csv(out, index=False)
    dist = df[TARGET_COLUMN].value_counts(normalize=True).round(3).to_dict()
    print(f"Wrote {len(df):,} rows -> {out}")
    print(f"Class distribution: {dist}")


if __name__ == "__main__":
    main()
