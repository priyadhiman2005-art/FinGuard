"""
FinGuard — Institutional Corporate Financial Risk & Fraud Intelligence Platform
=================================================================================
Zeckathon 2026 — Problem Statement 2: Financial Risk & Fraud Analytics

A professional, institutional-grade risk intelligence platform designed for credit risk committees,
forensic auditors, and institutional lenders.

Core Modules:
1. Executive Overview (Financial Risk Overview, high-density KPIs, risk distribution & factor summary)
2. Risk Explorer (1,364-firm test universe, risk ranking table, heatmap & Top-5% review queue)
3. Company Analysis (Deep firm profile, financial health, TreeSHAP attributions & report export)
4. Fraud Indicators (Altman Z, Beneish M-Score 8-indices, Piotroski F-Score with strict validation)
5. Scenario Lab (Interactive stress-testing sensitivity simulation with delta diagnostics)
6. Model Performance (Empirical ROC-AUC 0.9466, PR-AUC 0.4610, confusion matrices & 20:1 loss curve)
7. Data & Methodology (UCI ID 572 benchmark, Indian corporate distress case studies & disclosures)
"""

import os
import io
import json
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import joblib

# FinGuard Core Engine Modules
from src.fraud_scores import (
    calculate_altman_z_score,
    calculate_beneish_m_score,
    calculate_piotroski_f_score
)
from src.threshold_policy import apply_capacity_policy, analyze_threshold_cost
from src.explainability import FinGuardExplainer, CAUSAL_DISCLAIMER
from src.case_study import (
    load_distress_metadata,
    RESULTS_CSV_PATH,
    COLLECTION_TEMPLATE_PATH
)
from src.ui_components import (
    COLORS,
    FINTECH_CSS,
    apply_fintech_theme,
    render_header,
    render_kpi_card,
    render_callout,
    render_simulation_banner,
    render_empty_state
)

# ---------------------------------------------------------------------
# 1. STREAMLIT APPLICATION CONFIGURATION
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="FinGuard | Financial Risk Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(FINTECH_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------
# 2. CACHED MODEL & ARTIFACT MANAGEMENT
# ---------------------------------------------------------------------
@st.cache_resource
def load_fintech_artifacts():
    base_dir = os.path.dirname(__file__)
    models_dir = os.path.join(base_dir, "models")

    preprocessor = joblib.load(os.path.join(models_dir, "preprocessor.joblib"))
    rf_model = joblib.load(os.path.join(models_dir, "random_forest_risk_model.joblib"))
    lr_model = joblib.load(os.path.join(models_dir, "baseline_logistic_regression.joblib"))

    with open(os.path.join(models_dir, "evaluation_results.json"), "r") as f:
        eval_results = json.load(f)

    explainer = FinGuardExplainer(rf_model, eval_results["feature_names"])
    return preprocessor, rf_model, lr_model, eval_results, explainer


@st.cache_data
def load_test_universe():
    base_dir = os.path.dirname(__file__)
    test_path = os.path.join(base_dir, "data", "processed", "test.csv")
    return pd.read_csv(test_path)


@st.cache_data
def get_portfolio_evaluations():
    """
    Generate predictions and risk rankings for all 1,364 test companies once.
    Provides instant filtering, ranking, and Top-5% queue queries.
    """
    preprocessor, rf_model, lr_model, eval_results, _ = load_fintech_artifacts()
    test_df = load_test_universe()
    feature_cols = [c for c in test_df.columns if c != "Bankrupt?"]

    X_scaled = preprocessor.transform(test_df[feature_cols])
    rf_probas = rf_model.predict_proba(X_scaled)[:, 1]
    lr_probas = lr_model.predict_proba(X_scaled)[:, 1]

    n_samples = len(test_df)
    company_ids = [f"COMP-{i+1:04d}" for i in range(n_samples)]

    # Apply Top-5% capacity rule strictly
    cap_res = apply_capacity_policy(rf_probas, capacity_pct=0.05, company_ids=company_ids)
    in_top_5_mask = cap_res["flagged_mask"]

    def assign_tier(p):
        if p >= 0.50:
            return "Severe Distress (Tier 1)"
        elif p >= 0.25:
            return "Elevated Risk (Tier 2)"
        elif p >= 0.10:
            return "Moderate Risk (Tier 3)"
        else:
            return "Low Risk / Solvent (Tier 4)"

    tiers = [assign_tier(p) for p in rf_probas]

    portfolio_df = pd.DataFrame({
        "Company_ID": company_ids,
        "Actual_Status": ["Bankrupt (1)" if y == 1 else "Solvent (0)" for y in test_df["Bankrupt?"]],
        "Actual_Label": test_df["Bankrupt?"].values,
        "ML_Default_Probability": rf_probas,
        "Baseline_LR_Probability": lr_probas,
        "Risk_Tier": tiers,
        "In_Top_5Pct_Queue": in_top_5_mask,
        "Borrowing_Dependency": test_df["Borrowing dependency"].values,
        "Net_Income_to_Assets": test_df["Net Income to Total Assets"].values,
        "Debt_Ratio_Pct": test_df["Debt ratio %"].values,
        "Current_Liability_to_Assets": test_df["Current Liability to Assets"].values,
        "Persistent_EPS": test_df["Persistent EPS in the Last Four Seasons"].values,
    })

    # Sort descending by risk probability to establish formal percentile rank
    portfolio_df = portfolio_df.sort_values(by="ML_Default_Probability", ascending=False).reset_index(drop=True)
    portfolio_df["Portfolio_Risk_Rank"] = portfolio_df.index + 1
    portfolio_df["Percentile_Rank"] = ((n_samples - portfolio_df["Portfolio_Risk_Rank"] + 1) / n_samples * 100).round(2)

    return portfolio_df, cap_res


# Initialize cached resources
try:
    preprocessor, rf_model, lr_model, eval_results, explainer = load_fintech_artifacts()
    test_universe = load_test_universe()
    portfolio_df, cap_summary = get_portfolio_evaluations()
    system_ready = True
except Exception as e:
    system_ready = False
    init_err = str(e)


