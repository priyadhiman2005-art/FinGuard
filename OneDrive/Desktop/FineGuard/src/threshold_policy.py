"""
FinGuard - Risk Threshold & Capacity Policy Module
==================================================
Implements operational review constraints and cost-sensitive threshold optimization:
1. Top-5% Review Capacity Policy (operational constraint under limited audit bandwidth)
2. Cost-Sensitive Threshold Policy (asymmetric loss: Missed Default = 20x False Alarm)

Key Distinctions:
- Review-Capacity Policy: Fixed audit budget. Flags at most top k% highest-risk entities, 
  independent of absolute probability.
- Probability Threshold: Risk-appetite decision boundary. Flags any entity with P(default) >= tau,
  minimizing expected financial loss regardless of audit headcount.
"""

from typing import List, Dict, Any, Optional, Tuple, Union
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score


def apply_capacity_policy(
    probabilities: Union[List[float], np.ndarray, pd.Series],
    capacity_pct: float = 0.05,
    company_ids: Optional[List[Any]] = None,
    tie_breaker: str = "first"
) -> Dict[str, Any]:
    """
    Flag at most top `capacity_pct` (default 5%) of eligible companies ranked by risk probability.
    
    Safety guarantees:
    - 'No more than top 5%': Uses floor(N * capacity_pct) so we never breach review bandwidth.
    - Small dataset handling: If N < 20 and capacity_pct=0.05, capacity is 0 (or documented minimum).
      If N == 0, returns empty safely.
    - Strict tie handling: When multiple companies share the exact cutoff probability, 
      deterministic tie-breaking ensures capacity limit is never exceeded.
    """
    probas = np.asarray(probabilities, dtype=float)
    n = len(probas)
    
    if n == 0:
        return {
            "total_companies": 0,
            "review_capacity": 0,
            "flagged_count": 0,
            "flagged_indices": [],
            "flagged_company_ids": [],
            "cutoff_probability": None,
            "flagged_mask": np.array([], dtype=bool)
        }

    if company_ids is None:
        ids = [f"Company_{i+1}" for i in range(n)]
    else:
        ids = list(company_ids)

    # Review capacity rule: strictly no more than top capacity_pct
    max_capacity = int(np.floor(n * capacity_pct))

    if max_capacity == 0:
        return {
            "total_companies": n,
            "review_capacity": 0,
            "flagged_count": 0,
            "flagged_indices": [],
            "flagged_company_ids": [],
            "cutoff_probability": None,
            "flagged_mask": np.zeros(n, dtype=bool),
            "note": f"Dataset size (N={n}) with capacity {capacity_pct*100}% yields 0 review slots under strict floor."
        }

    # Deterministic ranking: Sort descending by probability, break ties stably by original index
    df = pd.DataFrame({
        "original_idx": np.arange(n),
        "id": ids,
        "probability": probas
    })

    # Sort descending by probability; stable tie-breaking preserves first occurrence
    df_sorted = df.sort_values(by="probability", ascending=False, kind="mergesort").reset_index(drop=True)

    flagged_df = df_sorted.iloc[:max_capacity]
    flagged_indices = flagged_df["original_idx"].tolist()
    flagged_ids = flagged_df["id"].tolist()
    cutoff_proba = float(flagged_df["probability"].iloc[-1])

    flagged_mask = np.zeros(n, dtype=bool)
    flagged_mask[flagged_indices] = True

    return {
        "total_companies": n,
        "review_capacity": max_capacity,
        "flagged_count": len(flagged_indices),
        "flagged_indices": flagged_indices,
        "flagged_company_ids": flagged_ids,
        "cutoff_probability": round(cutoff_proba, 4),
        "flagged_mask": flagged_mask,
        "note": f"Flagged top {len(flagged_indices)} companies ({round(len(flagged_indices)/n * 100, 2)}% of portfolio)."
    }


def analyze_threshold_cost(
    y_true: Union[List[int], np.ndarray, pd.Series],
    y_probas: Union[List[float], np.ndarray, pd.Series],
    fn_cost_ratio: float = 20.0,
    fp_cost: float = 1.0,
    threshold_steps: int = 100
) -> Dict[str, Any]:
    """
    Evaluate financial impact across probability decision thresholds from 0.01 to 0.99.
    Cost Ratio: Missed Default (FN) costs 20x a False Alarm (FP).
    Total Loss = (FP * 1.0) + (FN * 20.0)
    """
    y_t = np.asarray(y_true, dtype=int)
    y_p = np.asarray(y_probas, dtype=float)

    thresholds = np.linspace(0.01, 0.99, threshold_steps)
    cost_records = []

    min_cost = float("inf")
    optimal_threshold = 0.5
    optimal_point = {}

    for tau in thresholds:
        y_pred = (y_p >= tau).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_t, y_pred, labels=[0, 1]).ravel()
        
        cost = (fp * fp_cost) + (fn * fn_cost_ratio)
        prec = precision_score(y_t, y_pred, zero_division=0)
        rec = recall_score(y_t, y_pred, zero_division=0)
        f1 = f1_score(y_t, y_pred, zero_division=0)

        record = {
            "threshold": round(float(tau), 4),
            "tp": int(tp),
            "fp": int(fp),
            "tn": int(tn),
            "fn": int(fn),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1": round(float(f1), 4),
            "flagged_count": int(tp + fp),
            "flagged_pct": round(float((tp + fp) / len(y_t) * 100), 2),
            "total_cost": round(float(cost), 2)
        }
        cost_records.append(record)

        if cost < min_cost:
            min_cost = cost
            optimal_threshold = tau
            optimal_point = record

    return {
        "fn_cost_ratio": fn_cost_ratio,
        "fp_cost": fp_cost,
        "optimal_threshold": round(float(optimal_threshold), 4),
        "minimum_cost": round(float(min_cost), 2),
        "optimal_metrics": optimal_point,
        "cost_curve": cost_records
    }

