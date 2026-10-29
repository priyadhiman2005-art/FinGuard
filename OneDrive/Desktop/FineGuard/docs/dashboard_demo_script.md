# FinGuard — Step-by-Step Dashboard Demo Walkthrough

**Purpose:** A structured, high-impact demonstration script for live hackathon judge presentations.  
**Launch Command:** `python -m streamlit run app.py` (Opens at `http://localhost:8501`)

---

### Step 1: Open Dashboard & Executive Overview ("Overview")
1. **Show the Fintech Banner:**
   - Point out the header: *"FinGuard: Corporate Financial Risk & Fraud Intelligence"*.
   - Mention the academic disclosure: Educational prototype built for **Zeckathon 2026 (PS2: Financial Risk & Fraud Analytics)**.
2. **Review the 4 Institutional KPI Cards:**
   - **Active Test Portfolio:** 1,364 Held-Out Corporate Filings (Zero Leakage).
   - **Model Discrimination:** 0.9466 ROC-AUC (Random Forest Ensemble).
   - **PR-AUC (Average Precision):** 0.4610 (9.2x higher than linear baseline).
   - **Top-5% Audit Yield:** 54.5% of total defaults captured in just 5% of the portfolio.
3. **Highlight the Core Distinction:**
   - Emphasize the separation between **Solvency Exhaustion** (Altman Z + ML) and **Accounting Manipulation** (Beneish M-Score).

---

### Step 2: Live Portfolio Triage ("Risk Explorer")
1. Click **"Risk Explorer"** in the sidebar.
2. **Demonstrate Dynamic Portfolio Filtering:**
   - Filter by **"Risk Tier"** (e.g. select only *Severe Distress (Tier 1)*).
   - Filter by **"Review Queue Policy"** &rarr; Select **"Top-5% Review Queue Only"**.
   - Show that exactly **68 companies** (5.0% of the 1,364-firm universe) are flagged under the budget capacity rule.
   - Point out that **24 out of 44 total defaulting companies** in the entire portfolio are captured in this top 5% queue!
3. **Explore the Interactive Visualizations:**
   - Switch between **"📈 Portfolio Risk Distribution"** (showing the 0.20 cost-optimal threshold and 5% cutoff) and **"🗺️ Financial Ratio Risk Heatmap"** (Borrowing Dependency vs Return on Assets).
4. **Export Findings:**
   - Click **"⬇️ Export Filtered Risk Ranking (CSV)"** to show audit export capability.

---

### Step 3: Deep Single-Entity Diagnosis ("Company Analysis")
1. Click **"Company Analysis"** in the sidebar.
2. **Select an Entity:**
   - Select a company (e.g. `COMP-0001` or any flagged entity in the top tier).
3. **Review the Entity Profile Card:**
   - Show the **ML Bankruptcy Probability**, **Portfolio Risk Rank** (e.g., #1 of 1,364), and **Audit Review Status** (FLAGGED Top 5%).
   - Point out the **Automated Warning Signals** (e.g. *"Severe Borrowing Dependency"*, *"Persistent Earnings Deterioration"*).
4. **Explain Local SHAP Attributions:**
   - Show the horizontal bar chart: Red bars indicate features pushing risk UP (e.g. debt ratio, borrowing dependency); Green bars indicate mitigating factors.
   - Read the non-causal disclaimer: *"SHAP values quantify statistical feature attribution and do not constitute legal proof of fraud."*
5. **Download Audit Card:**
   - Click **"⬇️ Download Printable Audit Card (TXT)"** to demonstrate one-click reporting.

---

### Step 4: Forensic Accounting Deep Dive ("Fraud Indicators")
1. Click **"Fraud Indicators"** in the sidebar.
2. **Altman Z-Score:**
   - Demonstrate the difference between the 1968 Manufacturing Model and the 1983 Non-Manufacturing Model ($Z''$).
3. **Beneish M-Score (8-Variable Forensic Model):**
   - Toggle between **"Profile A: Healthy Non-Manipulator"** ($M = -2.25$, Unlikely Manipulator) and **"Profile B: Aggressive Accrual Manipulator"** ($M = -1.15$, Flagged as Likely Manipulator).
   - Review the 8 forensic indices (DSRI, GMI, AQI, SGI, DEPI, SGAI, LVGI, TATA).
4. **Highlight Zero-Fabrication Rule:**
   - Point out that FinGuard strictly refuses to calculate fake scores when prior-period comparative statements are absent.

---

### Step 5: Stress-Testing Sensitivity Simulation ("Scenario Lab")
1. Click **"Scenario Lab"** in the sidebar.
2. **Explain the Purpose:**
   - Point to the yellow caution banner: *"Hypothetical Stress Simulation — what-if sensitivity analysis"*.
3. **Apply Stress Shocks via Sliders:**
   - Select *Profile A: Stable Industrial Manufacturer*.
   - Move **Revenue Shock** to $-25\%$.
   - Move **EBIT Margin Shock** to $-35\%$.
   - Move **New Debt Expansion** to $+30\%$.
4. **Observe Before-vs-After Results:**
   - Show the **Baseline State** ($Z = 2.45$, Grey Zone) vs **Stressed State** ($Z = 1.35$, Distress Zone).
   - Point out the **Rating Migration Alert** dynamically diagnosing the solvency downgrade.

---

### Step 6: Empirical Validation & Loss Curve ("Model Performance")
1. Click **"Model Performance"** in the sidebar.
2. **Review Verified Results Table:**
   - Baseline Logit (4.25% precision, 743 false alarms) vs Improved Random Forest (42.31% precision, 30 false alarms).
   - Point out the side-by-side **Plotly Confusion Matrices**.
3. **Demonstrate Asymmetric 20:1 Cost Minimization:**
   - Explain that a missed default costs 20x more than an audit false alarm.
   - Show the U-shaped **Total Portfolio Loss Curve** and the dashed line at $\tau^* = 0.20$, which cuts total loss to 318.0 units (a 66.9% reduction over baseline).

---

### Step 7: Authentic Benchmarks & Case Studies ("Data Sources")
1. Click **"Data Sources"** in the sidebar.
2. **Review Academic Metadata:**
   - UCI ML Repository Dataset ID 572, Liang et al. (2016), CC BY 4.0 license.
3. **Explore the Indian Corporate Distress Benchmark:**
   - Click the **"Indian Corporate Distress Case Studies"** tab.
   - Show the verified pre-event records for 10 entities (DHFL, Jet Airways, RCom, Sintex, Bhushan Steel, etc.).
   - Point out that all 10 were detected in the Distress Zone 1–2 years before NCLT insolvency.
   - Showcase the **120-Filing Research Collection Template** download button.
