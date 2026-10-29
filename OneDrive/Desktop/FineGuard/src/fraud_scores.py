"""
FinGuard - Financial Risk & Fraud Indicators
=============================================
Implementation of standard corporate risk and fraud screening models:
1. Altman Z-Score (1968, 1983) - Bankruptcy & Solvency Risk
2. Beneish M-Score (1999) - Financial Statement Earnings Manipulation
3. Piotroski F-Score (2000) - Fundamental Financial Health

Rules:
- Strict input validation: No synthetic score fabrication when data is missing.
- Distinct conceptual scopes: Bankruptcy risk != Accounting manipulation.
"""

from typing import Dict, Any, Optional
from src.financial_ratios import safe_divide, validate_financial_inputs


# =====================================================================
# 1. ALTMAN Z-SCORE (Solvency & Bankruptcy Distress Indicator)
# =====================================================================
def calculate_altman_z_score(
    working_capital: float,
    total_assets: float,
    retained_earnings: float,
    ebit: float,
    market_value_equity: float,
    total_liabilities: float,
    sales: Optional[float] = None,
    is_manufacturing: bool = True
) -> Dict[str, Any]:
    """
    Calculate the Altman Z-Score for bankruptcy prediction.

    Original Manufacturing Model (1968):
        Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 0.999*X5
        Safe Zone:       Z > 2.99
        Grey Zone:       1.81 <= Z <= 2.99
        Distress Zone:   Z < 1.81

    Non-Manufacturing / Private Model (1983 Double-Prime Z''):
        Z'' = 6.56*X1 + 3.26*X2 + 6.72*X3 + 1.05*X4
        Safe Zone:       Z'' > 2.60
        Grey Zone:       1.10 <= Z'' <= 2.60
        Distress Zone:   Z'' < 1.10

    Components:
        X1 = Working Capital / Total Assets
        X2 = Retained Earnings / Total Assets
        X3 = EBIT / Total Assets
        X4 = Market Value Equity / Total Liabilities
        X5 = Sales / Total Assets (omitted in non-manufacturing model)
    """
    inputs = {
        "working_capital": working_capital,
        "total_assets": total_assets,
        "retained_earnings": retained_earnings,
        "ebit": ebit,
        "market_value_equity": market_value_equity,
        "total_liabilities": total_liabilities,
    }
    required = list(inputs.keys())
    if is_manufacturing:
        inputs["sales"] = sales
        required.append("sales")

    is_valid, missing = validate_financial_inputs(inputs, required)
    if not is_valid:
        return {
            "status": "INCOMPLETE_DATA",
            "score": None,
            "zone": "UNKNOWN",
            "model_type": "Manufacturing" if is_manufacturing else "Non-Manufacturing",
            "message": f"Cannot compute Altman Z-Score. Missing or invalid required fields: {', '.join(missing)}",
            "components": {}
        }

    if total_assets <= 0:
        return {
            "status": "INVALID_ASSETS",
            "score": None,
            "zone": "UNKNOWN",
            "model_type": "Manufacturing" if is_manufacturing else "Non-Manufacturing",
            "message": "Total Assets must be strictly greater than zero.",
            "components": {}
        }

    x1 = safe_divide(working_capital, total_assets)
    x2 = safe_divide(retained_earnings, total_assets)
    x3 = safe_divide(ebit, total_assets)
    x4 = safe_divide(market_value_equity, total_liabilities)

    components = {
        "X1_working_capital_to_assets": round(x1, 4),
        "X2_retained_earnings_to_assets": round(x2, 4),
        "X3_ebit_to_assets": round(x3, 4),
        "X4_equity_to_liabilities": round(x4, 4),
    }

    if is_manufacturing:
        x5 = safe_divide(sales, total_assets)
        components["X5_sales_to_assets"] = round(x5, 4)
        z = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 0.999 * x5
        model_name = "Original Public Manufacturing (1968)"
        if z > 2.99:
            zone = "Safe Zone"
            risk_level = "Low"
        elif z >= 1.81:
            zone = "Grey Zone"
            risk_level = "Moderate"
        else:
            zone = "Distress Zone"
            risk_level = "High"
    else:
        z = 6.56 * x1 + 3.26 * x2 + 6.72 * x3 + 1.05 * x4
        model_name = "Non-Manufacturing / Emerging Market Z'' (1983)"
        if z > 2.60:
            zone = "Safe Zone"
            risk_level = "Low"
        elif z >= 1.10:
            zone = "Grey Zone"
            risk_level = "Moderate"
        else:
            zone = "Distress Zone"
            risk_level = "High"

    return {
        "status": "SUCCESS",
        "score": round(z, 3),
        "zone": zone,
        "risk_level": risk_level,
        "model_type": model_name,
        "message": f"Altman Z-Score calculated as {round(z, 3)} ({zone}).",
        "components": components
    }


