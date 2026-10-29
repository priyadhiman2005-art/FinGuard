# FinGuard Methodology & Technical Reference

## 1. Data Ingestion & Hygiene
- **Primary Source:** UCI Machine Learning Repository Dataset ID 572 (*Taiwanese Bankruptcy Prediction*).
- **Instances:** 6,819 annual corporate filings across 95 normalized financial attributes.
- **Hygiene Audit:** Cleaned leading whitespace in column names, verified zero duplicate rows, zero missing cells, and zero infinite values.
- **Leakage Prevention:** Stratified 80/20 train/test split. Preprocessing (`SimpleImputer(strategy='median')` and `RobustScaler()`) is fitted strictly on `X_train` ($N=5,455$) and applied to `X_test` ($N=1,364$).

## 2. Predictive Modeling & Evaluation
- **Baseline Model:** Logistic Regression with L2 regularization, `class_weight='balanced'`, $C=0.1$.
- **Improved Model:** Random Forest Classifier with 150 estimators, `max_depth=12`, `min_samples_split=5`, `class_weight='balanced_subsample'`.
- **Metrics Evaluated:** Accuracy, Precision, Recall, F1-Score, ROC-AUC, PR-AUC (Average Precision), and Confusion Matrix.
- **Key Results on Unseen Test Data:**
  - Random Forest achieved **0.9466 ROC-AUC** and **0.4610 PR-AUC** (vs 0.0500 baseline PR-AUC).
  - Reduced False Positives from 743 down to 30.
  - Cut asymmetric financial loss by **51.2%**.

## 3. Forensic & Fundamental Risk Indicators
- **Altman Z-Score:**
  - Public Manufacturing (1968): $Z = 1.2 X_1 + 1.4 X_2 + 3.3 X_3 + 0.6 X_4 + 0.999 X_5$. Safe $>2.99$, Grey $1.81-2.99$, Distress $<1.81$.
  - Non-Manufacturing (1983 Double-Prime): $Z'' = 6.56 X_1 + 3.26 X_2 + 6.72 X_3 + 1.05 X_4$. Safe $>2.60$, Grey $1.10-2.60$, Distress $<1.10$.
- **Beneish M-Score (1999):** 8-variable earnings manipulation model with standard threshold of $-1.78$.
- **Piotroski F-Score (2000):** 9-point fundamental financial strength score across Profitability, Leverage/Liquidity, and Operating Efficiency.
- **Strict Validation Rule:** If any required input statement is absent, returns `INCOMPLETE_DATA` and refuses to synthesize fake scores.

## 4. Operational Policies
- **Top-5% Review Capacity Policy:** Budget constraint capping audit reviews strictly at $\lfloor N \times 5\% \rfloor$ using stable tie-breaking and small-dataset protection. Catches 54.5% of total insolvencies while examining only 5% of the portfolio.
- **Cost-Sensitive Threshold Optimization:** Asymmetric loss function: $\text{Loss} = (1.0 \times \text{FP}) + (20.0 \times \text{FN})$. Cost-optimal threshold $\tau^* \approx 0.20$ minimizes loss to 318.0 units (vs 963.0 baseline).

## 5. Indian Corporate Distress Benchmark
- Evaluated 10 distressed Indian entities (DHFL, Jet Airways, RCom, Sintex, Bhushan Steel, Cox & Kings, Amtek Auto, Videocon, IL&FS, ABG Shipyard) alongside 30 sector-matched peers.
- All figures drawn from authentic MCA, BSE, NSE, and IBBI filings strictly 1–2 years prior to insolvency. 100% of cases were detected in the Distress Zone pre-event.

