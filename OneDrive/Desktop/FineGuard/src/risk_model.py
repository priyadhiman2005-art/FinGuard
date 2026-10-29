"""
FinGuard - Bankruptcy Risk Prediction Models
============================================
Provides training, evaluation, comparison, and serialization for:
1. Baseline Model: Class-Weighted Logistic Regression
2. Improved Model: Class-Weighted Balanced Random Forest

Metrics:
- Precision, Recall (Default Detection), F1-Score
- Area Under ROC Curve (ROC-AUC)
- Area Under Precision-Recall Curve (PR-AUC / Average Precision)
- Confusion Matrix & Cost-Weighted Error
"""

import os
import json
import logging
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    classification_report
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROCESSED_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed")
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
PREPROCESSOR_PATH = os.path.join(MODELS_DIR, "preprocessor.joblib")
BASELINE_MODEL_PATH = os.path.join(MODELS_DIR, "baseline_logistic_regression.joblib")
IMPROVED_MODEL_PATH = os.path.join(MODELS_DIR, "random_forest_risk_model.joblib")
EVAL_RESULTS_PATH = os.path.join(MODELS_DIR, "evaluation_results.json")


def load_processed_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, list]:
    """Load pre-split train and test partitions."""
    train_path = os.path.join(PROCESSED_DATA_DIR, "train.csv")
    test_path = os.path.join(PROCESSED_DATA_DIR, "test.csv")

    if not os.path.exists(train_path) or not os.path.exists(test_path):
        from src.data_preprocessing import run_pipeline
        run_pipeline()

    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)

    feature_cols = [c for c in train_df.columns if c != "Bankrupt?"]
    X_train = train_df[feature_cols]
    y_train = train_df["Bankrupt?"]
    X_test = test_df[feature_cols]
    y_test = test_df["Bankrupt?"]

    return X_train, X_test, y_train, y_test, feature_cols


def evaluate_model_performance(
    model: Any,
    X_test_scaled: np.ndarray,
    y_test: pd.Series,
    model_name: str,
    threshold: float = 0.5,
    fn_cost_ratio: float = 20.0
) -> Dict[str, Any]:
    """
    Evaluate binary classification performance with particular focus on:
    - Default detection (Recall)
    - Precision-Recall AUC (PR-AUC), which is honest under severe class imbalance
    - Asymmetric financial cost: Cost(FN) = 20 * Cost(FP)
    """
    y_proba = model.predict_proba(X_test_scaled)[:, 1]
    y_pred = (y_proba >= threshold).astype(int)

    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y_test, y_proba)
    pr_auc = average_precision_score(y_test, y_proba)

    # Cost calculation: FP cost = 1 unit, FN cost = fn_cost_ratio units
    total_cost = (fp * 1.0) + (fn * fn_cost_ratio)

    results = {
        "model_name": model_name,
        "decision_threshold": threshold,
        "total_test_samples": int(len(y_test)),
        "actual_defaults": int(tp + fn),
        "actual_non_defaults": int(tn + fp),
        "true_positives": int(tp),
        "false_positives": int(fp),
        "true_negatives": int(tn),
        "false_negatives": int(fn),
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1_score": round(float(f1), 4),
        "roc_auc": round(float(roc_auc), 4),
        "pr_auc": round(float(pr_auc), 4),
        "asymmetric_cost": round(float(total_cost), 2),
    }

    return results


def train_models() -> Dict[str, Any]:
    """
    Train Baseline (Logistic Regression) and Improved (Random Forest) models,
    evaluate on the unseen test set, log comparisons, and save artifacts.
    """
    os.makedirs(MODELS_DIR, exist_ok=True)

    X_train, X_test, y_train, y_test, feature_names = load_processed_data()

    # Load fitted preprocessor
    if not os.path.exists(PREPROCESSOR_PATH):
        from src.data_preprocessing import run_pipeline
        run_pipeline()

    preprocessor = joblib.load(PREPROCESSOR_PATH)
    logger.info("Transforming train and test sets using fitted preprocessor...")
    X_train_scaled = preprocessor.transform(X_train)
    X_test_scaled = preprocessor.transform(X_test)

    # 1. Baseline Model: Class-Weighted Logistic Regression
    logger.info("Training Baseline Model: Logistic Regression (class_weight='balanced')...")
    baseline_lr = LogisticRegression(
        penalty="l2",
        C=0.1,
        class_weight="balanced",
        solver="lbfgs",
        max_iter=1000,
        random_state=42
    )
    baseline_lr.fit(X_train_scaled, y_train)
    joblib.dump(baseline_lr, BASELINE_MODEL_PATH)
    logger.info(f"Baseline model saved to {BASELINE_MODEL_PATH}")

    # 2. Improved Model: Class-Weighted Balanced Random Forest
    logger.info("Training Improved Model: Random Forest (class_weight='balanced_subsample')...")
    improved_rf = RandomForestClassifier(
        n_estimators=150,
        max_depth=12,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight="balanced_subsample",
        random_state=42,
        n_jobs=-1
    )
    improved_rf.fit(X_train_scaled, y_train)
    joblib.dump(improved_rf, IMPROVED_MODEL_PATH)
    logger.info(f"Improved model saved to {IMPROVED_MODEL_PATH}")

    # Evaluate both models on test set
    baseline_metrics = evaluate_model_performance(
        baseline_lr, X_test_scaled, y_test, model_name="Baseline (Logistic Regression)"
    )
    improved_metrics = evaluate_model_performance(
        improved_rf, X_test_scaled, y_test, model_name="Improved (Random Forest)"
    )

    # Extract Top Features
    rf_importances = improved_rf.feature_importances_
    top_indices = np.argsort(rf_importances)[::-1][:15]
    top_features = [
        {"feature": feature_names[i], "importance": round(float(rf_importances[i]), 5)}
        for i in top_indices
    ]

    all_results = {
        "baseline": baseline_metrics,
        "improved": improved_metrics,
        "top_features": top_features,
        "feature_names": feature_names
    }

    with open(EVAL_RESULTS_PATH, "w") as f:
        json.dump(all_results, f, indent=2)
    logger.info(f"Evaluation results successfully saved to {EVAL_RESULTS_PATH}")

    logger.info("=" * 60)
    logger.info("ACTUAL MODEL EVALUATION RESULTS:")
    logger.info(f"Baseline LR  -> Recall: {baseline_metrics['recall']}, Prec: {baseline_metrics['precision']}, F1: {baseline_metrics['f1_score']}, PR-AUC: {baseline_metrics['pr_auc']}, ROC-AUC: {baseline_metrics['roc_auc']}")
    logger.info(f"Improved RF  -> Recall: {improved_metrics['recall']}, Prec: {improved_metrics['precision']}, F1: {improved_metrics['f1_score']}, PR-AUC: {improved_metrics['pr_auc']}, ROC-AUC: {improved_metrics['roc_auc']}")
    logger.info("=" * 60)

    return all_results


if __name__ == "__main__":
    train_models()