# =====================================================================
# 2. BENEISH M-SCORE (Financial Statement Manipulation Indicator)
# =====================================================================
def calculate_beneish_m_score(
    sales_t: float,
    sales_t_minus_1: float,
    cogs_t: float,
    cogs_t_minus_1: float,
    receivables_t: float,
    receivables_t_minus_1: float,
    current_assets_t: float,
    current_assets_t_minus_1: float,
    ppe_t: float,
    ppe_t_minus_1: float,
    securities_t: float,
    securities_t_minus_1: float,
    total_assets_t: float,
    total_assets_t_minus_1: float,
    depreciation_t: float,
    depreciation_t_minus_1: float,
    sga_t: float,
    sga_t_minus_1: float,
    long_term_debt_t: float,
    long_term_debt_t_minus_1: float,
    current_liabilities_t: float,
    current_liabilities_t_minus_1: float,
    net_income_t: float,
    cfo_t: float
) -> Dict[str, Any]:
    """
    Calculate the 8-Variable Beneish M-Score for earnings manipulation detection.

    Formula (1999):
        M = -4.84 + 0.920*DSRI + 0.528*GMI + 0.404*AQI + 0.892*SGI 
            + 0.115*DEPI - 0.172*SGAI + 4.037*TATA + 0.0327*LVGI

    Threshold:
        M > -1.78  -> High probability of earnings manipulation (Manipulator)
        M <= -1.78 -> Low probability of earnings manipulation (Non-Manipulator)

    Scope distinction:
        Beneish M-Score evaluates aggressive accounting / earnings distortion.
        A company can manipulate earnings while having ample liquidity, or default 
        without ever manipulating earnings.
    """
    raw_inputs = {
        "sales_t": sales_t, "sales_t_minus_1": sales_t_minus_1,
        "cogs_t": cogs_t, "cogs_t_minus_1": cogs_t_minus_1,
        "receivables_t": receivables_t, "receivables_t_minus_1": receivables_t_minus_1,
        "current_assets_t": current_assets_t, "current_assets_t_minus_1": current_assets_t_minus_1,
        "ppe_t": ppe_t, "ppe_t_minus_1": ppe_t_minus_1,
        "securities_t": securities_t, "securities_t_minus_1": securities_t_minus_1,
        "total_assets_t": total_assets_t, "total_assets_t_minus_1": total_assets_t_minus_1,
        "depreciation_t": depreciation_t, "depreciation_t_minus_1": depreciation_t_minus_1,
        "sga_t": sga_t, "sga_t_minus_1": sga_t_minus_1,
        "long_term_debt_t": long_term_debt_t, "long_term_debt_t_minus_1": long_term_debt_t_minus_1,
        "current_liabilities_t": current_liabilities_t, "current_liabilities_t_minus_1": current_liabilities_t_minus_1,
        "net_income_t": net_income_t, "cfo_t": cfo_t
    }

    is_valid, missing = validate_financial_inputs(raw_inputs, list(raw_inputs.keys()))
    if not is_valid:
        return {
            "status": "INCOMPLETE_DATA",
            "score": None,
            "manipulation_flag": "UNKNOWN",
            "message": f"Cannot compute Beneish M-Score. Missing prior-period or current fields: {', '.join(missing)}",
            "indices": {}
        }

    # 1. DSRI: Days Sales in Receivables Index
    rec_to_sales_t = safe_divide(receivables_t, sales_t, default=1.0)
    rec_to_sales_t_prev = safe_divide(receivables_t_minus_1, sales_t_minus_1, default=1.0)
    dsri = safe_divide(rec_to_sales_t, rec_to_sales_t_prev, default=1.0)

    # 2. GMI: Gross Margin Index
    gm_prev = safe_divide(sales_t_minus_1 - cogs_t_minus_1, sales_t_minus_1, default=0.2)
    gm_curr = safe_divide(sales_t - cogs_t, sales_t, default=0.2)
    gmi = safe_divide(gm_prev, gm_curr, default=1.0)

    # 3. AQI: Asset Quality Index
    non_curr_t = total_assets_t - (current_assets_t + ppe_t + securities_t)
    aq_t = 1.0 - safe_divide(current_assets_t + ppe_t + securities_t, total_assets_t, default=0.0)
    aq_prev = 1.0 - safe_divide(current_assets_t_minus_1 + ppe_t_minus_1 + securities_t_minus_1, total_assets_t_minus_1, default=0.0)
    aqi = safe_divide(aq_t, aq_prev, default=1.0)

    # 4. SGI: Sales Growth Index
    sgi = safe_divide(sales_t, sales_t_minus_1, default=1.0)

    # 5. DEPI: Depreciation Index
    depr_rate_prev = safe_divide(depreciation_t_minus_1, depreciation_t_minus_1 + ppe_t_minus_1, default=0.1)
    depr_rate_t = safe_divide(depreciation_t, depreciation_t + ppe_t, default=0.1)
    depi = safe_divide(depr_rate_prev, depr_rate_t, default=1.0)

    # 6. SGAI: Sales General & Admin Expense Index
    sga_rate_t = safe_divide(sga_t, sales_t, default=0.15)
    sga_rate_prev = safe_divide(sga_t_minus_1, sales_t_minus_1, default=0.15)
    sgai = safe_divide(sga_rate_t, sga_rate_prev, default=1.0)

    # 7. LVGI: Leverage Index
    lev_t = safe_divide(long_term_debt_t + current_liabilities_t, total_assets_t, default=0.5)
    lev_prev = safe_divide(long_term_debt_t_minus_1 + current_liabilities_t_minus_1, total_assets_t_minus_1, default=0.5)
    lvgi = safe_divide(lev_t, lev_prev, default=1.0)

    # 8. TATA: Total Accruals to Total Assets
    total_accruals = net_income_t - cfo_t
    tata = safe_divide(total_accruals, total_assets_t, default=0.0)

    # Beneish M-Score Formula
    m_score = (
        -4.84
        + 0.920 * dsri
        + 0.528 * gmi
        + 0.404 * aqi
        + 0.892 * sgi
        + 0.115 * depi
        - 0.172 * sgai
        + 4.037 * tata
        + 0.0327 * lvgi
    )

    is_flagged = m_score > -1.78
    flag_label = "Likely Manipulator (High Risk)" if is_flagged else "Unlikely Manipulator (Low Risk)"

    indices = {
        "DSRI_days_sales_receivables_index": round(dsri, 3),
        "GMI_gross_margin_index": round(gmi, 3),
        "AQI_asset_quality_index": round(aqi, 3),
        "SGI_sales_growth_index": round(sgi, 3),
        "DEPI_depreciation_index": round(depi, 3),
        "SGAI_sga_expense_index": round(sgai, 3),
        "LVGI_leverage_index": round(lvgi, 3),
        "TATA_accruals_to_total_assets": round(tata, 4),
    }

    return {
        "status": "SUCCESS",
        "score": round(m_score, 3),
        "manipulation_flag": flag_label,
        "is_flagged": is_flagged,
        "threshold": -1.78,
        "message": f"Beneish M-Score is {round(m_score, 3)}. Threshold is -1.78. Assessment: {flag_label}.",
        "indices": indices
    }