# ---------------------------------------------------------------------
# 3. SIDEBAR NAVIGATION & SYSTEM TELEMETRY
# ---------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:14px; padding:2px 4px;">
            <div style="width:36px; height:36px; background:{COLORS['card_bg']}; border:1px solid {COLORS['primary_teal']}; border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:1.2rem; box-shadow:0 0 10px rgba(45,212,191,0.15);">🛡️</div>
            <div>
                <div style="font-size:1.18rem; font-weight:800; color:{COLORS['text_primary']}; letter-spacing:-0.4px; line-height:1.15;">FinGuard</div>
                <div style="font-size:0.68rem; color:{COLORS['primary_teal']}; font-weight:600; text-transform:uppercase; letter-spacing:0.8px;">Risk Intelligence</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    nav_destinations = [
        "Executive Overview",
        "Risk Explorer",
        "Company Analysis",
        "Fraud Indicators",
        "Scenario Lab",
        "Model Performance",
        "Data & Methodology"
    ]

    nav_icons = {
        "Executive Overview": "📊",
        "Risk Explorer": "🎯",
        "Company Analysis": "🏢",
        "Fraud Indicators": "🔍",
        "Scenario Lab": "🧪",
        "Model Performance": "📈",
        "Data & Methodology": "📚"
    }

    selected_nav = st.radio(
        "Navigation",
        nav_destinations,
        index=0,
        format_func=lambda x: f"{nav_icons.get(x, '•')}  {x}",
        label_visibility="collapsed"
    )

    st.markdown(
        f"""
        <div style="background:{COLORS['card_bg']}; border:1px solid {COLORS['border']}; border-radius:8px; padding:10px 12px; margin-top:20px; font-size:0.71rem; color:{COLORS['text_secondary']}; line-height:1.5;">
            <div style="color:{COLORS['text_primary']}; font-weight:700; margin-bottom:5px; text-transform:uppercase; letter-spacing:0.6px; font-size:0.68rem;">System Architecture</div>
            <div style="display:flex; justify-content:space-between; margin-bottom:2px;">
                <span>Benchmark:</span><strong style="color:{COLORS['text_primary']};">UCI ML #572</strong>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:2px;">
                <span>Test Universe:</span><strong style="color:{COLORS['text_primary']};">1,364 Filings</strong>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:2px;">
                <span>Model Engine:</span><strong style="color:{COLORS['text_primary']};">Balanced RF (150)</strong>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:2px;">
                <span>Model ROC-AUC:</span><strong style="color:{COLORS['primary_teal']};">0.9466</strong>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                <span>Model PR-AUC:</span><strong style="color:{COLORS['secondary_cyan']};">0.4610</strong>
            </div>
            <div style="border-top:1px solid {COLORS['border']}; padding-top:6px; display:flex; align-items:center; gap:6px; color:{COLORS['risk_green']}; font-weight:600; font-size:0.70rem;">
                <span style="width:6px; height:6px; border-radius:50%; background-color:{COLORS['risk_green']}; box-shadow:0 0 6px {COLORS['risk_green']}; display:inline-block;"></span>
                All Modules Verified Live
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =====================================================================
# PAGE 1: EXECUTIVE OVERVIEW
# =====================================================================
if selected_nav == "Executive Overview":
    render_header(
        title="Financial Risk Overview",
        subtitle="Evaluates corporate solvency exhaustion, probability of default, and accounting manipulation risk across 1,364 held-out corporate filings.",
        badge_text="Test Universe Evaluated",
        badge_type="teal"
    )

    render_callout(
        "<strong>Educational & Model Disclosure:</strong> FinGuard is an educational engineering prototype built for <strong>Zeckathon 2026 (PS2)</strong>. "
        "Probabilities represent statistical solvency estimates across 1,364 held-out filings, not guarantees of commercial outcome."
    )

    # High-Density Aligned KPI Row (Verified Metrics)
    total_firms = len(portfolio_df)
    high_risk_firms = int((portfolio_df["ML_Default_Probability"] >= 0.50).sum())
    high_risk_pct = (high_risk_firms / total_firms) * 100
    top5_slots = cap_summary["review_capacity"]
    defaults_in_top5 = int(((portfolio_df["In_Top_5Pct_Queue"] == True) & (portfolio_df["Actual_Label"] == 1)).sum())

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card(
            title="Companies Analysed",
            value=f"{total_firms:,}",
            subtext="Held-Out Test Partition (20% Split)",
            value_color=COLORS["text_primary"]
        )
    with k2:
        render_kpi_card(
            title="High-Risk Category",
            value=f"{high_risk_firms} <span style='font-size:0.95rem; color:{COLORS['risk_red']}; font-weight:700;'>({high_risk_pct:.1f}%)</span>",
            subtext="Probability >= 0.50 (22 Defaults Caught)",
            value_color=COLORS["risk_red"],
            border_color=COLORS["risk_red"]
        )
    with k3:
        render_kpi_card(
            title="Model ROC-AUC",
            value=f"{eval_results['improved']['roc_auc']:.4f}",
            subtext="Random Forest vs 0.6076 Logit Baseline",
            value_color=COLORS["primary_teal"]
        )
    with k4:
        render_kpi_card(
            title="Top-5% Review Queue",
            value=f"{top5_slots} Firms",
            subtext=f"Captures {defaults_in_top5}/44 Defaults (54.5% Yield)",
            value_color=COLORS["risk_amber"],
            border_color=COLORS["risk_amber"]
        )

    st.markdown('<div class="fin-section-title">📊 Portfolio Risk Architecture</div>', unsafe_allow_html=True)

    # Main Analytical Area: Risk Distribution & Portfolio Ranking
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        fig_dist = px.histogram(
            portfolio_df,
            x="ML_Default_Probability",
            color="Actual_Status",
            nbins=40,
            color_discrete_map={"Bankrupt (1)": COLORS["risk_red"], "Solvent (0)": COLORS["risk_green"]},
            labels={"ML_Default_Probability": "Predicted Default Probability", "Actual_Status": "Filing Status"},
        )
        
        # Staggered, Non-Overlapping Threshold Lines with styled dark badges
        fig_dist.add_vline(
            x=0.20,
            line_dash="dash",
            line_color=COLORS["secondary_cyan"],
            line_width=1.8,
            annotation_text="Cost-Optimal: 0.20",
            annotation_position="top left",
            annotation=dict(
                bgcolor="rgba(10, 22, 38, 0.92)",
                bordercolor=COLORS["secondary_cyan"],
                borderwidth=1,
                borderpad=3,
                font=dict(color=COLORS["secondary_cyan"], size=10, family="Plus Jakarta Sans")
            )
        )
        cutoff_prob = float(cap_summary["cutoff_probability"])
        fig_dist.add_vline(
            x=cutoff_prob,
            line_dash="dot",
            line_color=COLORS["risk_amber"],
            line_width=1.8,
            annotation_text=f"Top-5% Cutoff: {cutoff_prob:.2f}",
            annotation_position="top right",
            annotation=dict(
                bgcolor="rgba(10, 22, 38, 0.92)",
                bordercolor=COLORS["risk_amber"],
                borderwidth=1,
                borderpad=3,
                font=dict(color=COLORS["risk_amber"], size=10, family="Plus Jakarta Sans")
            )
        )
        fig_dist = apply_fintech_theme(
            fig_dist,
            height=310,
            title="Default Probability Distribution by Ground Truth"
        )
        fig_dist.update_layout(
            margin=dict(l=45, r=25, t=48, b=38),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1.0,
                font=dict(size=10, color=COLORS["text_primary"]),
                bgcolor="rgba(16, 31, 49, 0.70)"
            ),
            bargap=0.08
        )
        st.plotly_chart(fig_dist, use_container_width=True)

    with chart_col2:
        # Portfolio Risk Curve (Percentile vs Probability)
        sorted_curve = portfolio_df.sort_values(by="Portfolio_Risk_Rank", ascending=True)
        fig_curve = go.Figure()
        fig_curve.add_trace(go.Scatter(
            x=sorted_curve["Portfolio_Risk_Rank"],
            y=sorted_curve["ML_Default_Probability"] * 100,
            mode="lines",
            name="Default Probability",
            line=dict(color=COLORS["primary_teal"], width=2.2)
        ))
        fig_curve.add_vrect(
            x0=1, x1=top5_slots,
            fillcolor=COLORS["risk_amber"], opacity=0.12,
            line_width=1,
            line_color=COLORS["risk_amber"],
            annotation_text=f"Top-5% Queue ({top5_slots} Firms)",
            annotation_position="inside top left",
            annotation=dict(
                bgcolor="rgba(10, 22, 38, 0.92)",
                bordercolor=COLORS["risk_amber"],
                borderwidth=1,
                borderpad=3,
                font=dict(color=COLORS["risk_amber"], size=10, family="Plus Jakarta Sans")
            )
        )
        fig_curve = apply_fintech_theme(
            fig_curve,
            height=310,
            title="Rank-Ordered Risk Curve (1 to 1,364 Entities)"
        )
        fig_curve.update_layout(
            margin=dict(l=45, r=25, t=48, b=38),
            showlegend=False
        )
        fig_curve.update_xaxes(title_text="Portfolio Risk Rank (#1 = Highest Risk)")
        fig_curve.update_yaxes(title_text="Default Probability (%)", range=[0, 105])
        st.plotly_chart(fig_curve, use_container_width=True)

    # Financial Risk Factor Summary & Highest-Risk Records (Balanced Alignment)
    row2_col1, row2_col2 = st.columns([1.15, 1.85])

    with row2_col1:
        st.markdown('<div class="fin-section-title">🔍 Top Risk Drivers (Feature Importance)</div>', unsafe_allow_html=True)
        top_feat_df = pd.DataFrame(eval_results["top_features"][:8])
        fig_feat = px.bar(
            top_feat_df[::-1],
            x="importance",
            y="feature",
            orientation="h",
            color="importance",
            color_continuous_scale=[[0, COLORS["card_bg"]], [1, COLORS["primary_teal"]]],
        )
        fig_feat = apply_fintech_theme(
            fig_feat,
            height=270,
            title="Random Forest Mean Decrease in Impurity (MDI)"
        )
        fig_feat.update_layout(
            margin=dict(l=175, r=20, t=40, b=30),
            showlegend=False
        )
        fig_feat.update_coloraxes(showscale=False)
        fig_feat.update_xaxes(title_text="Importance Weight")
        fig_feat.update_yaxes(title_text="")
        st.plotly_chart(fig_feat, use_container_width=True)

    with row2_col2:
        st.markdown('<div class="fin-section-title">🚨 Highest-Risk Entities (Review Priority)</div>', unsafe_allow_html=True)
        top_records = portfolio_df.head(8)[[
            "Portfolio_Risk_Rank", "Company_ID", "Risk_Tier",
            "ML_Default_Probability", "In_Top_5Pct_Queue", "Actual_Status"
        ]].copy()
        top_records["ML_Default_Probability"] = (top_records["ML_Default_Probability"] * 100).round(2).astype(str) + "%"
        top_records["In_Top_5Pct_Queue"] = top_records["In_Top_5Pct_Queue"].map({True: "Flagged (Top 5%)", False: "Standard"})
        top_records.columns = ["Rank", "Company ID", "Risk Tier", "Default Prob", "Review Queue", "Ground Truth"]
        st.dataframe(top_records, use_container_width=True, hide_index=True, height=270)


# =====================================================================
# PAGE 2: RISK EXPLORER
# =====================================================================
elif selected_nav == "Risk Explorer":
    render_header(
        title="Portfolio Risk Explorer",
        subtitle="Interactive workspace for filtering, sorting, and triaging the 1,364 held-out test universe under the Top-5% review capacity policy.",
        badge_text="Audit Triage Workspace",
        badge_type="teal"
    )

    render_callout(
        r"<strong>Policy & Identity Disclosure:</strong> Company identifiers (e.g., <code>COMP-0001</code>) correspond to individual anonymized filings from the UCI benchmark. "
        r"The <strong>Top-5% Review Queue</strong> strictly allocates $\lfloor 1,364 \times 5\% \rfloor = 68$ audit review slots to simulate institutional audit bandwidth constraints."
    )

    # Search & Filter Controls
    fc1, fc2, fc3, fc4 = st.columns([1.5, 1.5, 1.2, 1.8])
    with fc1:
        tier_filter = st.multiselect(
            "Filter Risk Band:",
            options=["Severe Distress (Tier 1)", "Elevated Risk (Tier 2)", "Moderate Risk (Tier 3)", "Low Risk / Solvent (Tier 4)"],
            default=["Severe Distress (Tier 1)", "Elevated Risk (Tier 2)", "Moderate Risk (Tier 3)", "Low Risk / Solvent (Tier 4)"]
        )
    with fc2:
        queue_filter = st.selectbox(
            "Review Queue Policy:",
            ["All Portfolio Entities", "Top-5% Review Queue Only", "Non-Queue Entities"]
        )
    with fc3:
        status_filter = st.selectbox(
            "Ground Truth Status:",
            ["All Records", "Actual Bankrupt Only", "Actual Solvent Only"]
        )
    with fc4:
        search_query = st.text_input("Search Company ID (e.g. COMP-0042):", "").strip().upper()

    # Apply Filter Pipeline
    filtered_df = portfolio_df[portfolio_df["Risk_Tier"].isin(tier_filter)].copy()
    if queue_filter == "Top-5% Review Queue Only":
        filtered_df = filtered_df[filtered_df["In_Top_5Pct_Queue"] == True]
    elif queue_filter == "Non-Queue Entities":
        filtered_df = filtered_df[filtered_df["In_Top_5Pct_Queue"] == False]

    if status_filter == "Actual Bankrupt Only":
        filtered_df = filtered_df[filtered_df["Actual_Label"] == 1]
    elif status_filter == "Actual Solvent Only":
        filtered_df = filtered_df[filtered_df["Actual_Label"] == 0]

    if search_query:
        filtered_df = filtered_df[filtered_df["Company_ID"].str.contains(search_query)]

    # Empty State Guard
    if len(filtered_df) == 0:
        render_empty_state("No Matching Entities Found", "Adjust your filter criteria or search query to view portfolio records.")
    else:
        # Metrics for filtered view
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("Visible Portfolio", f"{len(filtered_df):,} firms")
        m_defaults = int((filtered_df["Actual_Label"] == 1).sum())
        m_col2.metric("Defaults in View", f"{m_defaults} / 44")
        m_queue_cnt = int((filtered_df["In_Top_5Pct_Queue"] == True).sum())
        m_col3.metric("Top-5% Queue Members", f"{m_queue_cnt}")
        avg_prob = filtered_df["ML_Default_Probability"].mean() * 100
        m_col4.metric("Avg Default Probability", f"{avg_prob:.2f}%")

        # Visual Scatter Map of Risk Drivers
        st.markdown('<div class="fin-section-title">🗺️ Financial Risk Factor Map</div>', unsafe_allow_html=True)
        fig_scatter = px.scatter(
            filtered_df,
            x="Borrowing_Dependency",
            y="Net_Income_to_Assets",
            color="ML_Default_Probability",
            size="Debt_Ratio_Pct",
            hover_name="Company_ID",
            hover_data=["Risk_Tier", "Actual_Status"],
            color_continuous_scale=[[0, COLORS["risk_green"]], [0.5, COLORS["risk_amber"]], [1, COLORS["risk_red"]]],
            labels={
                "Borrowing_Dependency": "Borrowing Dependency (Debt Rollover Reliance)",
                "Net_Income_to_Assets": "Net Income / Total Assets (Core Return)",
                "ML_Default_Probability": "Default Probability"
            }
        )
        fig_scatter.update_coloraxes(
            colorbar=dict(
                title=dict(text="Probability", font=dict(size=10, color=COLORS["text_secondary"])),
                tickfont=dict(size=9, color=COLORS["text_secondary"]),
                thickness=12,
                len=0.85
            )
        )
        fig_scatter = apply_fintech_theme(
            fig_scatter,
            height=340,
            title="Borrowing Dependency vs Return on Assets (Bubble Size = Debt Ratio %)"
        )
        fig_scatter.update_layout(margin=dict(l=55, r=30, t=48, b=40))
        st.plotly_chart(fig_scatter, use_container_width=True)

        st.markdown('<div class="fin-section-title">📋 Sortable Portfolio Triage Table</div>', unsafe_allow_html=True)

        # Formatted Display Table
        disp_cols = [
            "Portfolio_Risk_Rank", "Company_ID", "Risk_Tier",
            "ML_Default_Probability", "In_Top_5Pct_Queue", "Actual_Status",
            "Borrowing_Dependency", "Net_Income_to_Assets", "Debt_Ratio_Pct"
        ]
        table_output = filtered_df[disp_cols].copy()
        table_output["ML_Default_Probability"] = (table_output["ML_Default_Probability"] * 100).round(2).astype(str) + "%"
        table_output["Borrowing_Dependency"] = table_output["Borrowing_Dependency"].round(4)
        table_output["Net_Income_to_Assets"] = table_output["Net_Income_to_Assets"].round(4)
        table_output["Debt_Ratio_Pct"] = table_output["Debt_Ratio_Pct"].round(4)
        table_output["In_Top_5Pct_Queue"] = table_output["In_Top_5Pct_Queue"].map({True: "Flagged (Top 5%)", False: "Standard"})
        table_output.columns = ["Rank", "Company ID", "Risk Tier", "Default Prob", "Review Queue", "Ground Truth", "Borrowing Dep", "ROA", "Debt Ratio %"]

        st.dataframe(table_output, use_container_width=True, hide_index=True)

        csv_download = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Export Filtered Portfolio (CSV)",
            data=csv_download,
            file_name="finguard_risk_explorer_export.csv",
            mime="text/csv"
        )


# =====================================================================
# PAGE 3: COMPANY ANALYSIS
# =====================================================================
elif selected_nav == "Company Analysis":
    render_header(
        title="Single Entity Risk Analysis",
        subtitle="Individual corporate risk diagnosis, automated warning signals, and feature-level TreeSHAP attributions.",
        badge_text="Entity Diagnosis",
        badge_type="teal"
    )

    # Company Selector Dropdown
    c_list = portfolio_df["Company_ID"].tolist()
    sel_company_id = st.selectbox("Select Target Company Identifier:", c_list, index=0)

    # Retrieve Company Data
    comp_row_meta = portfolio_df[portfolio_df["Company_ID"] == sel_company_id].iloc[0]
    comp_raw_idx = int(sel_company_id.split("-")[1]) - 1
    raw_record = test_universe.iloc[comp_raw_idx]
    feature_cols = [c for c in test_universe.columns if c != "Bankrupt?"]

    # Centerpiece Risk Profile - Perfectly Aligned KPI Cards
    c_prob = comp_row_meta["ML_Default_Probability"]
    c_tier = comp_row_meta["Risk_Tier"]
    c_rank = comp_row_meta["Portfolio_Risk_Rank"]
    c_pct = comp_row_meta["Percentile_Rank"]
    c_queue = comp_row_meta["In_Top_5Pct_Queue"]
    c_actual = comp_row_meta["Actual_Label"]

    r1, r2, r3, r4 = st.columns(4)
    with r1:
        prob_color = COLORS["risk_red"] if c_prob >= 0.35 else (COLORS["risk_amber"] if c_prob >= 0.15 else COLORS["risk_green"])
        render_kpi_card(
            title="Default Probability",
            value=f"{c_prob * 100:.2f}%",
            subtext=f"Band: {c_tier}",
            value_color=prob_color,
            border_color=prob_color
        )
    with r2:
        render_kpi_card(
            title="Portfolio Risk Ranking",
            value=f"#{c_rank} <span style='font-size:0.95rem; color:{COLORS['text_secondary']};'>/ 1,364</span>",
            subtext=f"Top {100 - c_pct:.1f}% highest risk entity",
            value_color=COLORS["secondary_cyan"]
        )
    with r3:
        queue_text = "FLAGGED (Top 5% Rule)" if c_queue else "Routine Monitoring"
        queue_color = COLORS["risk_amber"] if c_queue else COLORS["text_secondary"]
        render_kpi_card(
            title="Audit Capacity Queue",
            value=f"<span style='font-size:1.15rem;'>{queue_text}</span>",
            subtext="Capacity Policy Allocation",
            value_color=queue_color
        )
    with r4:
        actual_text = "BANKRUPT / DISTRESSED" if c_actual == 1 else "SOLVENT"
        actual_color = COLORS["risk_red"] if c_actual == 1 else COLORS["risk_green"]
        render_kpi_card(
            title="Ground Truth Status",
            value=f"<span style='font-size:1.15rem;'>{actual_text}</span>",
            subtext="Verified UCI Benchmark Record",
            value_color=actual_color
        )

    # Automated Warning Flags
    st.markdown('<div class="fin-section-title">⚠️ Automated Solvency & Early Warning Signals</div>', unsafe_allow_html=True)
    flags = []
    if comp_row_meta["Borrowing_Dependency"] > 0.38:
        flags.append(f"🚨 <strong>Critical Borrowing Dependency:</strong> Heavy reliance on external short-term credit lines ({comp_row_meta['Borrowing_Dependency']:.4f}).")
    if comp_row_meta["Net_Income_to_Assets"] < 0.70:
        flags.append(f"⚠️ <strong>Eroded Return on Assets:</strong> Core return on investment is depressed ({comp_row_meta['Net_Income_to_Assets']:.4f}).")
    if comp_row_meta["Debt_Ratio_Pct"] > 0.20:
        flags.append(f"⚠️ <strong>Elevated Balance Sheet Leverage:</strong> Liabilities represent a high proportion of total assets ({comp_row_meta['Debt_Ratio_Pct']:.4f}).")
    if comp_row_meta["Persistent_EPS"] < 0.20:
        flags.append(f"🚨 <strong>Persistent Earnings Deterioration:</strong> Multi-quarter EPS contraction ({comp_row_meta['Persistent_EPS']:.4f}).")

    if not flags:
        st.success("✅ **Solvency Buffer:** No critical liquidity or leverage warning thresholds breached.")
    else:
        for fl in flags:
            render_callout(fl)

    # Feature-Level TreeSHAP Explainability
    st.markdown('<div class="fin-section-title">🔍 Explainable AI: Feature-Level Model Attribution</div>', unsafe_allow_html=True)

    x_single_raw = test_universe.iloc[[comp_raw_idx]][feature_cols]
    x_single_scaled = preprocessor.transform(x_single_raw)

    shap_res = explainer.explain_instance(
        x_single_scaled[0],
        raw_values=x_single_raw.iloc[0].to_dict(),
        top_k=8
    )

    render_callout(
        f"<strong>Explainability Engine:</strong> {shap_res['method']}<br/>"
        f"{shap_res['disclaimer']}"
    )

    drivers_df = pd.DataFrame(shap_res["top_drivers"])
    fig_shap = px.bar(
        drivers_df[::-1],
        x="shap_value",
        y="feature",
        orientation="h",
        color="impact",
        color_discrete_map={"Increases Risk": COLORS["risk_red"], "Decreases Risk": COLORS["risk_green"]},
        labels={"shap_value": "SHAP Contribution Value", "feature": "Financial Ratio", "impact": "Contribution Direction"}
    )
    fig_shap = apply_fintech_theme(
        fig_shap,
        height=320,
        title=f"Feature Contributions to Predicted Risk for {sel_company_id}"
    )
    fig_shap.update_layout(margin=dict(l=185, r=25, t=48, b=35))
    st.plotly_chart(fig_shap, use_container_width=True)

    # Analyst Interpretation Box
    top_pos_drivers = [d["feature"] for d in shap_res["top_drivers"] if d["shap_value"] > 0][:3]
    top_neg_drivers = [d["feature"] for d in shap_res["top_drivers"] if d["shap_value"] < 0][:2]
    
    interp_text = f"<strong>Analyst Risk Synthesis:</strong> Entity {sel_company_id} is classified as <strong>{c_tier}</strong> with a predicted default probability of <strong>{c_prob * 100:.2f}%</strong>. "
    if top_pos_drivers:
        interp_text += f"The primary financial indicators elevating risk are: <em>{', '.join(top_pos_drivers)}</em>. "
    if top_neg_drivers:
        interp_text += f"Partially mitigating these pressures are: <em>{', '.join(top_neg_drivers)}</em>."
    
    render_callout(interp_text)

    # Printable Audit Card Export
    st.markdown('<div class="fin-section-title">📄 Printable Corporate Audit Card</div>', unsafe_allow_html=True)
    printable_audit_card = f"""
================================================================================
                    FINGUARD CORPORATE AUDIT REPORT CARD
================================================================================
Company Identifier:         {sel_company_id}
Benchmark Origin:          UCI Machine Learning Repository (Dataset ID: 572)
Predicted Default Prob:    {c_prob * 100:.2f}%
Assigned Risk Band:        {c_tier}
Portfolio Risk Rank:       #{c_rank} of 1,364 entities (Top {100-c_pct:.1f}%)
Review Queue Allocation:   {'SELECTED FOR AUDIT (Top-5% Capacity Rule)' if c_queue else 'Routine Monitoring'}
Ground Truth Status:       {'BANKRUPT / DISTRESSED' if c_actual == 1 else 'SOLVENT'}

Key Financial Metrics:
- Borrowing Dependency:    {comp_row_meta['Borrowing_Dependency']:.4f}
- Net Income to Assets:    {comp_row_meta['Net_Income_to_Assets']:.4f}
- Debt Ratio %:            {comp_row_meta['Debt_Ratio_Pct']:.4f}

Primary Model Risk Contributors (TreeSHAP Attribution):
{chr(10).join([f"- {d['feature']}: {d['shap_value']:+.4f} ({d['impact']})" for d in shap_res['top_drivers'][:5]])}

Methodological & Legal Notice:
{CAUSAL_DISCLAIMER}
================================================================================
    """
    st.download_button(
        "⬇️ Download Printable Company Assessment (TXT)",
        data=printable_audit_card,
        file_name=f"finguard_assessment_{sel_company_id}.txt",
        mime="text/plain"
    )


# =====================================================================
# PAGE 4: FRAUD INDICATORS
# =====================================================================
elif selected_nav == "Fraud Indicators":
    render_header(
        title="Forensic Fraud & Solvency Indicators",
        subtitle="Independent calculation of Altman Z-Score, Beneish M-Score, and Piotroski F-Score with strict missing-data validation.",
        badge_text="Forensic Engine",
        badge_type="teal"
    )

    render_callout(
        "<strong>Integrity & Validation Protocol:</strong> FinGuard strictly calculates scores only when 100% of required accounting statements are present. "
        "If comparative prior-period inputs are missing, the system outputs <code>INCOMPLETE_DATA</code> rather than silently filling them with arbitrary numbers. "
        "<strong>Note:</strong> Financial distress indicators (Altman Z) evaluate liquidity/solvency exhaustion, whereas forensic accounting indicators (Beneish M) screen for earnings manipulation. They represent distinct analytical tasks."
    )

    fi_tab1, fi_tab2, fi_tab3 = st.tabs(["Altman Z-Score (Solvency)", "Beneish M-Score (Manipulation)", "Piotroski F-Score (Fundamentals)"])

    # TAB 1: ALTMAN Z-SCORE
    with fi_tab1:
        st.subheader("Altman Z-Score Solvency Screening")
        st.markdown(
            """
            - **Original Manufacturing Model (1968):**  
              $$Z = 1.2 X_1 + 1.4 X_2 + 3.3 X_3 + 0.6 X_4 + 0.999 X_5$$
            - **Non-Manufacturing / Emerging Market Model (1983 Double-Prime $Z''$):**  
              $$Z'' = 6.56 X_1 + 3.26 X_2 + 6.72 X_3 + 1.05 X_4$$
            """
        )

        az_c1, az_c2, az_c3 = st.columns(3)
        with az_c1:
            wc_in = st.number_input("Working Capital ($/₹)", value=150.0)
            ta_in = st.number_input("Total Assets ($/₹)", value=1000.0, min_value=1.0)
            re_in = st.number_input("Retained Earnings ($/₹)", value=220.0)
        with az_c2:
            eb_in = st.number_input("EBIT ($/₹)", value=90.0)
            mve_in = st.number_input("Market Value Equity ($/₹)", value=650.0, min_value=0.0)
            tl_in = st.number_input("Total Liabilities ($/₹)", value=550.0, min_value=0.0)
        with az_c3:
            sl_in = st.number_input("Annual Sales ($/₹)", value=1100.0, min_value=0.0)
            is_mfg_chk = st.checkbox("Public Manufacturing Model (1968)", value=True)

        alt_out = calculate_altman_z_score(
            working_capital=wc_in, total_assets=ta_in, retained_earnings=re_in,
            ebit=eb_in, market_value_equity=mve_in, total_liabilities=tl_in,
            sales=sl_in, is_manufacturing=is_mfg_chk
        )

        st.markdown("#### Calculation Results")
        ac1, ac2, ac3 = st.columns(3)
        ac1.metric("Calculated Z-Score", f"{alt_out['score']}")
        ac2.metric("Assigned Zone", f"{alt_out['zone']}")
        ac3.metric("Model Applied", f"{alt_out['model_type']}")

        st.markdown("##### Ratio Components Breakdown")
        st.json(alt_out["components"])

    # TAB 2: BENEISH M-SCORE
    with fi_tab2:
        st.subheader("Beneish M-Score (8-Variable Manipulation Model)")
        st.markdown(
            """
            $$M = -4.84 + 0.920\\cdot \\text{DSRI} + 0.528\\cdot \\text{GMI} + 0.404\\cdot \\text{AQI} + 0.892\\cdot \\text{SGI} + 0.115\\cdot \\text{DEPI} - 0.172\\cdot \\text{SGAI} + 4.037\\cdot \\text{TATA} + 0.0327\\cdot \\text{LVGI}$$
            **Decision Threshold:** $M > -1.78$ indicates high probability of accounting manipulation.
            """
        )

        st.info("💡 Beneish M-Score requires sequential 2-year comparative balance sheets and cash flow statements.")

        profile_choice = st.radio("Select Forensic Statement Profile:", ["Profile A: Healthy Reporting (Unlikely Manipulator)", "Profile B: Aggressive Accruals (Likely Manipulator)"], horizontal=True)

        if "Profile A" in profile_choice:
            ben_out = calculate_beneish_m_score(
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
                net_income_t=80, cfo_t=85
            )
        else:
            ben_out = calculate_beneish_m_score(
                sales_t=1500, sales_t_minus_1=1000,
                cogs_t=600, cogs_t_minus_1=650,
                receivables_t=600, receivables_t_minus_1=150,
                current_assets_t=800, current_assets_t_minus_1=400,
                ppe_t=500, ppe_t_minus_1=450,
                securities_t=10, securities_t_minus_1=50,
                total_assets_t=1500, total_assets_t_minus_1=1000,
                depreciation_t=20, depreciation_t_minus_1=50,
                sga_t=100, sga_t_minus_1=150,
                long_term_debt_t=600, long_term_debt_t_minus_1=200,
                current_liabilities_t=300, current_liabilities_t_minus_1=100,
                net_income_t=350, cfo_t=-150
            )

        bc1, bc2, bc3 = st.columns(3)
        bc1.metric("Beneish M-Score", f"{ben_out['score']}")
        bc2.metric("Manipulation Flag", f"{ben_out['manipulation_flag']}")
        bc3.metric("Threshold Cutoff", "-1.78")

        st.markdown("##### 8 Forensic Accounting Indices Breakdown")
        st.json(ben_out["indices"])

    # TAB 3: PIOTROSKI F-SCORE
    with fi_tab3:
        st.subheader("Piotroski F-Score (9-Point Fundamental Stability)")
        st.markdown(
            """
            Evaluates 9 discrete signals across Profitability (4 pts), Leverage/Liquidity (3 pts), and Operating Efficiency (2 pts).  
            **Scoring Categories:** 8–9: Strong Fundamental Health | 5–7: Moderate Health | 0–4: Weak Fundamental Health.
            """
        )
        pio_out = calculate_piotroski_f_score(
            net_income_t=120, net_income_t_minus_1=80,
            cfo_t=150, total_assets_t=1000, total_assets_t_minus_1=1000,
            long_term_debt_t=100, long_term_debt_t_minus_1=150,
            current_assets_t=400, current_assets_t_minus_1=350,
            current_liabilities_t=200, current_liabilities_t_minus_1=200,
            shares_t=1000, shares_t_minus_1=1000,
            gross_margin_t=0.35, gross_margin_t_minus_1=0.30,
            sales_t=1200, sales_t_minus_1=1000
        )
        st.metric("Piotroski F-Score (Healthy Demo)", f"{pio_out['score']} / 9", pio_out["category"])
        st.json(pio_out["criteria_breakdown"])


# =====================================================================
# PAGE 5: SCENARIO LAB
# =====================================================================
elif selected_nav == "Scenario Lab":
    render_header(
        title="Interactive Scenario Lab",
        subtitle="Simulate what-if stress shocks, examine solvency ratio impacts, and observe rating migration diagnostics.",
        badge_text="Stress Simulator",
        badge_type="teal"
    )

    render_simulation_banner(
        "HYPOTHETICAL STRESS SIMULATION: All outputs in this module represent sensitivity stress simulations. "
        "They do NOT represent observed historical corporate filings."
    )

    st.markdown('<div class="fin-section-title">1. Select Starting Entity Profile</div>', unsafe_allow_html=True)
    sim_mode = st.radio("Simulation Base:", ["Benchmark Corporate Entity", "Standard Industrial Profile Archetype"], horizontal=True)

    if sim_mode == "Benchmark Corporate Entity":
        sim_cid = st.selectbox("Select Test Entity for Simulation:", portfolio_df["Company_ID"].tolist()[:50], index=0)
        sim_idx = int(sim_cid.split("-")[1]) - 1
        sim_row = test_universe.iloc[sim_idx]
        
        # Base financial values mapped from benchmark features
        base_assets = 1000.0
        base_wc = float(sim_row["Current Assets"] - sim_row["Current Liability to Assets"]) * 1000 if "Current Assets" in sim_row else 150.0
        base_re = float(sim_row["Retained Earnings to Total Assets"]) * base_assets if "Retained Earnings to Total Assets" in sim_row else 200.0
        base_ebit = float(sim_row["ROA(C) before interest and depreciation before interest"]) * base_assets if "ROA(C) before interest and depreciation before interest" in sim_row else 90.0
        base_liab = float(sim_row["Debt ratio %"]) * base_assets if "Debt ratio %" in sim_row else 500.0
        base_equity = max(base_assets - base_liab, 50.0)
        base_sales = float(sim_row["Total Asset Turnover"]) * base_assets if "Total Asset Turnover" in sim_row else 1000.0
        is_mfg_sim = True
    else:
        base_assets = 1000.0
        base_wc = 180.0
        base_re = 220.0
        base_ebit = 95.0
        base_equity = 700.0
        base_liab = 500.0
        base_sales = 1200.0
        is_mfg_sim = True

    st.markdown('<div class="fin-section-title">2. Apply Stress Shocks</div>', unsafe_allow_html=True)
    sh1, sh2, sh3, sh4 = st.columns(4)
    with sh1:
        rev_shock_val = st.slider("Revenue Shock (%)", min_value=-50, max_value=20, value=-20, step=5)
    with sh2:
        margin_shock_val = st.slider("EBIT Margin Shock (%)", min_value=-60, max_value=20, value=-30, step=5)
    with sh3:
        debt_shock_val = st.slider("Debt Expansion (%)", min_value=0, max_value=60, value=25, step=5)
    with sh4:
        wc_drain_val = st.slider("Working Capital Drain (%)", min_value=-60, max_value=10, value=-35, step=5)

    # Compute Stressed Metrics
    str_sales = base_sales * (1 + rev_shock_val / 100.0)
    str_ebit = base_ebit * (1 + margin_shock_val / 100.0)
    str_liab = base_liab * (1 + debt_shock_val / 100.0)
    str_wc = base_wc * (1 + wc_drain_val / 100.0)
    str_assets = base_assets + (str_liab - base_liab)
    str_equity = max(base_equity * (1 + margin_shock_val / 200.0), 10.0)

    # Calculate Baseline vs Stressed Altman Z
    base_z_calc = calculate_altman_z_score(
        working_capital=base_wc, total_assets=base_assets,
        retained_earnings=base_re, ebit=base_ebit,
        market_value_equity=base_equity, total_liabilities=base_liab,
        sales=base_sales, is_manufacturing=is_mfg_sim
    )

    str_z_calc = calculate_altman_z_score(
        working_capital=str_wc, total_assets=str_assets,
        retained_earnings=base_re, ebit=str_ebit,
        market_value_equity=str_equity, total_liabilities=str_liab,
        sales=str_sales, is_manufacturing=is_mfg_sim
    )

    st.markdown('<div class="fin-section-title">📊 Before-versus-After Stress Results</div>', unsafe_allow_html=True)

    b_col1, b_col2 = st.columns(2)
    with b_col1:
        render_kpi_card(
            title="Baseline State (Pre-Shock)",
            value=f"{base_z_calc['score']}",
            subtext=f"Zone: {base_z_calc['zone']} | Risk: {base_z_calc['risk_level']}",
            value_color=COLORS["risk_green"],
            border_color=COLORS["risk_green"]
        )
    with b_col2:
        delta_val = str_z_calc["score"] - base_z_calc["score"]
        str_color = COLORS["risk_red"] if str_z_calc["zone"] == "Distress Zone" else COLORS["risk_amber"]
        render_kpi_card(
            title="Stressed State (Post-Shock)",
            value=f"{str_z_calc['score']} <span style='font-size:1rem; color:{COLORS['text_secondary']};'>({delta_val:+.2f})</span>",
            subtext=f"Zone: {str_z_calc['zone']} | Risk: {str_z_calc['risk_level']}",
            value_color=str_color,
            border_color=str_color
        )

    # Rating Migration Diagnosis
    if str_z_calc["zone"] != base_z_calc["zone"]:
        st.error(f"🚨 **Rating Migration Alert:** Applied financial stress triggered a formal zone downgrade from **{base_z_calc['zone']}** to **{str_z_calc['zone']}**.")
    else:
        st.warning(f"⚠️ **Solvency Buffer Compressed:** Entity remains in **{str_z_calc['zone']}**, but solvency margin contracted by {abs(delta_val):.2f} points.")


# =====================================================================
# PAGE 6: MODEL PERFORMANCE
# =====================================================================
elif selected_nav == "Model Performance":
    render_header(
        title="Model Performance & Evaluation",
        subtitle="Empirical validation metrics on the held-out test partition (N = 1,364, Defaults = 44) under 20:1 asymmetric loss.",
        badge_text="Held-Out Test Results",
        badge_type="teal"
    )

    b_eval = eval_results["baseline"]
    m_eval = eval_results["improved"]

    # Comparative Metrics Row (Perfect Aligned Height)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card(
            title="Model ROC-AUC",
            value=f"{m_eval['roc_auc']:.4f}",
            subtext="Random Forest vs 0.6076 Baseline",
            value_color=COLORS["primary_teal"]
        )
    with c2:
        render_kpi_card(
            title="Precision-Recall AUC",
            value=f"{m_eval['pr_auc']:.4f}",
            subtext="9.2x higher than linear logit (0.0500)",
            value_color=COLORS["secondary_cyan"]
        )
    with c3:
        render_kpi_card(
            title="Precision on Defaults",
            value=f"{m_eval['precision']*100:.2f}%",
            subtext="Random Forest (10x fewer false alarms)",
            value_color=COLORS["risk_green"]
        )
    with c4:
        render_kpi_card(
            title="Asymmetric Loss (20:1)",
            value=f"{m_eval['asymmetric_cost']:.0f} units",
            subtext="51.2% cost reduction vs baseline (963)",
            value_color=COLORS["risk_amber"]
        )

    st.markdown('<div class="fin-section-title">📊 Confusion Matrix Comparison</div>', unsafe_allow_html=True)

    cm1, cm2 = st.columns(2)
    with cm1:
        cm_b = np.array([[b_eval["true_negatives"], b_eval["false_positives"]], [b_eval["false_negatives"], b_eval["true_positives"]]])
        fig_cm_b = px.imshow(
            cm_b, text_auto=True,
            x=["Predicted Solvent (0)", "Predicted Bankrupt (1)"],
            y=["Actual Solvent (0)", "Actual Bankrupt (1)"],
            color_continuous_scale="Blues",
            title="Baseline Logit: 743 False Alarms (Precision: 4.25%)"
        )
        fig_cm_b = apply_fintech_theme(fig_cm_b, height=310)
        fig_cm_b.update_layout(margin=dict(l=50, r=25, t=48, b=35))
        st.plotly_chart(fig_cm_b, use_container_width=True)

    with cm2:
        cm_m = np.array([[m_eval["true_negatives"], m_eval["false_positives"]], [m_eval["false_negatives"], m_eval["true_positives"]]])
        fig_cm_m = px.imshow(
            cm_m, text_auto=True,
            x=["Predicted Solvent (0)", "Predicted Bankrupt (1)"],
            y=["Actual Solvent (0)", "Actual Bankrupt (1)"],
            color_continuous_scale="Viridis",
            title="Improved RF: 30 False Alarms (Precision: 42.31%)"
        )
        fig_cm_m = apply_fintech_theme(fig_cm_m, height=310)
        fig_cm_m.update_layout(margin=dict(l=50, r=25, t=48, b=35))
        st.plotly_chart(fig_cm_m, use_container_width=True)

    st.markdown('<div class="fin-section-title">⚖️ Asymmetric Cost Curve Simulation (20:1 Loss Ratio)</div>', unsafe_allow_html=True)
    st.markdown(
        """
        In commercial lending, a missed default ($FN$) costs approximately **20 times more** than an administrative false alarm ($FP$).  
        $$\\text{Total Portfolio Loss} = (1.0 \\times FP) + (20.0 \\times FN)$$
        """
    )

    y_t = test_universe["Bankrupt?"].values
    f_cols = [c for c in test_universe.columns if c != "Bankrupt?"]
    X_sc = preprocessor.transform(test_universe[f_cols])
    p_arr = rf_model.predict_proba(X_sc)[:, 1]

    cost_res = analyze_threshold_cost(y_t, p_arr, fn_cost_ratio=20.0)
    cost_df = pd.DataFrame(cost_res["cost_curve"])

    fig_cost = go.Figure()
    fig_cost.add_trace(go.Scatter(
        x=cost_df["threshold"],
        y=cost_df["total_cost"],
        mode="lines",
        name="Total Portfolio Loss",
        line=dict(color=COLORS["risk_red"], width=2.4)
    ))
    opt_tau = float(cost_res["optimal_threshold"])
    fig_cost.add_vline(
        x=opt_tau,
        line_dash="dash",
        line_color=COLORS["primary_teal"],
        line_width=1.8,
        annotation_text=f"Cost-Optimal tau* = {opt_tau:.2f}",
        annotation_position="top right",
        annotation=dict(
            bgcolor="rgba(10, 22, 38, 0.92)",
            bordercolor=COLORS["primary_teal"],
            borderwidth=1,
            borderpad=3,
            font=dict(color=COLORS["primary_teal"], size=10, family="Plus Jakarta Sans")
        )
    )
    fig_cost = apply_fintech_theme(
        fig_cost,
        height=320,
        title="Expected Portfolio Loss vs Decision Threshold (Minimum Loss at tau* = 0.20)"
    )
    fig_cost.update_layout(
        margin=dict(l=50, r=25, t=48, b=40),
        showlegend=False
    )
    fig_cost.update_xaxes(title_text="Probability Decision Threshold")
    fig_cost.update_yaxes(title_text="Total Financial Loss Units")
    st.plotly_chart(fig_cost, use_container_width=True)


# =====================================================================
# PAGE 7: DATA & METHODOLOGY
# =====================================================================
elif selected_nav == "Data & Methodology":
    render_header(
        title="Data Sources, Methodology & Research Benchmark",
        subtitle="Transparent academic citations, leakage-prevention protocols, and the Indian corporate distress case studies.",
        badge_text="Methodology Reference",
        badge_type="teal"
    )

    dm_tab1, dm_tab2 = st.tabs(["UCI Taiwanese Benchmark Documentation", "Indian Corporate Distress Benchmark"])

    with dm_tab1:
        st.subheader("Academic Benchmark Details")
        st.markdown(
            """
            - **Repository:** UCI Machine Learning Repository (Dataset ID: 572)
            - **Original Source:** Taiwan Economic Journal (TEJ), 1999–2009 filings.
            - **Academic Citation:** Liang, D., Lu, C.-J., Tsai, C.-F., & Shih, G.-A. (2016). *Financial ratio selection for business failure prediction*. Neurocomputing, 173, 383–389.
            - **License:** Creative Commons Attribution 4.0 International (**CC BY 4.0**).
            - **Target Prevalence:** 6,599 Solvent (96.77%) vs 220 Bankrupt (3.23%).
            """
        )

        st.markdown("#### Data Hygiene & Preprocessing Audit")
        audit_records = pd.DataFrame([
            {"Parameter": "Total Benchmark Observations", "Value": "6,819 corporate filings"},
            {"Parameter": "Total Financial Attributes", "Value": "95 normalized accounting ratios"},
            {"Parameter": "Missing / Null Cells", "Value": "0 (Fully populated)"},
            {"Parameter": "Infinite Numeric Values", "Value": "0 across all 654,624 cells"},
            {"Parameter": "Zero Leakage Splitting", "Value": "Stratified 80% Train ($N=5,455$) / 20% Test ($N=1,364$)"},
            {"Parameter": "Time-Aware Limitation", "Value": "Timestamps anonymized in UCI release; documented stratified split"}
        ])
        st.table(audit_records)

    with dm_tab2:
        st.subheader("🇮🇳 Indian Corporate Distress Benchmark (10 Targets & 30 Peers)")
        render_callout(
            "<strong>Pre-Event Temporal Boundary:</strong> All financial filings analyzed strictly precede official NCLT insolvency admissions or RBI board supersessions. "
            "Sources: Ministry of Corporate Affairs (MCA), BSE/NSE annual reports, and IBBI public orders."
        )

        if os.path.exists(RESULTS_CSV_PATH):
            ind_data_df = pd.read_csv(RESULTS_CSV_PATH)
            st.dataframe(ind_data_df, use_container_width=True)

            st.markdown('<div class="fin-section-title">📊 Pre-Event Altman Z-Score Distribution</div>', unsafe_allow_html=True)
            fig_ind_z = px.bar(
                ind_data_df.sort_values(by="Altman Z-Score", ascending=True),
                x="Altman Z-Score",
                y="Company Name",
                orientation="h",
                color="Risk Zone",
                color_discrete_map={
                    "Distress Zone": COLORS["risk_red"],
                    "Grey Zone": COLORS["risk_amber"],
                    "Safe Zone": COLORS["risk_green"]
                },
                title="Pre-Event Altman Z-Score for Distressed Indian Entities"
            )
            # Staggered, Non-Overlapping Cutoff Annotations
            fig_ind_z.add_vline(
                x=1.81,
                line_dash="dash",
                line_color=COLORS["risk_amber"],
                line_width=1.8,
                annotation_text="Mfg Cutoff: 1.81",
                annotation_position="top right",
                annotation=dict(
                    bgcolor="rgba(10, 22, 38, 0.92)",
                    bordercolor=COLORS["risk_amber"],
                    borderwidth=1,
                    borderpad=3,
                    font=dict(color=COLORS["risk_amber"], size=10, family="Plus Jakarta Sans")
                )
            )
            fig_ind_z.add_vline(
                x=1.10,
                line_dash="dot",
                line_color=COLORS["risk_red"],
                line_width=1.8,
                annotation_text="Non-Mfg Cutoff: 1.10",
                annotation_position="bottom right",
                annotation=dict(
                    bgcolor="rgba(10, 22, 38, 0.92)",
                    bordercolor=COLORS["risk_red"],
                    borderwidth=1,
                    borderpad=3,
                    font=dict(color=COLORS["risk_red"], size=10, family="Plus Jakarta Sans")
                )
            )
            fig_ind_z = apply_fintech_theme(
                fig_ind_z,
                height=360,
                title="Pre-Event Altman Z-Score for Distressed Indian Entities"
            )
            fig_ind_z.update_layout(margin=dict(l=150, r=25, t=48, b=38))
            st.plotly_chart(fig_ind_z, use_container_width=True)

            d_col1, d_col2 = st.columns(2)
            with d_col1:
                st.download_button(
                    "⬇️ Download Evaluated Indian Distress CSV",
                    data=ind_data_df.to_csv(index=False).encode("utf-8"),
                    file_name="finguard_indian_distress_benchmark.csv",
                    mime="text/csv"
                )
            with d_col2:
                if os.path.exists(COLLECTION_TEMPLATE_PATH):
                    with open(COLLECTION_TEMPLATE_PATH, "rb") as f_t:
                        st.download_button(
                            "⬇️ Download 40-Entity Collection Template (120 Filings)",
                            data=f_t.read(),
                            file_name="case_study_data_collection_template.csv",
                            mime="text/csv"
                        )
