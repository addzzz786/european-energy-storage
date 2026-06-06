import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import pytest
from src.data_pipeline import fetch_agsi_storage


def test_storage_no_negative_values():
    """Storage fill percentage cannot be below zero."""
    df = fetch_agsi_storage(
        country_code="eu",
        start="2022-01-01",
        end="2022-03-31"
    )
    assert (df["full_pct"] >= 0).all(), "Negative storage values found"


def test_storage_no_duplicate_dates():
    """Each date should appear exactly once."""
    df = fetch_agsi_storage(
        country_code="eu",
        start="2022-01-01",
        end="2022-03-31"
    )
    assert df.index.is_unique, "Duplicate dates found in index"


def test_storage_correct_dtypes():
    """All numeric columns should be float64."""
    df = fetch_agsi_storage(
        country_code="eu",
        start="2022-01-01",
        end="2022-03-31"
    )
    for col in ["full_pct", "injection", "withdrawal", "working_gas_volume"]:
        assert df[col].dtype == "float64", f"{col} is not float64"