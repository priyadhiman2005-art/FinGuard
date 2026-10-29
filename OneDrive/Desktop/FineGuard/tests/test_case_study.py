"""
Unit tests for FinGuard Indian Corporate Distress Case Study Module
"""

import os
import pandas as pd
import pytest
from src.case_study import (
    load_distress_metadata,
    evaluate_indian_distress_cases,
    generate_data_collection_template,
    RESULTS_CSV_PATH,
    COLLECTION_TEMPLATE_PATH
)


def test_metadata_completeness():
    metadata = load_distress_metadata()
    cases = metadata["distressed_companies"]
    assert len(cases) == 10, "Must contain exactly 10 distressed entities."

    for c in cases:
        assert "id" in c
        assert "company_name" in c
        assert "event_date" in c
        assert len(c["pre_event_years"]) == 3, "Must specify 3 pre-event years."
        assert len(c["matched_peers"]) == 3, "Must specify 3 sector-matched peers."
        assert len(c["public_sources"]) >= 1, "Must cite verifiable public sources."


def test_distress_evaluation_execution():
    df = evaluate_indian_distress_cases()
    assert os.path.exists(RESULTS_CSV_PATH)
    assert len(df) == 10
    assert "Altman Z-Score" in df.columns
    assert "Risk Zone" in df.columns

    # Verify all evaluated cases fall in Distress Zone based on authentic pre-event filings
    distress_count = (df["Risk Zone"] == "Distress Zone").sum()
    assert distress_count == 10, "All 10 distressed Indian companies should be detected in Distress Zone pre-event."


def test_data_collection_template_structure():
    tmpl_df = generate_data_collection_template()
    assert os.path.exists(COLLECTION_TEMPLATE_PATH)
    # 10 distressed targets * 3 years = 30 rows
    # 30 matched peers * 3 years = 90 rows
    # Total = 120 filing slots
    assert len(tmpl_df) == 120
    expected_cols = [
        "Company_ID", "Company_Name", "Role", "Sector", "Matched_To",
        "Fiscal_Year", "Total_Assets", "Total_Liabilities", "Net_Worth",
        "Working_Capital", "Retained_Earnings", "EBIT", "Sales"
    ]
    for col in expected_cols:
        assert col in tmpl_df.columns

