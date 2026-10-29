# FinGuard — Corporate Financial Risk & Fraud Detection System

**Zeckathon 2026 — Problem Statement 2: Financial Risk & Fraud Analytics**  
**Author:** 4th-Year B.Tech Computer Science Student  
**Status:** Tested & Verified Prototype (28/28 Unit Tests Passing)  

---

## 1. What the Project Does

**FinGuard** is an early-warning risk intelligence system designed to help financial analysts, credit committees, and auditors identify companies facing financial distress, impending bankruptcy, or potential accounting manipulation **1 to 2 years before formal default**.

### Key Capabilities:
1. **Predictive Solvency Modeling:** Machine learning classifier (Balanced Random Forest) trained on 6,819 corporate filings and 95 financial ratios from the authentic UCI repository.
2. **Forensic & Fundamental Indicators:** Independent calculations of:
   - **Altman Z-Score** (1968 Manufacturing & 1983 Non-Manufacturing models) for structural solvency.
   - **Beneish M-Score** (1999 8-variable model) for earnings and revenue manipulation.
   - **Piotroski F-Score** (2000 9-criteria model) for fundamental financial health.
3. **Operational Policy Triage:**
   - **Top-5% Review Capacity Policy:** Rationing audit reviews under fixed staff bandwidth constraints.
   - **20:1 Cost-Optimal Decision Threshold:** Minimizing total loan portfolio loss where missing a default costs 20x more than a false alarm.
4. **Indian Corporate Distress Benchmark:** Pre-event evaluation of 10 real-world Indian insolvency cases (DHFL, Jet Airways, RCom, Sintex, Bhushan Steel, etc.) alongside 30 sector-matched peers.
5. **Explainability Engine:** TreeSHAP additive feature attributions revealing local positive and negative risk contributors.

> [!NOTE]
> **Educational & Academic Disclaimer:** FinGuard is an educational engineering prototype developed for Zeckathon. It is not an authorized credit rating agency, legal audit report, or investment recommendation. All classifications are probabilistic evaluations for research purposes.

---

## 2. Project Folder Structure

```text
FinGuard/
│
├── app.py                                  # Full 7-page interactive Streamlit dashboard
├── requirements.txt                        # Verified Python dependencies (Python 3.10+)
├── README.md                               # Beginner-friendly setup & project guide
├── .gitignore                              # Git exclusion rules
│
├── src/                                    # Core analytical modules
│   ├── __init__.py                         # Package initialization
│   ├── data_preprocessing.py               # Ingestion, audit & zero-leakage split pipeline
│   ├── financial_ratios.py                 # Math helpers & division-by-zero guards
│   ├── fraud_scores.py                     # Altman Z, Beneish M & Piotroski F models
│   ├── risk_model.py                       # Logistic Regression & Random Forest training
│   ├── threshold_policy.py                 # Top-5% capacity rule & 20:1 cost optimization
│   ├── explainability.py                   # TreeSHAP explainer & heuristic fallback
│   └── case_study.py                       # Indian distress benchmark & template generator
│
├── data/                                   # Data assets
│   ├── raw/
│   │   └── taiwanese_bankruptcy.csv        # Authentic UCI Dataset ID 572 (6,819 rows)
│   ├── processed/
│   │   ├── train.csv                       # 80% Stratified training partition (5,455 rows)
│   │   └── test.csv                        # 20% Held-out test partition (1,364 rows)
│   └── case_studies/
│       ├── indian_distress_metadata.json   # 10 distressed Indian entities + 30 peers
│       ├── indian_distress_evaluation.csv  # Pre-event evaluated distress scores
│       └── case_study_data_collection_template.csv # 120-filing research collection template
│
├── models/                                 # Serialized model artifacts
│   ├── preprocessor.joblib                 # Median Imputer + RobustScaler (fit on train)
│   ├── baseline_logistic_regression.joblib # Baseline Logit model
│   ├── random_forest_risk_model.joblib     # Improved Random Forest ensemble
│   └── evaluation_results.json             # Actual test metrics & feature importances
│
├── tests/                                  # Pytest automated test suites
│   ├── test_data_pipeline.py               # Tests for zero leakage & data hygiene
│   ├── test_financial_scores.py            # Tests for Altman Z, Beneish M, Piotroski F
│   ├── test_risk_model.py                  # Tests for model inference & metric ranges
│   ├── test_threshold_and_explainability.py# Tests for 5% capacity rule & SHAP fallback
│   └── test_case_study.py                  # Tests for Indian cases & collection template
│
├── reports/                                # Generated PDF research report & charts
│   ├── generate_charts.py                  # Pillow script generating high-DPI visual charts
│   ├── generate_report_pdf.py              # ReportLab script producing 8-page PDF report
│   ├── FinGuard_Project_Report.pdf         # 8-Page Selectable-Text Research Report (0.15 MB)
│   ├── chart_confusion_matrix.png          # Visual confusion matrix comparison
│   ├── chart_feature_importance.png        # Top 10 Random Forest risk drivers
│   └── chart_indian_cases.png              # Pre-event Altman Z scores for Indian cases
│
├── presentations/                          # Generated presentation deck
│   ├── generate_presentation_pdf.py        # ReportLab script producing 10-slide deck
│   └── FinGuard_Hackathon_Presentation.pdf # 10-Slide Selectable-Text Presentation (0.02 MB)
│
└── docs/                                   # Complete documentation & presentation support
    ├── data_sources.md                     # Citations, CC BY 4.0 license & time-split note
    ├── methodology.md                      # Technical reference & mathematical formulations
    ├── limitations.md                      # Transparent scope & methodological boundaries
    ├── AI_disclosure.md                    # Transparent disclosure of AI assistance
    ├── presentation_script.md              # 3-5 minute presentation script in easy English
    ├── dashboard_demo_script.md            # Step-by-step click-by-click demo walkthrough
    ├── judge_qa_15.md                      # 15 likely judge questions & concise answers
    └── beginner_explanation.md             # Conceptual explanation for student beginners
```

