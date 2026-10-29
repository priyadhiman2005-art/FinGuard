"""
FinGuard - Presentation PDF Generator (ReportLab)
=================================================
Produces an authentic, professional, selectable-text 10-slide presentation deck
for Zeckathon — PS2: Financial Risk & Fraud Analytics.

Strict constraints:
- Exactly 10 slides
- Landscape format (11 x 8.5 inches)
- < 20 MB file size
- High contrast, modern fintech design, readable bullet points
"""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, HRFlowable
)
from reportlab.pdfgen import canvas

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PRESENTATION_PDF_PATH = os.path.join(BASE_DIR, "presentations", "FinGuard_Hackathon_Presentation.pdf")
CHARTS_DIR = os.path.join(BASE_DIR, "reports")

SLIDE_WIDTH, SLIDE_HEIGHT = landscape(letter)  # 11 x 8.5 inches (792 x 612 pt)


class SlideCanvas(canvas.Canvas):
    """Draws consistent presentation background, headers, and footer slide numbers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_slide_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_slide_decorations(self, total_slides):
        self.saveState()
        # Top accent bar
        self.setFillColor(colors.HexColor("#0F4C81"))
        self.rect(0, SLIDE_HEIGHT - 6, SLIDE_WIDTH, 6, fill=1, stroke=0)

        # Footer
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#718096"))
        self.drawString(40, 22, "FinGuard: Corporate Financial Risk & Fraud Detection System | Zeckathon 2026 (PS2)")
        self.drawRightString(SLIDE_WIDTH - 40, 22, f"Slide {self._pageNumber} of {total_slides}")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.75)
        self.line(40, 32, SLIDE_WIDTH - 40, 32)

        self.restoreState()


def build_presentation():
    doc = SimpleDocTemplate(
        PRESENTATION_PDF_PATH,
        pagesize=landscape(letter),
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_slide_title = ParagraphStyle(
        "TitleSlideTitle",
        fontName="Helvetica-Bold",
        fontSize=26,
        leading=32,
        textColor=colors.HexColor("#0F2942"),
        spaceAfter=10
    )
    title_slide_sub = ParagraphStyle(
        "TitleSlideSub",
        fontName="Helvetica",
        fontSize=13,
        leading=18,
        textColor=colors.HexColor("#4A5568"),
        spaceAfter=15
    )
    slide_h1 = ParagraphStyle(
        "SlideH1",
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F4C81"),
        spaceAfter=4
    )
    slide_h2 = ParagraphStyle(
        "SlideH2",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#2D3748"),
        spaceBefore=4,
        spaceAfter=3
    )
    slide_body = ParagraphStyle(
        "SlideBody",
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#2D3748")
    )
    slide_bullet = ParagraphStyle(
        "SlideBullet",
        parent=slide_body,
        leftIndent=14,
        firstLineIndent=-10,
        spaceBefore=2,
        spaceAfter=2
    )
    badge_style = ParagraphStyle(
        "BadgeText",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0F4C81")
    )

    story = []

    # =========================================================================
    # SLIDE 1: TITLE & TEAM PARTICIPANT DETAILS
    # =========================================================================
    story.append(Spacer(1, 40))
    story.append(Paragraph("FinGuard: Corporate Financial Risk & Fraud Detection System", title_slide_title))
    story.append(Paragraph("Early-Warning Intelligence for Corporate Insolvency Forecasting & Forensic Statement Analytics", title_slide_sub))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F4C81"), spaceBefore=5, spaceAfter=20))

    meta_info = [
        [Paragraph("<b>Hackathon:</b> Zeckathon 2026", slide_body), Paragraph("<b>Participant:</b> 4th-Year B.Tech Computer Science Student", slide_body)],
        [Paragraph("<b>Problem Statement:</b> PS2: Financial Risk & Fraud Analytics", slide_body), Paragraph("<b>Tech Stack:</b> Python, Scikit-learn, Streamlit, SHAP, Plotly", slide_body)],
        [Paragraph("<b>Dataset:</b> UCI Machine Learning Repository (ID: 572)", slide_body), Paragraph("<b>Status:</b> Fully Functional & Unit-Tested Prototype", slide_body)]
    ]
    meta_table = Table(meta_info, colWidths=[350, 360])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 25))
    story.append(Paragraph("<i>Educational & Academic Prototype | Developed for Hackathon Evaluation</i>", ParagraphStyle("Disc", fontName="Helvetica-Oblique", fontSize=8.5, textColor=colors.HexColor("#718096"))))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 2: PROBLEM STATEMENT
    # =========================================================================
    story.append(Paragraph("Problem Statement: Detecting Corporate Distress Early", slide_h1))
    story.append(Paragraph("The challenges of corporate insolvency forecasting and accounting fraud screening:", slide_body))
    story.append(Spacer(1, 10))

    col_data_2 = [
        [
            Paragraph("<b>1. Extreme Class Imbalance</b>", slide_h2),
            Paragraph("<b>2. Asymmetric Financial Loss</b>", slide_h2),
            Paragraph("<b>3. Conflating Distress vs Fraud</b>", slide_h2)
        ],
        [
            Paragraph("• In authentic portfolios, defaulting companies make up <b>only 3.23% of filings</b> (30:1 solvency ratio).<br/>• Naive accuracy is deeply misleading: a dummy model predicting 0% bankruptcies achieves 96.8% accuracy while missing 100% of defaults.", slide_body),
            Paragraph("• In credit syndicates, a <b>missed default costs ~20x more</b> than an unnecessary audit.<br/>• Standard ML models optimize overall accuracy rather than minimizing cost-weighted portfolio losses.", slide_body),
            Paragraph("• <b>Bankruptcy Risk:</b> Liquidity exhaustion and debt coverage failure.<br/>• <b>Accounting Fraud:</b> Aggressive revenue inflation or capitalized costs.<br/>• They require separate, specialized screening tools.", slide_body)
        ]
    ]
    t2 = Table(col_data_2, colWidths=[235, 235, 240])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F4C81")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t2)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 3: WHY THE PROBLEM MATTERS
    # =========================================================================
    story.append(Paragraph("Why It Matters: Financial & Systemic Consequences", slide_h1))
    story.append(Paragraph("The macro and microeconomic necessity for multi-tiered early-warning indicators:", slide_body))
    story.append(Spacer(1, 12))

    points_3 = [
        [Paragraph("<b>Institutional Banking</b>", slide_h2), Paragraph("• Non-Performing Assets (NPAs) lock bank capital and destabilize lending capacity.<br/>• Early warning enables loan covenants, collateral enhancement, or timely restructuring.", slide_body)],
        [Paragraph("<b>Public Investors & Vendors</b>", slide_h2), Paragraph("• Sudden corporate collapses (e.g. DHFL, IL&FS) wipe out equity and unsecured supply vendors.<br/>• Forensic statement analysis provides retail investors and rating agencies with audit triggers.", slide_body)],
        [Paragraph("<b>Operational Audit Constraints</b>", slide_h2), Paragraph("• Risk audit teams have finite bandwidth: they cannot review 500 companies simultaneously.<br/>• <b>A strict Top-5% Review Capacity Policy</b> is essential to maximize audit yield under tight resource budgets.", slide_body)]
    ]
    t3 = Table(points_3, colWidths=[180, 530])
    t3.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EFF6FF")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(t3)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 4: PROPOSED FINGUARD SOLUTION
    # =========================================================================
    story.append(Paragraph("Proposed FinGuard Solution: 4-Layer Architecture", slide_h1))
    story.append(Paragraph("An end-to-end analytics platform uniting machine learning, classical scoring, and policy triage:", slide_body))
    story.append(Spacer(1, 10))

    layers_data = [
        [Paragraph("<b>Layer</b>", slide_body), Paragraph("<b>Key Innovation</b>", slide_body), Paragraph("<b>Engineering Implementation</b>", slide_body)],
        [Paragraph("<b>1. Data Layer</b>", slide_h2), Paragraph("Zero data leakage, stratified splitting", slide_body), Paragraph("Median Imputer + RobustScaler fitted strictly on training partition.", slide_body)],
        [Paragraph("<b>2. Model Layer</b>", slide_h2), Paragraph("Class-balanced non-linear ensemble", slide_body), Paragraph("Balanced Random Forest (150 trees) vs Logistic Regression baseline.", slide_body)],
        [Paragraph("<b>3. Forensic Layer</b>", slide_h2), Paragraph("Separated solvency vs fraud scoring", slide_body), Paragraph("Altman Z-Score, Beneish M-Score, and Piotroski F-Score (zero fake data).", slide_body)],
        [Paragraph("<b>4. Policy Layer</b>", slide_h2), Paragraph("Operational review capacity + cost curve", slide_body), Paragraph("Top-5% Review Capacity Policy + 20:1 Cost-Optimal decision threshold.", slide_body)],
        [Paragraph("<b>5. Explainability</b>", slide_h2), Paragraph("Transparent feature attribution", slide_body), Paragraph("TreeSHAP feature waterfalls with resilient heuristic fallback & disclaimer.", slide_body)]
    ]
    t4 = Table(layers_data, colWidths=[120, 260, 330])
    t4.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F4C81")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t4)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 5: SYSTEM ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("System Architecture & Dataflow Workflow", slide_h1))
    story.append(Paragraph("Modular pipeline architecture ensuring auditability, speed, and zero data leakage:", slide_body))
    story.append(Spacer(1, 10))

    flow_data = [
        [Paragraph("<b>Raw Ingestion</b>", slide_h2), Paragraph("&rarr;", slide_h1), Paragraph("<b>Zero-Leakage Prep</b>", slide_h2), Paragraph("&rarr;", slide_h1), Paragraph("<b>Dual Predictive Core</b>", slide_h2), Paragraph("&rarr;", slide_h1), Paragraph("<b>Actionable UI</b>", slide_h2)],
        [
            Paragraph("• UCI ML Repo ID 572<br/>• 6,819 Corporate Filings<br/>• 95 Normalized Ratios", slide_body),
            Paragraph("", slide_body),
            Paragraph("• 80% Train / 20% Test<br/>• RobustScaler on Train<br/>• Time-Split Disclosed", slide_body),
            Paragraph("", slide_body),
            Paragraph("• Random Forest Classifier<br/>• Altman Z + Beneish M<br/>• Piotroski F-Score", slide_body),
            Paragraph("", slide_body),
            Paragraph("• Streamlit Web App<br/>• Top-5% Audit Triage<br/>• Local SHAP Insights", slide_body)
        ]
    ]
    t5 = Table(flow_data, colWidths=[150, 20, 150, 20, 180, 20, 170])
    t5.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 1), colors.HexColor("#EFF6FF")),
        ("BACKGROUND", (2, 0), (2, 1), colors.HexColor("#F0FDF4")),
        ("BACKGROUND", (4, 0), (4, 1), colors.HexColor("#FEF3C7")),
        ("BACKGROUND", (6, 0), (6, 1), colors.HexColor("#F5F3FF")),
        ("BOX", (0, 0), (0, 1), 1, colors.HexColor("#3B82F6")),
        ("BOX", (2, 0), (2, 1), 1, colors.HexColor("#22C55E")),
        ("BOX", (4, 0), (4, 1), 1, colors.HexColor("#F59E0B")),
        ("BOX", (6, 0), (6, 1), 1, colors.HexColor("#8B5CF6")),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("ALIGN", (3, 0), (3, -1), "CENTER"),
        ("ALIGN", (5, 0), (5, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t5)
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>Zero Leakage Guarantee:</b> Preprocessing pipeline parameters (median, IQR) are learned strictly on `X_train` and applied unchanged to `X_test`.", ParagraphStyle("Note", fontName="Helvetica-Bold", fontSize=9, textColor=colors.HexColor("#0F4C81"))))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 6: DATASET & METHODOLOGY
    # =========================================================================
    story.append(Paragraph("Dataset & Methodology: Authentic Benchmark Verification", slide_h1))
    story.append(Paragraph("Citations, class balance, and data hygiene audits:", slide_body))
    story.append(Spacer(1, 10))

    ds_col_data = [
        [Paragraph("<b>Dataset Metadata & Citation</b>", slide_h2), Paragraph("<b>Data Hygiene & Validation Audit</b>", slide_h2)],
        [
            Paragraph(
                "• <b>Dataset:</b> Taiwanese Bankruptcy Prediction (UCI ID: 572)<br/>"
                "• <b>Source:</b> Taiwan Economic Journal (TEJ), 1999–2009.<br/>"
                "• <b>Academic Citation:</b> Liang et al. (2016), <i>Neurocomputing</i>.<br/>"
                "• <b>License:</b> CC BY 4.0 (Open for research and benchmark use).<br/>"
                "• <b>Attributes:</b> 95 normalized financial ratios + 1 binary target.<br/>"
                "• <b>Target Distribution:</b> 6,599 solvent (96.8%) vs 220 bankrupt (3.23%).",
                slide_body
            ),
            Paragraph(
                "• <b>Missing Values:</b> 0 across all 654,624 matrix cells.<br/>"
                "• <b>Infinite Values:</b> 0 infinite entries detected.<br/>"
                "• <b>Train/Test Split:</b> 80% Train ($N=5,455$) / 20% Test ($N=1,364$).<br/>"
                "• <b>Imbalance Handling:</b> Class-weighted loss functions (`balanced_subsample`).<br/>"
                "• <b>Time-Split Limitation:</b> UCI release anonymizes timestamps; documented stratified split preserves exact 3.23% class distribution.",
                slide_body
            )
        ]
    ]
    t6 = Table(ds_col_data, colWidths=[355, 355])
    t6.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white]),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(t6)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 7: ACTUAL MODEL RESULTS & RISK INDICATORS
    # =========================================================================
    story.append(Paragraph("Actual Model Evaluation Results (Unseen Test Set)", slide_h1))
    story.append(Paragraph("Held-out test partition evaluation: N = 1,364 instances with 44 actual defaults:", slide_body))
    story.append(Spacer(1, 8))

    res_data = [
        [Paragraph("<b>Metric</b>", slide_body), Paragraph("<b>Baseline: Logistic Reg</b>", slide_body), Paragraph("<b>Improved: Random Forest</b>", slide_body), Paragraph("<b>Practical Advantage</b>", slide_body)],
        [Paragraph("<b>Accuracy</b>", slide_body), Paragraph("44.72%", slide_body), Paragraph("<b>96.19%</b>", slide_body), Paragraph("Eliminates severe over-flagging.", slide_body)],
        [Paragraph("<b>Precision</b>", slide_body), Paragraph("4.25% (33 / 776)", slide_body), Paragraph("<b>42.31%</b> (22 / 52)", slide_body), Paragraph("<b>10x fewer false alarms</b> with RF.", slide_body)],
        [Paragraph("<b>Recall (Defaults Caught)</b>", slide_body), Paragraph("<b>75.00%</b> (33 / 44)", slide_body), Paragraph("50.00% (22 / 44)", slide_body), Paragraph("At default 0.5 threshold (tuneable).", slide_body)],
        [Paragraph("<b>ROC-AUC</b>", slide_body), Paragraph("0.6076", slide_body), Paragraph("<b>0.9466</b>", slide_body), Paragraph("Exceptional risk ranking separation.", slide_body)],
        [Paragraph("<b>PR-AUC (Avg Precision)</b>", slide_body), Paragraph("0.0500", slide_body), Paragraph("<b>0.4610</b>", slide_body), Paragraph("<b>9.2x increase</b> over baseline.", slide_body)],
        [Paragraph("<b>False Positives (Alarms)</b>", slide_body), Paragraph("743 companies", slide_body), Paragraph("<b>30 companies</b>", slide_body), Paragraph("Saves 713 wasted credit investigations.", slide_body)],
        [Paragraph("<b>Asymmetric Cost (FP + 20*FN)</b>", slide_body), Paragraph("963.0 units", slide_body), Paragraph("<b>470.0 units</b>", slide_body), Paragraph("<b>51.2% total portfolio cost reduction</b>.", slide_body)]
    ]
    t7 = Table(res_data, colWidths=[150, 160, 160, 240])
    t7.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F4C81")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t7)
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Top Empirical Risk Drivers (MDI):</b> 1. Borrowing dependency (5.7%) | 2. Net Income / Assets (4.9%) | 3. Persistent EPS (4.7%) | 4. Debt / Net Worth (3.9%).", ParagraphStyle("Drivers", fontName="Helvetica", fontSize=8.5, textColor=colors.HexColor("#4A5568"))))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 8: DASHBOARD DEMONSTRATION & FEATURES
    # =========================================================================
    story.append(Paragraph("FinGuard Streamlit Dashboard: Interactive Experience", slide_h1))
    story.append(Paragraph("A production-grade, 7-page interactive risk platform running on Streamlit & Plotly:", slide_body))
    story.append(Spacer(1, 10))

    dash_features = [
        [Paragraph("<b>Dashboard Page</b>", slide_h2), Paragraph("<b>Core Functional Capabilities</b>", slide_body)],
        [Paragraph("<b>1. Overview & Disclaimers</b>", slide_body), Paragraph("Executive summaries, key metrics, and formal academic/educational disclaimers.", slide_body)],
        [Paragraph("<b>2. Data Quality & Audit</b>", slide_body), Paragraph("Interactive class imbalance visualization, 4 feature category breakdowns, zero-leakage specs.", slide_body)],
        [Paragraph("<b>3. Model Comparison</b>", slide_body), Paragraph("Interactive Plotly confusion matrices, ROC/PR comparisons, and feature importance rankings.", slide_body)],
        [Paragraph("<b>4. Single Entity Scoring</b>", slide_body), Paragraph("Manual entry or test set picker; real-time Altman Z, Beneish M, and local TreeSHAP waterfalls.", slide_body)],
        [Paragraph("<b>5. Policy Simulator</b>", slide_body), Paragraph("Top-5% Review Capacity slider and interactive 20:1 Cost Curve loss minimization curve.", slide_body)],
        [Paragraph("<b>6. Indian Case Studies</b>", slide_body), Paragraph("Pre-event filings for 10 distressed Indian entities + 30 peers; downloadable CSVs & templates.", slide_body)],
        [Paragraph("<b>7. Demo Sandbox</b>", slide_body), Paragraph("Clearly labelled synthetic archetypes for stress-testing without fabricating real data.", slide_body)]
    ]
    t8 = Table(dash_features, colWidths=[200, 510])
    t8.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t8)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 9: LIMITATIONS & FUTURE IMPROVEMENTS
    # =========================================================================
    story.append(Paragraph("Limitations & Future Engineering Scope", slide_h1))
    story.append(Paragraph("Transparent integrity disclosures and analytical roadmap:", slide_body))
    story.append(Spacer(1, 10))

    lim_data = [
        [Paragraph("<b>Current Methodological Limitations</b>", slide_h2), Paragraph("<b>Future Enhancement Roadmap</b>", slide_h2)],
        [
            Paragraph(
                "• <b>Static Financial Snapshot:</b> The UCI benchmark lacks sequential annual timestamps for rolling time-splits.<br/>"
                "• <b>Cross-Border GAAP Divergence:</b> Taiwan TEJ accounting vs Indian Ind-AS and US GAAP have subtle ratio nuances.<br/>"
                "• <b>Absence of Macro Factors:</b> Model relies on reported financial statements without real-time interest rate or sector shock inputs.<br/>"
                "• <b>SHAP Non-Causality:</b> Feature attributions are statistical correlations, not legal proof of deliberate fraud.",
                slide_body
            ),
            Paragraph(
                "• <b>Financial NLP Integration:</b> Ingest Management Discussion & Analysis (MD&A) and auditor resignation filings via LLMs.<br/>"
                "• <b>Sequential Temporal Models:</b> Transition from tree ensembles to LSTM / Transformer architectures on 5-year statement sequences.<br/>"
                "• <b>Automated MCA/XBRL Scraping:</b> Real-time pipeline connecting directly to MCA21 / BSE APIs for continuous credit monitoring.<br/>"
                "• <b>Supply Chain Graph Risk:</b> Model contagion risk across interconnected vendor-buyer networks.",
                slide_body
            )
        ]
    ]
    t9 = Table(lim_data, colWidths=[355, 355])
    t9.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F4C81")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white]),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(t9)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 10: CONCLUSION & REFERENCES
    # =========================================================================
    story.append(Paragraph("Conclusion & Primary References", slide_h1))
    story.append(Paragraph("Summary of achievements and academic foundations:", slide_body))
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>Key FinGuard Accomplishments:</b><br/>"
        "1. <b>Empirical Superiority:</b> Balanced Random Forest cuts asymmetric financial loss by <b>51.2%</b> and lifts PR-AUC by <b>9.2x</b>.<br/>"
        "2. <b>Real-World Feasibility:</b> Top-5% capacity rule captures <b>54.5% of defaults</b> while screening only 5% of the portfolio.<br/>"
        "3. <b>Cross-Border Validation:</b> Accurately flagged <b>10 out of 10 distressed Indian corporate cases</b> in the Distress Zone prior to NCLT insolvency.<br/>"
        "4. <b>Ethical & Explainable AI:</b> Zero data leakage, strict missingness validation (zero fake data), and TreeSHAP explainability.",
        slide_body
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "<b>Academic References:</b><br/>"
        "• Liang et al. (2016). <i>Financial ratio selection for business failure prediction</i>. Neurocomputing, 173.<br/>"
        "• Altman, E. I. (1968, 1983). <i>Financial Ratios, Discriminant Analysis and Corporate Bankruptcy</i>. Journal of Finance.<br/>"
        "• Beneish, M. D. (1999). <i>The Detection of Earnings Manipulation</i>. Financial Analysts Journal, 55(5).<br/>"
        "• Piotroski, J. D. (2000). <i>Value Investing: Historical Financial Statement Information</i>. Journal of Accounting Research.<br/>"
        "• Lundberg & Lee (2017). <i>A Unified Approach to Interpreting Model Predictions (SHAP)</i>. NeurIPS 30.",
        ParagraphStyle("Refs", fontName="Helvetica", fontSize=8.5, leading=12, textColor=colors.HexColor("#4A5568"))
    ))
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>Thank you! Questions & Discussion Welcome.</b>", ParagraphStyle("ThankYou", fontName="Helvetica-Bold", fontSize=13, textColor=colors.HexColor("#0F4C81"))))

    # Build presentation
    doc.build(story, canvasmaker=SlideCanvas)
    print(f"Presentation PDF successfully generated at: {PRESENTATION_PDF_PATH}")


if __name__ == "__main__":
    build_presentation()

