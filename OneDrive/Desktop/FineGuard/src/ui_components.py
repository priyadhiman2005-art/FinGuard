"""
FinGuard - Institutional Fintech Design System & UI Components
==============================================================
Provides reusable styling, Plotly theme enforcement, and consistent
visual components for the FinGuard intelligence platform.
"""

import streamlit as st
import plotly.graph_objects as go

# ---------------------------------------------------------------------
# EXACT FINTECH COLOR PALETTE
# ---------------------------------------------------------------------
COLORS = {
    "main_bg": "#07111F",
    "sidebar_bg": "#0A1626",
    "card_bg": "#101F31",
    "elevated_bg": "#14263A",
    "border": "#26384B",
    "primary_teal": "#2DD4BF",
    "secondary_cyan": "#67E8F9",
    "text_primary": "#F1F5F9",
    "text_secondary": "#94A3B8",
    "risk_red": "#F87171",
    "risk_amber": "#FBBF24",
    "risk_green": "#34D399",
}

# ---------------------------------------------------------------------
# REUSABLE CSS DESIGN SYSTEM
# ---------------------------------------------------------------------
FINTECH_CSS = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    .stApp {{
        background-color: {COLORS["main_bg"]};
        color: {COLORS["text_primary"]};
    }}

    /* Tighten stream view container spacing for 16:9 laptop screens */
    header[data-testid="stHeader"] {{
        background-color: transparent !important;
        height: 0rem !important;
    }}
    #MainMenu, footer {{
        visibility: hidden !important;
    }}
    .block-container {{
        padding-top: 1.4rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {{
        background-color: {COLORS["sidebar_bg"]} !important;
        border-right: 1px solid {COLORS["border"]} !important;
        padding-top: 1rem !important;
    }}

    /* Institutional Sidebar Navigation Pills */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] > label {{
        display: none !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] {{
        display: flex;
        flex-direction: column;
        gap: 3px;
        width: 100%;
    }}
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] label {{
        display: flex !important;
        align-items: center !important;
        background-color: transparent !important;
        border: 1px solid transparent !important;
        border-left: 3px solid transparent !important;
        border-radius: 6px !important;
        padding: 7px 11px !important;
        margin: 0 !important;
        cursor: pointer !important;
        transition: all 0.15s ease-in-out !important;
        width: 100% !important;
    }}
    /* Hide default radio circle indicator */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] label > div:first-child {{
        display: none !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] label span {{
        color: {COLORS["text_secondary"]} !important;
        font-size: 0.86rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.1px !important;
        margin: 0 !important;
        transition: color 0.15s ease !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] label:hover {{
        background-color: {COLORS["elevated_bg"]} !important;
        border-color: {COLORS["border"]} !important;
        border-left: 3px solid {COLORS["secondary_cyan"]} !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] label:hover div[data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] label:hover span {{
        color: {COLORS["text_primary"]} !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {{
        background-color: rgba(45, 212, 191, 0.12) !important;
        border-color: rgba(45, 212, 191, 0.35) !important;
        border-left: 3px solid {COLORS["primary_teal"]} !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) div[data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) span {{
        color: {COLORS["primary_teal"]} !important;
        font-weight: 700 !important;
    }}

    /* Global Headings */
    h1, h2, h3, h4 {{
        color: {COLORS["text_primary"]} !important;
        font-weight: 700;
        letter-spacing: -0.3px;
    }}

    /* Page Header Banner */
    .page-header {{
        background: linear-gradient(135deg, {COLORS["card_bg"]} 0%, {COLORS["elevated_bg"]} 100%);
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
        padding: 12px 18px;
        margin-bottom: 12px;
    }}

    .page-title {{
        font-size: 1.35rem;
        font-weight: 800;
        color: {COLORS["text_primary"]};
        letter-spacing: -0.3px;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }}

    .page-subtitle {{
        font-size: 0.82rem;
        color: {COLORS["text_secondary"]};
        margin-top: 3px;
        line-height: 1.35;
    }}

    /* Section Subheaders */
    .fin-section-title {{
        font-size: 1.02rem;
        font-weight: 700;
        color: {COLORS["text_primary"]};
        margin: 14px 0 8px 0;
        letter-spacing: -0.2px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    /* Institutional KPI Card - Aligned Fixed Height */
    .fin-card {{
        background: {COLORS["card_bg"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
        padding: 13px 16px;
        margin-bottom: 6px;
        min-height: 104px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-sizing: border-box;
        transition: border-color 0.2s ease, transform 0.15s ease;
    }}
    .fin-card:hover {{
        border-color: {COLORS["primary_teal"]};
    }}

    .fin-card-label {{
        font-size: 0.70rem;
        font-weight: 600;
        color: {COLORS["text_secondary"]};
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 2px;
    }}

    .fin-card-value {{
        font-size: 1.60rem;
        font-weight: 800;
        color: {COLORS["text_primary"]};
        letter-spacing: -0.5px;
        line-height: 1.15;
        font-feature-settings: "tnum" 1;
    }}

    .fin-card-subtext {{
        font-size: 0.74rem;
        color: {COLORS["text_secondary"]};
        margin-top: 4px;
        line-height: 1.25;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    /* Risk & Status Badges */
    .badge-safe {{
        background-color: rgba(52, 211, 153, 0.12);
        color: {COLORS["risk_green"]};
        border: 1px solid rgba(52, 211, 153, 0.35);
        padding: 2px 8px;
        border-radius: 5px;
        font-size: 0.72rem;
        font-weight: 700;
        display: inline-block;
    }}

    .badge-amber {{
        background-color: rgba(251, 191, 36, 0.12);
        color: {COLORS["risk_amber"]};
        border: 1px solid rgba(251, 191, 36, 0.35);
        padding: 2px 8px;
        border-radius: 5px;
        font-size: 0.72rem;
        font-weight: 700;
        display: inline-block;
    }}

    .badge-danger {{
        background-color: rgba(248, 113, 113, 0.12);
        color: {COLORS["risk_red"]};
        border: 1px solid rgba(248, 113, 113, 0.35);
        padding: 2px 8px;
        border-radius: 5px;
        font-size: 0.72rem;
        font-weight: 700;
        display: inline-block;
    }}

    .badge-teal {{
        background-color: rgba(45, 212, 191, 0.12);
        color: {COLORS["primary_teal"]};
        border: 1px solid rgba(45, 212, 191, 0.35);
        padding: 2px 8px;
        border-radius: 5px;
        font-size: 0.72rem;
        font-weight: 700;
        display: inline-block;
    }}

    /* Compact Callout Container */
    .callout-box {{
        background-color: {COLORS["elevated_bg"]};
        border-left: 3px solid {COLORS["primary_teal"]};
        border-radius: 0 6px 6px 0;
        padding: 8px 14px;
        margin: 8px 0 12px 0;
        color: {COLORS["text_secondary"]};
        font-size: 0.81rem;
        line-height: 1.4;
    }}

    .callout-box strong {{
        color: {COLORS["text_primary"]};
    }}

    .simulation-box {{
        background-color: rgba(251, 191, 36, 0.08);
        border: 1px dashed {COLORS["risk_amber"]};
        border-radius: 6px;
        padding: 8px 14px;
        margin: 8px 0 12px 0;
        color: {COLORS["risk_amber"]};
        font-size: 0.81rem;
        font-weight: 600;
    }}

    /* Clean Empty State */
    .empty-state {{
        background-color: {COLORS["card_bg"]};
        border: 1px dashed {COLORS["border"]};
        border-radius: 8px;
        padding: 30px 20px;
        text-align: center;
        color: {COLORS["text_secondary"]};
    }}

    /* Dataframe Table Container */
    .stDataFrame {{
        border: 1px solid {COLORS["border"]};
        border-radius: 6px;
        background-color: {COLORS["card_bg"]};
    }}

    /* Streamlit Metric Overrides */
    div[data-testid="stMetric"] {{
        background-color: {COLORS["card_bg"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 6px;
        padding: 10px 14px;
    }}
    div[data-testid="stMetricLabel"] {{
        color: {COLORS["text_secondary"]} !important;
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
    }}
    div[data-testid="stMetricValue"] {{
        color: {COLORS["text_primary"]} !important;
        font-size: 1.35rem !important;
        font-weight: 700 !important;
    }}
</style>
"""


def apply_fintech_theme(
    fig: go.Figure,
    height: int = 340,
    title: str = "",
    margin: dict = None,
    show_legend: bool = None,
    **kwargs
) -> go.Figure:
    """
    Standardize Plotly figures to the FinGuard institutional dark theme.
    Guarantees sufficient margins and non-overlapping title / legend positioning.
    Accepts arbitrary Plotly layout keyword arguments (margin, show_legend, etc.)
    and applies them safely to the layout.
    """
    # Safe default margin giving headroom for titles and legends
    safe_margin = margin or dict(l=45, r=25, t=48 if title else 20, b=38)

    layout_updates = dict(
        paper_bgcolor=COLORS["card_bg"],
        plot_bgcolor=COLORS["card_bg"],
        height=height,
        margin=safe_margin,
        font=dict(color=COLORS["text_secondary"], size=11, family="Plus Jakarta Sans"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1.0,
            font=dict(color=COLORS["text_primary"], size=10),
            bgcolor="rgba(16, 31, 49, 0.70)"
        ),
        hoverlabel=dict(
            bgcolor=COLORS["elevated_bg"],
            bordercolor=COLORS["border"],
            font=dict(color=COLORS["text_primary"], family="Plus Jakarta Sans", size=11)
        ),
        xaxis=dict(
            gridcolor=COLORS["border"],
            zerolinecolor=COLORS["border"],
            showline=True,
            linecolor=COLORS["border"],
            tickfont=dict(color=COLORS["text_secondary"], size=10),
            title_font=dict(color=COLORS["text_secondary"], size=11)
        ),
        yaxis=dict(
            gridcolor=COLORS["border"],
            zerolinecolor=COLORS["border"],
            showline=True,
            linecolor=COLORS["border"],
            tickfont=dict(color=COLORS["text_secondary"], size=10),
            title_font=dict(color=COLORS["text_secondary"], size=11)
        )
    )

    if title:
        layout_updates["title"] = dict(
            text=title,
            font=dict(color=COLORS["text_primary"], size=13, family="Plus Jakarta Sans"),
            x=0.01,
            y=0.98,
            xanchor="left",
            yanchor="top"
        )

    if show_legend is not None:
        layout_updates["showlegend"] = show_legend

    if "showlegend" in kwargs:
        layout_updates["showlegend"] = kwargs.pop("showlegend")

    # Merge any extra kwargs safely
    layout_updates.update(kwargs)

    fig.update_layout(**layout_updates)
    return fig


def render_header(title: str, subtitle: str, badge_text: str = None, badge_type: str = "teal"):
    """Render consistent page header with optional contextual badge."""
    badge_html = f'<span class="badge-{badge_type}" style="margin-left:10px; vertical-align:middle;">{badge_text}</span>' if badge_text else ''
    st.markdown(
        f"""
        <div class="page-header">
            <div class="page-title">{title} {badge_html}</div>
            <div class="page-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_kpi_card(title: str, value: str, subtext: str = None, value_color: str = None, border_color: str = None):
    """Render standard institutional KPI metric card with standardized height."""
    val_style = f'color:{value_color};' if value_color else f'color:{COLORS["text_primary"]};'
    card_style = f'border-color:{border_color};' if border_color else ''
    sub_html = f'<div class="fin-card-subtext">{subtext}</div>' if subtext else ''
    st.markdown(
        f"""
        <div class="fin-card" style="{card_style}">
            <div class="fin-card-label">{title}</div>
            <div class="fin-card-value" style="{val_style}">{value}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_callout(text: str):
    """Render informational callout."""
    st.markdown(f'<div class="callout-box">{text}</div>', unsafe_allow_html=True)


def render_simulation_banner(text: str):
    """Render hypothetical scenario warning banner."""
    st.markdown(f'<div class="simulation-box">⚠️ {text}</div>', unsafe_allow_html=True)


def render_empty_state(title: str, message: str):
    """Render empty state when filters yield zero records."""
    st.markdown(
        f"""
        <div class="empty-state">
            <div style="font-size:1.05rem; font-weight:700; color:{COLORS['text_primary']}; margin-bottom:4px;">{title}</div>
            <div style="font-size:0.83rem;">{message}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
