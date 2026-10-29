# FinGuard — 3 to 5 Minute Hackathon Presentation Script

**Target Time:** 3 minutes 45 seconds  
**Tone:** Confident, humble, technically precise, beginner-friendly  
**Speaker:** 4th-Year B.Tech Computer Science Student  

---

### [Slide 1: Title & Introduction — 0:00 to 0:30]
"Good morning, respected judges and fellow participants. My name is [Your Name], a 4th-year Computer Science student. Today, I am proud to present **FinGuard: Corporate Financial Risk and Fraud Detection System**, built for Problem Statement 2: Financial Risk and Fraud Analytics.

In the corporate world, sudden bankruptcies and accounting scandals — like DHFL or IL&FS in India — destroy billions of dollars in investor wealth and cause severe bad loans for banking institutions. FinGuard is an early-warning risk intelligence system designed to flag distressed companies and forensic accounting anomalies *before* they turn into catastrophic corporate collapses."

---

### [Slides 2 & 3: The Problem & Why It Matters — 0:30 to 1:15]
"When we started analyzing this problem, we discovered three critical realities that traditional machine learning projects often overlook:

First, **extreme class imbalance**: in real-world corporate portfolios, defaulting companies are rare — only about 3.2% in our authentic benchmark. A naive model that simply predicts 'healthy' for every company gets 96.8% accuracy while missing 100% of defaults. Accuracy is a deceptive metric here.

Second, **asymmetric financial risk**: in commercial lending, missing a defaulting borrower is vastly more costly than auditing a healthy firm. Specifically, a missed default costs up to 20 times more than a false alarm.

Third, **bankruptcy is not the same as fraud**: a struggling company can default with completely honest accounting, while an active fraudster can look profitable and liquid on paper. They require separate, specialized screening tools."

---

### [Slides 4 & 5: FinGuard Solution & System Architecture — 1:15 to 2:00]
"To solve this, we engineered FinGuard with a four-layer architecture:

1. **Zero-Leakage Data Pipeline**: We used the authentic UCI Taiwanese Bankruptcy benchmark of 6,819 corporate filings across 95 financial ratios. We split into 80% train and 20% test, fitting our imputer and scaler *strictly* on training data.
2. **Dual-Model Predictive Core**: We compared a class-weighted Logistic Regression baseline with a Balanced Random Forest ensemble.
3. **Classical Forensic Engine**: We implemented the Altman Z-Score for solvency, the 8-variable Beneish M-Score for earnings manipulation, and the 9-point Piotroski F-Score for fundamental health — with a strict rule: *no fake scores when data is missing*.
4. **Operational Policy Engine**: We built a realistic Top-5% Review Capacity Policy and a 20:1 cost-optimal threshold optimizer."

---

### [Slides 6 & 7: Actual Results & Risk Drivers — 2:00 to 2:50]
"Let’s examine our actual, verified results on the held-out test set of 1,364 unseen companies:

Our baseline Logistic Regression caught 75% of defaults, but it generated 743 false alarms — an audit team would drown in noise.

Our improved **Random Forest model achieved a phenomenal 0.9466 ROC-AUC and 0.4610 PR-AUC**, which is 9.2 times higher than the baseline. Most importantly, it reduced false alarms from 743 down to just 30, and **cut our total cost-weighted financial loss by 51.2%**.

Using SHAP explainability, our model revealed the top real-world risk drivers: heavy borrowing dependency, collapsing return on assets, persistent negative EPS, and extreme debt-to-net-worth ratios."

---

### [Slide 8: Indian Case Studies & Dashboard Demo — 2:50 to 3:30]
"To test cross-border robustness, we constructed an empirical case study of **10 prominent Indian corporate defaults** — including DHFL, Jet Airways, RCom, and Bhushan Steel — alongside 30 sector-matched peers. Using only pre-event financial statements from MCA and BSE filings, FinGuard successfully identified **10 out of 10 distressed Indian entities in the Distress Zone** 1 to 2 years before official NCLT insolvency proceedings.

Our interactive Streamlit dashboard allows risk analysts to input financial statements, simulate audit capacity budgets, explore SHAP waterfall plots, and download audit CSV reports."

---

### [Slides 9 & 10: Limitations & Conclusion — 3:30 to 4:00]
"In the spirit of scientific honesty, we document our limitations: the model currently evaluates structured financial statements and does not yet ingest unstructured auditor resignation notes or macroeconomic interest rate shocks. Furthermore, our SHAP attributions represent statistical correlations, not legal proof of fraud.

In conclusion, FinGuard proves that combining class-balanced machine learning with classical forensic indices and operational capacity constraints creates a practical, high-impact risk early-warning system.

Thank you so much. I welcome your questions!"