# =====================================================================
# 3. PIOTROSKI F-SCORE (Fundamental Financial Health Indicator)
# =====================================================================
def calculate_piotroski_f_score(
    net_income_t: float,
    net_income_t_minus_1: float,
    cfo_t: float,
    total_assets_t: float,
    total_assets_t_minus_1: float,
    long_term_debt_t: float,
    long_term_debt_t_minus_1: float,
    current_assets_t: float,
    current_assets_t_minus_1: float,
    current_liabilities_t: float,
    current_liabilities_t_minus_1: float,
    shares_t: float,
    shares_t_minus_1: float,
    gross_margin_t: float,
    gross_margin_t_minus_1: float,
    sales_t: float,
    sales_t_minus_1: float
) -> Dict[str, Any]:
    """
    Calculate the 9-point Piotroski F-Score for fundamental financial health.

    Criteria (1 point each if true):
    Profitability:
      1. ROA_t > 0
      2. CFO_t > 0
      3. Delta ROA > 0 (ROA_t > ROA_{t-1})
      4. Accrual > 0 (CFO_t > Net_Income_t, meaning cash flow exceeds accounting profit)
    Leverage, Liquidity & Source of Funds:
      5. Delta Leverage < 0 (Long-Term Debt / Assets decreased)
      6. Delta Current Ratio > 0 (Current Ratio increased)
      7. No Equity Dilution (Shares_t <= Shares_{t-1})
    Operating Efficiency:
      8. Delta Gross Margin > 0 (Gross Margin increased)
      9. Delta Asset Turnover > 0 (Asset Turnover increased)

    Scoring:
      8 - 9: Strong fundamental health (Low Risk)
      5 - 7: Moderate fundamental health (Medium Risk)
      0 - 4: Weak fundamental health (High Risk / Vulnerable)
    """
    raw_inputs = {
        "net_income_t": net_income_t, "net_income_t_minus_1": net_income_t_minus_1,
        "cfo_t": cfo_t,
        "total_assets_t": total_assets_t, "total_assets_t_minus_1": total_assets_t_minus_1,
        "long_term_debt_t": long_term_debt_t, "long_term_debt_t_minus_1": long_term_debt_t_minus_1,
        "current_assets_t": current_assets_t, "current_assets_t_minus_1": current_assets_t_minus_1,
        "current_liabilities_t": current_liabilities_t, "current_liabilities_t_minus_1": current_liabilities_t_minus_1,
        "shares_t": shares_t, "shares_t_minus_1": shares_t_minus_1,
        "gross_margin_t": gross_margin_t, "gross_margin_t_minus_1": gross_margin_t_minus_1,
        "sales_t": sales_t, "sales_t_minus_1": sales_t_minus_1
    }

    is_valid, missing = validate_financial_inputs(raw_inputs, list(raw_inputs.keys()))
    if not is_valid:
        return {
            "status": "INCOMPLETE_DATA",
            "score": None,
            "category": "UNKNOWN",
            "message": f"Cannot compute Piotroski F-Score. Missing required fields: {', '.join(missing)}",
            "criteria_breakdown": {}
        }

    roa_t = safe_divide(net_income_t, total_assets_t)
    roa_prev = safe_divide(net_income_t_minus_1, total_assets_t_minus_1)

    # 1. Positive ROA
    f1 = 1 if roa_t > 0 else 0
    # 2. Positive CFO
    f2 = 1 if cfo_t > 0 else 0
    # 3. Delta ROA > 0
    f3 = 1 if roa_t > roa_prev else 0
    # 4. Accrual quality: CFO > Net Income
    f4 = 1 if cfo_t > net_income_t else 0

    # 5. Decreased Leverage
    lev_t = safe_divide(long_term_debt_t, total_assets_t)
    lev_prev = safe_divide(long_term_debt_t_minus_1, total_assets_t_minus_1)
    f5 = 1 if lev_t < lev_prev else 0

    # 6. Improved Liquidity (Current Ratio)
    cr_t = safe_divide(current_assets_t, current_liabilities_t)
    cr_prev = safe_divide(current_assets_t_minus_1, current_liabilities_t_minus_1)
    f6 = 1 if cr_t > cr_prev else 0

    # 7. No Dilution
    f7 = 1 if shares_t <= shares_t_minus_1 else 0

    # 8. Improved Gross Margin
    f8 = 1 if gross_margin_t > gross_margin_t_minus_1 else 0

    # 9. Improved Asset Turnover
    at_t = safe_divide(sales_t, total_assets_t)
    at_prev = safe_divide(sales_t_minus_1, total_assets_t_minus_1)
    f9 = 1 if at_t > at_prev else 0

    total_f = f1 + f2 + f3 + f4 + f5 + f6 + f7 + f8 + f9

    if total_f >= 8:
        category = "Strong Fundamental Health"
        risk_level = "Low"
    elif total_f >= 5:
        category = "Moderate Fundamental Health"
        risk_level = "Medium"
    else:
        category = "Weak Fundamental Health"
        risk_level = "High"

    breakdown = {
        "F1_positive_roa": bool(f1),
        "F2_positive_cfo": bool(f2),
        "F3_delta_roa_positive": bool(f3),
        "F4_accruals_cfo_gt_ni": bool(f4),
        "F5_leverage_reduced": bool(f5),
        "F6_current_ratio_improved": bool(f6),
        "F7_no_equity_dilution": bool(f7),
        "F8_gross_margin_improved": bool(f8),
        "F9_asset_turnover_improved": bool(f9),
    }

    return {
        "status": "SUCCESS",
        "score": total_f,
        "max_score": 9,
        "category": category,
        "risk_level": risk_level,
        "message": f"Piotroski F-Score is {total_f}/9 ({category}).",
        "criteria_breakdown": breakdown
    }
