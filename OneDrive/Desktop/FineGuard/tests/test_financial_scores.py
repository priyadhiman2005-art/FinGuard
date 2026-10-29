"""
Unit tests for FinGuard Financial Risk & Fraud Indicators
Testing: Altman Z-Score, Beneish M-Score, Piotroski F-Score, and helper utilities.
"""

import pytest
from src.financial_ratios import safe_divide, validate_financial_inputs
from src.fraud_scores import (
    calculate_altman_z_score,
    calculate_beneish_m_score,
    calculate_piotroski_f_score
)


# =====================================================================
# 1. HELPER & VALIDATION TESTS
# =====================================================================
def test_safe_divide():
    assert safe_divide(10, 2) == 5.0
    assert safe_divide(10, 0) == 0.0
    assert safe_divide(10, 0, default=-1.0) == -1.0
    assert safe_divide(None, 5) == 0.0
    assert safe_divide(5, None) == 0.0
    assert safe_divide(float("nan"), 5) == 0.0
    assert safe_divide(5, float("nan")) == 0.0
    assert safe_divide(float("inf"), 5) == 0.0


def test_validate_financial_inputs():
    valid_data = {"a": 100, "b": "200.5", "c": 0}
    is_valid, missing = validate_financial_inputs(valid_data, ["a", "b", "c"])
    assert is_valid is True
    assert len(missing) == 0

    invalid_data = {"a": 100, "b": None, "c": "not_a_number"}
    is_valid, missing = validate_financial_inputs(invalid_data, ["a", "b", "c", "d"])
    assert is_valid is False
    assert "b" in missing
    assert "c" in missing
    assert "d" in missing


# =====================================================================
# 2. ALTMAN Z-SCORE TESTS
# =====================================================================
def test_altman_z_score_manufacturing_healthy():
    """
    Healthy public manufacturing company:
    High working capital, healthy retained earnings, solid EBIT, high equity value.
    Expected: Safe Zone (Z > 2.99)
    """
    res = calculate_altman_z_score(
        working_capital=500,
        total_assets=1000,
        retained_earnings=400,
        ebit=200,
        market_value_equity=1500,
        total_liabilities=500,
        sales=1200,
        is_manufacturing=True
    )
    assert res["status"] == "SUCCESS"
    assert res["zone"] == "Safe Zone"
    assert res["risk_level"] == "Low"
    assert res["score"] > 2.99


def test_altman_z_score_manufacturing_distressed():
    """
    Distressed public manufacturing company:
    Negative working capital, negative retained earnings, negative EBIT, heavy liabilities.
    Expected: Distress Zone (Z < 1.81)
    """
    res = calculate_altman_z_score(
        working_capital=-200,
        total_assets=1000,
        retained_earnings=-300,
        ebit=-100,
        market_value_equity=100,
        total_liabilities=1200,
        sales=400,
        is_manufacturing=True
    )
    assert res["status"] == "SUCCESS"
    assert res["zone"] == "Distress Zone"
    assert res["risk_level"] == "High"
    assert res["score"] < 1.81


def test_altman_z_score_non_manufacturing():
    """
    Emerging market / non-manufacturing formula (1983 Double-Prime Z'').
    Does not require sales input.
    """
    res = calculate_altman_z_score(
        working_capital=300,
        total_assets=1000,
        retained_earnings=200,
        ebit=150,
        market_value_equity=800,
        total_liabilities=400,
        sales=None,
        is_manufacturing=False
    )
    assert res["status"] == "SUCCESS"
    assert "Non-Manufacturing" in res["model_type"]
    assert res["zone"] == "Safe Zone"
    assert res["score"] > 2.60


def test_altman_z_score_missing_inputs_returns_incomplete():
    """Rule check: Never fabricate fake scores when required inputs are missing."""
    res = calculate_altman_z_score(
        working_capital=100,
        total_assets=500,
        retained_earnings=None,  # Missing
        ebit=50,
        market_value_equity=200,
        total_liabilities=300,
        sales=600,
        is_manufacturing=True
    )
    assert res["status"] == "INCOMPLETE_DATA"
    assert res["score"] is None
    assert "retained_earnings" in res["message"]


def test_altman_z_score_invalid_assets():
    res = calculate_altman_z_score(
        working_capital=100,
        total_assets=0,
        retained_earnings=50,
        ebit=50,
        market_value_equity=200,
        total_liabilities=300,
        sales=600,
        is_manufacturing=True
    )
    assert res["status"] == "INVALID_ASSETS"
    assert res["score"] is None


# =====================================================================
# 3. BENEISH M-SCORE TESTS
# =====================================================================
def test_beneish_m_score_non_manipulator():
    """Normal stable company: M <= -1.78 indicates low probability of manipulation."""
    res = calculate_beneish_m_score(
        sales_t=1000, sales_t_minus_1=950,
        cogs_t=600, cogs_t_minus_1=570,
        receivables_t=150, receivables_t_minus_1=145,
        current_assets_t=400, current_assets_t_minus_1=390,
        ppe_t=500, ppe_t_minus_1=480,
        securities_t=50, securities_t_minus_1=50,
        total_assets_t=1000, total_assets_t_minus_1=950,
        depreciation_t=50, depreciation_t_minus_1=48,
        sga_t=120, sga_t_minus_1=115,
        long_term_debt_t=200, long_term_debt_t_minus_1=200,
        current_liabilities_t=150, current_liabilities_t_minus_1=145,
        net_income_t=80, cfo_t=85  # Accruals negative/small (healthy CFO)
    )
    assert res["status"] == "SUCCESS"
    assert res["is_flagged"] is False
    assert res["score"] <= -1.78
    assert "Unlikely Manipulator" in res["manipulation_flag"]


