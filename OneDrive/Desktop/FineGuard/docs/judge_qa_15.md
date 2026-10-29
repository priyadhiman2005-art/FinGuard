# FinGuard — 15 Likely Judge Questions & Clear Answers

Prepared for **Zeckathon — PS2: Financial Risk & Fraud Analytics**.

---

### Q1. Why did you use the UCI Taiwanese Bankruptcy dataset instead of a dataset with thousands of public Indian companies?
**Answer:**
"Authentic, labeled financial distress data requires clean historical default definitions. The UCI Taiwanese Bankruptcy dataset (TEJ 1999–2009, 6,819 firms) is an internationally recognized academic benchmark with verified audit outcomes and 95 normalized ratios. To prove real-world Indian relevance, we also constructed an authentic Indian validation benchmark evaluating 10 prominent defaulted entities (like DHFL, Jet Airways, and IL&FS) using pre-event MCA/BSE filings, achieving 100% detection in the Distress Zone."

---

### Q2. Why did your Baseline Logistic Regression have higher Recall (75%) than your Random Forest (50%) at the 0.50 threshold?
**Answer:**
"Because the baseline Logistic Regression used `class_weight='balanced'`, which forced it to flag 776 companies as bankrupt to catch 33 defaults — causing **743 false positives**! That is an unworkable precision of 4.25%. In contrast, Random Forest achieved 0.9466 ROC-AUC and 0.4610 PR-AUC. When we lower the decision threshold on Random Forest to the cost-optimal 0.20 level, its Recall jumps to 77.3% with only 118 false positives instead of 743, cutting total financial loss by over 66%."

---

### Q3. Why is overall accuracy a misleading metric in bankruptcy and fraud prediction?
**Answer:**
"In our dataset, only 3.23% of companies defaulted. A naive or dummy model that predicts every single company is solvent achieves **96.77% accuracy**, but catches zero defaulting firms (0% recall). That's why we focus on Precision-Recall AUC (PR-AUC), Default Recall, and cost-weighted asymmetric error rather than raw accuracy."

---

### Q4. How did you ensure there was zero data leakage in your machine learning pipeline?
**Answer:**
"We performed an 80/20 stratified split first. Our preprocessing pipeline — SimpleImputer with median strategy and RobustScaler — was fitted **strictly on the training partition (`X_train`)**. The test partition (`X_test`) was only transformed using the pre-fitted parameters. No test distribution statistics were ever visible to our model training."

---

### Q5. Why did you use Stratified Shuffle Split instead of a pure sequential Time-Aware split?
**Answer:**
"In the official UCI ML Repository release (Dataset ID: 572), individual company annual timestamps and stock ticker symbols were stripped by the authors to protect corporate anonymity. Since time series dates are absent in the public release, a chronological split is structurally impossible. Stratified shuffle splitting is the methodologically sound alternative that prevents distribution drift while preserving the authentic 3.23% minority class prevalence across both splits."

---

### Q6. What is the fundamental difference between the Altman Z-Score and the Beneish M-Score?
**Answer:**
"They address two entirely different tasks:
- **Altman Z-Score** predicts **insolvency/bankruptcy risk** by measuring working capital, debt coverage, and retained earnings exhaustion.
- **Beneish M-Score** screens for **financial statement manipulation / accounting distortion** by analyzing aggressive accounts receivable growth, margin inflation, and accruals.
A distressed company can have 100% honest books, while an active accounting manipulator can look liquid and profitable on paper."

---

### Q7. Why did you refuse to compute the Beneish M-Score and Piotroski F-Score on single-year inputs?
**Answer:**
"Both scores mathematically require multi-year comparative filings. Beneish M needs prior-year sales, receivables, and depreciation; Piotroski F requires year-over-year deltas for ROA, debt, and current ratios. Many hackathon projects fabricate fake prior-year numbers or assume zeroes. Following our strict hackathon integrity rules, FinGuard outputs `INCOMPLETE DATA` rather than inventing synthetic numbers."

---

### Q8. What is the difference between a Top-5% Review Capacity Policy and a Probability Decision Threshold?
**Answer:**
"A **Review-Capacity Policy** is an *operational budget constraint*: if an audit team only has the physical headcount to investigate 5% of borrowers, we cap flags at $\lfloor N \times 5\% \rfloor$, ranked by risk.
A **Probability Threshold ($\tau$)** is a *risk-appetite decision boundary*: it flags any entity where $P(default) \ge \tau$ to minimize mathematical financial loss, regardless of audit team size."

---

### Q9. How did you model the 20:1 asymmetric cost ratio?
**Answer:**
"In credit risk, a missed default (False Negative) is catastrophic, costing write-offs of principal, whereas a false alarm (False Positive) is merely the administrative cost of a secondary audit. We defined total loss as:
$$\text{Total Loss} = (1.0 \times \text{FP}) + (20.0 \times \text{FN})$$
By evaluating thresholds from 0.01 to 0.99, we found the optimal threshold $\tau^* \approx 0.20$, which minimized loss at 318.0 units (cutting default baseline loss by over 66%)."

---

### Q10. What does SHAP tell an analyst, and what does it NOT tell an analyst?
**Answer:**
"SHAP (TreeExplainer) tells an analyst the exact additive mathematical contribution of each financial ratio to the model's output — for example, showing that high 'Borrowing Dependency' added +18% to a firm's risk score.
However, SHAP does **not** prove legal fraud or intentional management wrongdoing. It shows empirical feature associations within historical data, not causal or legal guilt."

---

### Q11. How does your fallback explainer work if SHAP cannot run?
**Answer:**
"If SHAP is unavailable (due to environment constraints or non-tree models), our system falls back to a deterministic heuristic explainer that computes each feature's deviation from the training population median using the RobustScaler's Interquartile Range (IQR). It identifies outlier ratios that push the company away from normal solvency bounds."

---

### Q12. How did you choose the 30 sector-matched peers for the 10 Indian distressed companies?
**Answer:**
"Each distressed company was matched with 3 active domestic peers in the same 3-digit industry sector with comparable core business models: for instance, DHFL was matched with LIC Housing Finance, HDFC, and PNB Housing; Jet Airways with IndiGo, SpiceJet, and GoAir; and Bhushan Steel with Tata Steel, JSW Steel, and SAIL. We generated an open 120-filing data collection template for full 3-year sequential research."

---

### Q13. Why did you use RobustScaler instead of StandardScaler or MinMaxScaler?
**Answer:**
"Financial ratios suffer from extreme, heavy-tailed outliers — for example, companies with near-zero equity can have leverage ratios in the thousands. `StandardScaler` uses the mean and variance, which are distorted by outliers. `MinMaxScaler` compresses 99% of data into a tiny band. `RobustScaler` centers using the median and scales using the Interquartile Range (IQR), making it immune to extreme financial ratio spikes."

---

### Q14. What are the key limitations of your current prototype?
**Answer:**
"First, it operates on structured numerical ratios and does not yet parse unstructured qualitative text (like auditor resignation notes or whistleblower complaints via financial NLP). Second, it focuses on annual corporate filings rather than macroeconomic shocks (like sudden interest rate hikes or FX volatility)."

---

### Q15. If a bank deployed FinGuard tomorrow, what would be the immediate business impact?
**Answer:**
"Under a standard 5% audit capacity budget, FinGuard allows the credit committee to catch **over 54% of all corporate insolvencies** while reviewing only 1 out of every 20 loan accounts. On an unconstrained basis, tuning the model to our 20:1 cost-optimal threshold cuts overall expected portfolio loan loss by **over 51%** compared to standard credit scoring models."

