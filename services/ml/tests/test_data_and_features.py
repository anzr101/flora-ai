"""Unit tests for the data generator and feature engineering (no model needed)."""

from __future__ import annotations

import numpy as np

from floraml.config import CLASS_NAMES, FEATURE_COLUMNS, TARGET_COLUMN
from floraml.features import engineer, engineered_feature_names
from floraml.generate_data import generate


def test_generator_is_deterministic():
    a = generate(n=500, seed=7)
    b = generate(n=500, seed=7)
    assert a.equals(b), "same seed must produce identical data"


def test_generator_schema_and_classes():
    df = generate(n=1000, seed=1)
    assert list(df.columns) == FEATURE_COLUMNS + [TARGET_COLUMN]
    assert set(df[TARGET_COLUMN].unique()).issubset(set(CLASS_NAMES))
    # The DGP is imbalanced but should produce every class.
    assert df[TARGET_COLUMN].nunique() == 3


def test_no_nans_in_raw_features():
    df = generate(n=1000, seed=2)
    assert df[FEATURE_COLUMNS].isna().sum().sum() == 0


def test_engineer_adds_expected_columns_and_is_pure():
    df = generate(n=200, seed=3)
    out = engineer(df)
    assert list(out.columns) == engineered_feature_names()
    # Pure function: re-running yields identical output.
    assert np.allclose(out.values, engineer(df).values, equal_nan=True)


def test_heat_dry_stress_interaction_is_nonzero_when_hot_and_dry():
    import pandas as pd

    hot_dry = pd.DataFrame(
        [{c: 0 for c in FEATURE_COLUMNS}]
    )
    hot_dry.loc[0, "temperature_c"] = 40
    hot_dry.loc[0, "soil_moisture_pct"] = 5
    assert engineer(hot_dry)["heat_dry_stress"].iloc[0] > 0
