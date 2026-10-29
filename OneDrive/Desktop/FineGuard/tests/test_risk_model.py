"""
Unit tests for FinGuard Bankruptcy Risk Models
Testing model loading, inference shapes, probability bounds, and metrics.
"""

import os
import joblib
import numpy as np
import pytest
from src.risk_model import (
    load_processed_data,
    BASELINE_MODEL_PATH,
    IMPROVED_MODEL_PATH,
    PREPROCESSOR_PATH,
    EVAL_RESULTS_PATH,
    evaluate_model_performance
)


def test_models_and_artifacts_exist():
    assert os.path.exists(PREPROCESSOR_PATH), "Preprocessor artifact must exist."
    assert os.path.exists(BASELINE_MODEL_PATH), "Baseline LR artifact must exist."
    assert os.path.exists(IMPROVED_MODEL_PATH), "Improved RF artifact must exist."
    assert os.path.exists(EVAL_RESULTS_PATH), "Evaluation results JSON must exist."


def test_model_inference_and_probability_ranges():
    preprocessor = joblib.load(PREPROCESSOR_PATH)
    rf_model = joblib.load(IMPROVED_MODEL_PATH)
    lr_model = joblib.load(BASELINE_MODEL_PATH)

    _, X_test, y_test, _, _ = load_processed_data()
    X_test_scaled = preprocessor.transform(X_test)

    # Probabilities should be bounded in [0, 1] and sum to 1.0
    rf_probas = rf_model.predict_proba(X_test_scaled)
    lr_probas = lr_model.predict_proba(X_test_scaled)

    assert rf_probas.shape == (len(X_test), 2)
    assert lr_probas.shape == (len(X_test), 2)

    assert (rf_probas >= 0.0).all() and (rf_probas <= 1.0).all()
    assert (lr_probas >= 0.0).all() and (lr_probas <= 1.0).all()
    assert np.allclose(rf_probas.sum(axis=1), 1.0)
    assert np.allclose(lr_probas.sum(axis=1), 1.0)


def test_evaluation_metrics_validity():
    preprocessor = joblib.load(PREPROCESSOR_PATH)
    rf_model = joblib.load(IMPROVED_MODEL_PATH)
    _, X_test, _, y_test, _ = load_processed_data()
    X_test_scaled = preprocessor.transform(X_test)

    metrics = evaluate_model_performance(
        rf_model, X_test_scaled, y_test, model_name="Improved RF", threshold=0.5
    )

    assert metrics["actual_defaults"] == 44
    assert metrics["actual_non_defaults"] == 1320
    assert 0.0 <= metrics["precision"] <= 1.0
    assert 0.0 <= metrics["recall"] <= 1.0
    assert 0.0 <= metrics["roc_auc"] <= 1.0
    assert 0.0 <= metrics["pr_auc"] <= 1.0
    assert metrics["roc_auc"] > 0.85, "Random forest ROC-AUC should demonstrate strong discrimination."