---

## 3. How to Set Up & Run (Windows Guide)

All commands below work in **Windows PowerShell** or **Windows Command Prompt (cmd.exe)**.

### Step 1: Clone or Navigate to the Project Directory
```powershell
cd C:\Users\priya\OneDrive\Desktop\FineGuard
```

### Step 2: Install Python Dependencies
FinGuard requires Python 3.10+ (tested and verified on Python 3.14.7).
```powershell
pip install -r requirements.txt
```

### Step 3: Run the Data Preprocessing Pipeline
Splits raw data into zero-leakage training and testing sets and fits the RobustScaler:
```powershell
python -m src.data_preprocessing
```
*Output: Saves `data/processed/train.csv`, `data/processed/test.csv`, and `models/preprocessor.joblib`.*

### Step 4: Train & Evaluate the Risk Models
Trains Baseline Logistic Regression and Improved Random Forest, saving metrics to JSON:
```powershell
python -m src.risk_model
```
*Output: Displays real test recall, precision, PR-AUC, and saves models to `models/`.*

### Step 5: Evaluate the Indian Corporate Distress Cases
Calculates pre-event Altman Z-scores and generates the 120-filing data collection template:
```powershell
python -m src.case_study
```

### Step 6: Run the Full Automated Test Suite
Executes all 28 automated unit tests across all modules:
```powershell
python -m pytest tests/ -v
```
*Expected Result: `28 passed in ~20s` (100% pass rate).*

### Step 7: Launch the Interactive Streamlit Web Dashboard
```powershell
python -m streamlit run app.py
```
*Open your web browser and go to: `http://localhost:8501`*

### Step 8: Regenerate the Project Report & Presentation PDFs
```powershell
# 1. Generate high-resolution chart assets:
python reports/generate_charts.py

# 2. Build the 8-page Project Report PDF:
python reports/generate_report_pdf.py

# 3. Build the 10-slide Presentation PDF:
python presentations/generate_presentation_pdf.py
```

---

## 4. Actual Model Performance Summary

Evaluated on the **unseen held-out test partition** ($N = 1,364$, 44 actual defaults):

| Evaluation Metric | Baseline (Logistic Regression) | Improved (Random Forest) | Impact / Analytical Interpretation |
| :--- | :---: | :---: | :--- |
| **Model Type** | L2 Regularized (`class_weight='balanced'`) | Balanced Ensemble (150 trees) | Linear vs Non-linear interaction trees |
| **Accuracy** | 44.72% | **96.19%** | Naive baseline over-flags massively |
| **Precision** | 4.25% (33 / 776) | **42.31%** (22 / 52) | **10x reduction** in false alarms |
| **Recall (Caught Defaults)** | **75.00%** (33 / 44) | **50.00%** (22 / 44) | Default 0.5 threshold (tuneable to 77.3% at $\tau^*=0.20$) |
| **F1-Score** | 0.0805 | **0.4583** | **5.7x improvement** in harmonic balance |
| **ROC-AUC** | 0.6076 | **0.9466** | Exceptional ranking discrimination |
| **PR-AUC (Avg Precision)** | 0.0500 | **0.4610** | **9.2x increase** over baseline |
| **False Positives (Alarms)** | 743 companies | **30 companies** | Saves 713 wasted manual credit audits |
| **Asymmetric Loss ($FP + 20 \cdot FN$)** | 963.0 units | **470.0 units** | **51.2% total cost reduction** |

---

## 5. Common Errors & How to Fix Them

1. **`ModuleNotFoundError: No module named 'src'`**
   - *Cause:* Running scripts from inside the `src/` folder rather than the project root.
   - *Fix:* Always run commands from the project root (`FineGuard/`) using `python -m src.<module_name>` or `python -m pytest tests/`.

2. **`pytest: The term 'pytest' is not recognized`**
   - *Cause:* Python's `Scripts/` folder is not in your Windows system `PATH`.
   - *Fix:* Use `python -m pytest tests/ -v` instead of calling `pytest` directly.

3. **`streamlit: The term 'streamlit' is not recognized`**
   - *Cause:* Same as above (`PATH` variable).
   - *Fix:* Use `python -m streamlit run app.py`.

4. **Port 8501 Already in Use**
   - *Cause:* Another Streamlit process is already running in the background.
   - *Fix:* Run `python -m streamlit run app.py --server.port 8502`.

---

## 6. Citations & Academic References
1. **Liang, D., Lu, C.-J., Tsai, C.-F., & Shih, G.-A. (2016).** *Financial ratio selection for business failure prediction.* Neurocomputing, 173, 383–389. (UCI ML Repository Dataset ID: 572).
2. **Altman, E. I. (1968).** *Financial Ratios, Discriminant Analysis and the Prediction of Corporate Bankruptcy.* The Journal of Finance, 23(4), 589–609.
3. **Altman, E. I. (1983).** *Corporate Financial Distress: A Complete Guide to Predicting, Avoiding, and Dealing with Bankruptcy.* John Wiley & Sons.
4. **Beneish, M. D. (1999).** *The Detection of Earnings Manipulation.* Financial Analysts Journal, 55(5), 24–36.
5. **Piotroski, J. D. (2000).** *Value Investing: The Use of Historical Financial Statement Information to Separate Winners from Losers.* Journal of Accounting Research, 38, 1–41.
6. **Lundberg, S. M., & Lee, S.-I. (2017).** *A Unified Approach to Interpreting Model Predictions (SHAP).* Advances in Neural Information Processing Systems (NeurIPS 30).

