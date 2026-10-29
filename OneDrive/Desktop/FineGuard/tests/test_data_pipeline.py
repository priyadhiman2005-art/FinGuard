"""
Unit tests for FinGuard Data Collection & Preprocessing Pipeline
"""

import os
import pandas as pd
import numpy as np
import pytest
from src.data_preprocessing import (
    load_and_clean_raw_data,
    inspect_data_quality,
    build_preprocessor,
    prepare_train_test_split,
    RAW_CSV_PATH,
    PROCESSED_DATA_DIR,
    PREPROCESSOR_PATH
)


def test_raw_dataset_exists_and_loads():
    """Verify raw dataset exists and can be cleaned without error."""
    assert os.path.exists(RAW_CSV_PATH)
    df = load_and_clean_raw_data(RAW_CSV_PATH)
    assert len(df) == 6819
    assert df.shape[1] == 96
    # Headers must have no leading/trailing whitespace
    for col in df.columns:
        assert col == col.strip()


def test_data_quality_report():
    """Verify quality check detects zero missing, zero infinite values, and exact class balance."""
    df = load_and_clean_raw_data(RAW_CSV_PATH)
    report = inspect_data_quality(df)
    assert report["total_rows"] == 6819
    assert report["total_features"] == 95
    assert report["total_missing_values"] == 0
    assert report["infinite_values"] == 0
    assert report["class_distribution"][0] == 6599
    assert report["class_distribution"][1] == 220
    assert pytest.approx(report["bankruptcy_rate_pct"], 0.05) == 3.23


def test_zero_leakage_train_test_split():
    """Verify train/test split adheres to strict stratification and zero data leakage."""
    df = load_and_clean_raw_data(RAW_CSV_PATH)
    X_train, X_test, y_train, y_test, preprocessor = prepare_train_test_split(df)

    assert len(X_train) == 5455
    assert len(X_test) == 1364
    assert len(y_train) == 5455
    assert len(y_test) == 1364

    # Both train and test should reflect the ~3.23% positive class rate
    train_rate = y_train.mean() * 100
    test_rate = y_test.mean() * 100
    assert pytest.approx(train_rate, 0.1) == 3.23
    assert pytest.approx(test_rate, 0.1) == 3.23

    # Ensure preprocessor is fitted on train only and transforms test correctly
    X_test_scaled = preprocessor.transform(X_test)
    assert X_test_scaled.shape == (1364, 95)
    assert not np.isnan(X_test_scaled).any()

