"""
Unit tests for FinGuard Threshold Policy and Explainability Engine
"""

import os
import joblib
import numpy as np
import pytest
from src.threshold_policy import apply_capacity_policy, analyze_threshold_cost
from src.explainability import FinGuardExplainer, CAUSAL_DISCLAIMER
from src.risk_model import IMPROVED_MODEL_PATH, PREPROCESSOR_PATH, load_processed_data


def test_capacity_policy_exact_cap_respected():
    # 100 companies -> strictly 5 flagged
    probas = np.linspace(0.01, 0.99, 100)
    res = apply_capacity_policy(probas, capacity_pct=0.05)
    assert res["total_companies"] == 100
    assert res["review_capacity"] == 5
    assert res["flagged_count"] == 5
    assert len(res["flagged_indices"]) == 5
    assert res["flagged_mask"].sum() == 5


def test_capacity_policy_small_dataset_safe():
    # 10 companies -> floor(10 * 0.05) = 0 (no more than 5% rule)
    probas = np.array([0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05])
    res = apply_capacity_policy(probas, capacity_pct=0.05)
    assert res["flagged_count"] == 0
    assert len(res["flagged_indices"]) == 0
    assert not res["flagged_mask"].any()

    # Empty array
    res_empty = apply_capacity_policy([], capacity_pct=0.05)
    assert res_empty["flagged_count"] == 0


def test_capacity_policy_strict_tie_breaking():
    # 20 companies -> capacity = 1
    # Multiple companies have identical highest probability (0.95)
    probas = [0.95, 0.95, 0.95, 0.8, 0.7] + [0.1] * 15
    res = apply_capacity_policy(probas, capacity_pct=0.05)
    assert res["review_capacity"] == 1
    assert res["flagged_count"] == 1, "Must never exceed capacity even when ties exist at boundary."


def test_threshold_cost_analysis_20_to_1():
    y_true = np.array([1, 1, 0, 0, 0, 0, 0, 0, 0, 0])
    # Model assigns high prob to first default, low to second
    y_probas = np.array([0.9, 0.2, 0.1, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05])

    res = analyze_threshold_cost(y_true, y_probas, fn_cost_ratio=20.0, fp_cost=1.0)
    assert res["fn_cost_ratio"] == 20.0
    assert len(res["cost_curve"]) > 0
    assert res["minimum_cost"] is not None
    assert 0.01 <= res["optimal_threshold"] <= 0.99


def test_explainability_shap_and_disclaimer():
    rf_model = joblib.load(IMPROVED_MODEL_PATH)
    preprocessor = joblib.load(PREPROCESSOR_PATH)
    _, X_test, _, _, feature_names = load_processed_data()

    explainer = FinGuardExplainer(rf_model, feature_names)
    assert explainer.shap_explainer is not None

    sample_scaled = preprocessor.transform(X_test.iloc[[0]])
    explanation = explainer.explain_instance(sample_scaled, top_k=5)

    assert explanation["status"] in ["SUCCESS", "FALLBACK"]
    assert len(explanation["top_drivers"]) == 5
    assert CAUSAL_DISCLAIMER in explanation["disclaimer"]
    for d in explanation["top_drivers"]:
        assert "feature" in d
        assert "shap_value" in d
        assert "impact" in d


def test_explainability_fallback():
    # Explainer with no shap_explainer should trigger fallback safely
    _, X_test, _, _, feature_names = load_processed_data()
    explainer = FinGuardExplainer(None, feature_names)
    explainer.shap_explainer = None  # Force fallback

    dummy_scaled = np.zeros((1, len(feature_names)))
    dummy_scaled[0, 0] = 3.5  # High outlier
    dummy_scaled[0, 1] = -2.5

    explanation = explainer.explain_instance(dummy_scaled, top_k=5)
    assert explanation["status"] == "FALLBACK"
    assert "Fallback" in explanation["method"] or "Heuristic" in explanation["method"]
    assert len(explanation["top_drivers"]) == 5
    assert CAUSAL_DISCLAIMER in explanation["disclaimer"]

