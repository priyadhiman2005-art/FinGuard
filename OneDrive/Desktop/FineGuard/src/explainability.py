"""
FinGuard - Explainability Engine (SHAP & Fallback Heuristic)
============================================================
Explains why an entity was flagged as high or low financial risk.
Features:
1. SHAP TreeExplainer for Random Forest (TreeSHAP)
2. Resilient Rule-Based Fallback Explainer (if SHAP is unavailable)
3. Transparent feature attribution breakdown (Risk Drivers vs Mitigators)

Integrity Disclosure:
SHAP values quantify statistical feature attribution to the model's prediction.
They represent mathematical associations within the dataset and do NOT constitute
legal, forensic, or causal proof of intentional accounting fraud or corporate mismanagement.
"""

import logging
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import shap

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

CAUSAL_DISCLAIMER = (
    "Educational & Analytical Disclaimer: Model explanations and SHAP feature attributions "
    "reflect empirical correlations learned by the machine learning algorithm on historical ratios. "
    "They do NOT constitute causal proof, forensic verification, or legal evidence of fraud, "
    "misrepresentation, or regulatory non-compliance."
)


class FinGuardExplainer:
    def __init__(self, model: Any, feature_names: List[str], background_data: Optional[np.ndarray] = None):
        self.model = model
        self.feature_names = feature_names
        self.background_data = background_data
        self.shap_explainer = None
        self._init_shap()

    def _init_shap(self):
        """Attempt initializing SHAP TreeExplainer."""
        try:
            # TreeExplainer is fast and exact for tree ensemble models
            self.shap_explainer = shap.TreeExplainer(self.model)
            logger.info("SHAP TreeExplainer successfully initialized.")
        except Exception as e:
            logger.warning(f"Could not initialize SHAP TreeExplainer ({e}). Fallback explainer will be used.")
            self.shap_explainer = None

    def explain_instance(
        self,
        x_scaled: np.ndarray,
        raw_values: Optional[Dict[str, float]] = None,
        top_k: int = 8
    ) -> Dict[str, Any]:
        """
        Explain a single corporate instance's predicted risk score.
        Attempts SHAP TreeExplainer first; falls back smoothly to heuristic if unavailable.
        """
        if x_scaled.ndim == 1:
            x_scaled = x_scaled.reshape(1, -1)

        # 1. Try SHAP explanation
        if self.shap_explainer is not None:
            try:
                shap_values = self.shap_explainer.shap_values(x_scaled)
                
                # Check SHAP output dimension (handles both list of arrays for binary or 3D array)
                if isinstance(shap_values, list):
                    vals = shap_values[1][0]  # Class 1 (Bankrupt)
                elif hasattr(shap_values, "shape") and len(shap_values.shape) == 3:
                    vals = shap_values[0, :, 1]
                else:
                    vals = shap_values[0]

                return self._format_shap_output(vals, x_scaled[0], raw_values, top_k)
            except Exception as e:
                logger.warning(f"SHAP runtime computation failed: {e}. Executing fallback explainer.")

        # 2. Resilient Rule-Based Fallback
        return self._format_fallback_output(x_scaled[0], raw_values, top_k)

    def _format_shap_output(
        self,
        shap_vals: np.ndarray,
        scaled_vals: np.ndarray,
        raw_values: Optional[Dict[str, float]],
        top_k: int
    ) -> Dict[str, Any]:
        """Format SHAP values into positive risk contributors and mitigating factors."""
        records = []
        for i, name in enumerate(self.feature_names):
            val = float(shap_vals[i])
            scaled_v = float(scaled_vals[i])
            raw_v = raw_values.get(name, scaled_v) if raw_values else scaled_v

            records.append({
                "feature": name,
                "shap_value": round(val, 5),
                "impact": "Increases Risk" if val > 0 else "Decreases Risk",
                "scaled_value": round(scaled_v, 4),
                "reported_value": round(float(raw_v), 4) if isinstance(raw_v, (int, float)) else str(raw_v)
            })

        # Sort by absolute SHAP impact
        records.sort(key=lambda r: abs(r["shap_value"]), reverse=True)
        top_drivers = records[:top_k]

        risk_increasing = [r for r in top_drivers if r["shap_value"] > 0]
        risk_decreasing = [r for r in top_drivers if r["shap_value"] < 0]

        return {
            "status": "SUCCESS",
            "method": "SHAP (TreeExplainer)",
            "top_drivers": top_drivers,
            "risk_increasing_factors": risk_increasing,
            "risk_mitigating_factors": risk_decreasing,
            "disclaimer": CAUSAL_DISCLAIMER
        }

    def _format_fallback_output(
        self,
        scaled_vals: np.ndarray,
        raw_values: Optional[Dict[str, float]],
        top_k: int
    ) -> Dict[str, Any]:
        """
        Deterministic fallback explainer using RobustScaler deviation (median-centered).
        Identifies ratios exhibiting severe divergence from training population median.
        """
        records = []
        for i, name in enumerate(self.feature_names):
            scaled_v = float(scaled_vals[i])
            raw_v = raw_values.get(name, scaled_v) if raw_values else scaled_v
            
            # Since RobustScaler centers on median, |scaled_v| indicates IQR deviations
            records.append({
                "feature": name,
                "deviation_iqr": round(scaled_v, 4),
                "shap_value": round(scaled_v * 0.05, 5),  # Heuristic proxy for display
                "impact": "Increases Risk" if scaled_v > 0.5 or scaled_v < -0.5 else "Neutral",
                "scaled_value": round(scaled_v, 4),
                "reported_value": round(float(raw_v), 4) if isinstance(raw_v, (int, float)) else str(raw_v)
            })

        records.sort(key=lambda r: abs(r["deviation_iqr"]), reverse=True)
        top_drivers = records[:top_k]

        return {
            "status": "FALLBACK",
            "method": "Heuristic Deviation Explainer (Median IQR Relative Offset)",
            "top_drivers": top_drivers,
            "risk_increasing_factors": [r for r in top_drivers if "Risk" in r["impact"]],
            "risk_mitigating_factors": [r for r in top_drivers if "Risk" not in r["impact"]],
            "disclaimer": CAUSAL_DISCLAIMER
        }

