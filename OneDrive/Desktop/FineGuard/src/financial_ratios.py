"""
FinGuard - Financial Ratios & Helper Utilities
==============================================
Provides safe mathematical helpers, accounting ratio calculators,
and input validation routines for corporate financial statements.
"""

from typing import Tuple, List, Dict, Any, Optional
import math
import numpy as np


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning a default value if denominator is 
    zero, NaN, infinite, or if numerator is invalid.
    """
    try:
        if denominator is None or numerator is None:
            return default
        num = float(numerator)
        den = float(denominator)
        if math.isnan(num) or math.isnan(den) or math.isinf(num) or math.isinf(den):
            return default
        if abs(den) < 1e-12:
            return default
        res = num / den
        return default if math.isnan(res) or math.isinf(res) else res
    except (ZeroDivisionError, OverflowError, ValueError, TypeError):
        return default


def validate_financial_inputs(data: Dict[str, Any], required_fields: list) -> Tuple[bool, list]:
    """
    Validate that all required financial fields exist, are numeric, and non-null.
    Returns (is_valid, missing_or_invalid_fields).
    """
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)
            continue
        try:
            val = float(data[field])
            if math.isnan(val) or math.isinf(val):
                missing_fields.append(field)
        except (ValueError, TypeError):
            missing_fields.append(field)

    return (len(missing_fields) == 0, missing_fields)