def test_beneish_m_score_likely_manipulator():
    """
    Company exhibiting red flags:
    Huge receivables surge (DSRI >> 1), gross margin distortion (GMI >> 1),
    massive accruals (Net Income = 300 while CFO = -100).
    Expected: M > -1.78 (Likely Manipulator).
    """
    res = calculate_beneish_m_score(
        sales_t=1500, sales_t_minus_1=1000,
        cogs_t=600, cogs_t_minus_1=650,
        receivables_t=600, receivables_t_minus_1=150,  # Massive receivables surge
        current_assets_t=800, current_assets_t_minus_1=400,
        ppe_t=500, ppe_t_minus_1=450,
        securities_t=10, securities_t_minus_1=50,
        total_assets_t=1500, total_assets_t_minus_1=1000,
        depreciation_t=20, depreciation_t_minus_1=50,  # Lower depreciation rate
        sga_t=100, sga_t_minus_1=150,
        long_term_debt_t=600, long_term_debt_t_minus_1=200,  # Leverage spike
        current_liabilities_t=300, current_liabilities_t_minus_1=100,
        net_income_t=350, cfo_t=-150  # Huge accruals gap
    )
    assert res["status"] == "SUCCESS"
    assert res["is_flagged"] is True
    assert res["score"] > -1.78
    assert "Likely Manipulator" in res["manipulation_flag"]


def test_beneish_m_score_missing_inputs():
    res = calculate_beneish_m_score(
        sales_t=1000, sales_t_minus_1=950,
        cogs_t=600, cogs_t_minus_1=570,
        receivables_t=150, receivables_t_minus_1=145,
        current_assets_t=400, current_assets_t_minus_1=390,
        ppe_t=500, ppe_t_minus_1=480,
        securities_t=50, securities_t_minus_1=50,
        total_assets_t=1000, total_assets_t_minus_1=950,
        depreciation_t=50, depreciation_t_minus_1=48,
        sga_t=120, sga_t_minus_1=115,
        long_term_debt_t=200, long_term_debt_t_minus_1=200,
        current_liabilities_t=150, current_liabilities_t_minus_1=145,
        net_income_t=80, cfo_t=None  # Missing CFO
    )
    assert res["status"] == "INCOMPLETE_DATA"
    assert res["score"] is None
    assert "cfo_t" in res["message"]


# =====================================================================
# 4. PIOTROSKI F-SCORE TESTS
# =====================================================================
def test_piotroski_f_score_strong():
    """
    Company satisfying all 9 fundamental criteria:
    Positive ROA, positive CFO, Delta ROA > 0, CFO > Net Income,
    Decreased Leverage, Increased Current Ratio, No Share Dilution,
    Increased Gross Margin, Increased Asset Turnover.
    Expected: Score = 9, Strong Fundamental Health.
    """
    res = calculate_piotroski_f_score(
        net_income_t=120, net_income_t_minus_1=80,
        cfo_t=150,  # CFO > Net Income
        total_assets_t=1000, total_assets_t_minus_1=1000,
        long_term_debt_t=100, long_term_debt_t_minus_1=150,  # Leverage down
        current_assets_t=400, current_assets_t_minus_1=350,
        current_liabilities_t=200, current_liabilities_t_minus_1=200,  # Current ratio up (2.0 > 1.75)
        shares_t=1000, shares_t_minus_1=1000,  # No dilution
        gross_margin_t=0.35, gross_margin_t_minus_1=0.30,  # Margin up
        sales_t=1200, sales_t_minus_1=1000  # Asset turnover up (1.2 > 1.0)
    )
    assert res["status"] == "SUCCESS"
    assert res["score"] == 9
    assert res["category"] == "Strong Fundamental Health"
    assert res["risk_level"] == "Low"


def test_piotroski_f_score_weak():
    """
    Deteriorating company:
    Negative ROA, negative CFO, deteriorating margins, increasing debt, share dilution.
    Expected: Score <= 3, Weak Fundamental Health.
    """
    res = calculate_piotroski_f_score(
        net_income_t=-50, net_income_t_minus_1=20,
        cfo_t=-80,  # CFO < Net Income (-80 < -50)
        total_assets_t=1200, total_assets_t_minus_1=1000,
        long_term_debt_t=600, long_term_debt_t_minus_1=300,  # Leverage surged
        current_assets_t=200, current_assets_t_minus_1=300,
        current_liabilities_t=300, current_liabilities_t_minus_1=200,  # Current ratio crashed
        shares_t=1500, shares_t_minus_1=1000,  # Heavy dilution (+50%)
        gross_margin_t=0.15, gross_margin_t_minus_1=0.25,  # Margin crashed
        sales_t=800, sales_t_minus_1=1000  # Turnover fell
    )
    assert res["status"] == "SUCCESS"
    assert res["score"] <= 3
    assert res["category"] == "Weak Fundamental Health"
    assert res["risk_level"] == "High"


def test_piotroski_f_score_missing_inputs():
    res = calculate_piotroski_f_score(
        net_income_t=100, net_income_t_minus_1=None,  # Missing prior period
        cfo_t=120,
        total_assets_t=1000, total_assets_t_minus_1=950,
        long_term_debt_t=200, long_term_debt_t_minus_1=200,
        current_assets_t=400, current_assets_t_minus_1=350,
        current_liabilities_t=200, current_liabilities_t_minus_1=200,
        shares_t=1000, shares_t_minus_1=1000,
        gross_margin_t=0.30, gross_margin_t_minus_1=0.28,
        sales_t=1100, sales_t_minus_1=1000
    )
    assert res["status"] == "INCOMPLETE_DATA"
    assert res["score"] is None
    assert "net_income_t_minus_1" in res["message"]

