"""
Unit tests for FinGuard UI Components & Design System
"""

import plotly.graph_objects as go
import pytest
from src.ui_components import COLORS, apply_fintech_theme


def test_colors_palette_integrity():
    assert COLORS["main_bg"] == "#07111F"
    assert COLORS["sidebar_bg"] == "#0A1626"
    assert COLORS["card_bg"] == "#101F31"
    assert COLORS["primary_teal"] == "#2DD4BF"
    assert COLORS["risk_red"] == "#F87171"
    assert COLORS["risk_amber"] == "#FBBF24"
    assert COLORS["risk_green"] == "#34D399"


def test_apply_fintech_theme():
    fig = go.Figure()
    fig.add_trace(go.Bar(x=["A", "B"], y=[10, 20]))
    themed_fig = apply_fintech_theme(fig, height=300, title="Test Chart")

    assert themed_fig.layout.paper_bgcolor == COLORS["card_bg"]
    assert themed_fig.layout.plot_bgcolor == COLORS["card_bg"]
    assert themed_fig.layout.height == 300

