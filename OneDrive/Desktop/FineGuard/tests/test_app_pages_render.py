"""
Integration tests verifying all 7 pages of app.py render without exceptions or TypeErrors.
"""

import os
from streamlit.testing.v1 import AppTest

APP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app.py"))


def test_all_seven_pages_render_without_exceptions():
    """Verify that all 7 navigation destinations in FinGuard render without runtime exceptions."""
    pages = [
        "Executive Overview",
        "Risk Explorer",
        "Company Analysis",
        "Fraud Indicators",
        "Scenario Lab",
        "Model Performance",
        "Data & Methodology"
    ]

    at = AppTest.from_file(APP_PATH, default_timeout=35).run()
    assert len(at.exception) == 0, f"Executive Overview threw exceptions: {[e.value for e in at.exception]}"

    for page_name in pages[1:]:
        nav_radio = at.sidebar.radio[0]
        nav_radio.set_value(page_name).run()
        assert len(at.exception) == 0, f"Page '{page_name}' threw exceptions: {[e.value for e in at.exception]}"
