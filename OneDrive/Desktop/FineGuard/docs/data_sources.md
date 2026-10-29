# FinGuard Data Sources & Benchmark Documentation

## 1. Primary Benchmark Dataset: Taiwanese Bankruptcy Prediction

### Source Information
- **Repository**: [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/572/taiwanese+bankruptcy+prediction)
- **Dataset ID**: 572
- **Original Source**: Taiwan Economic Journal (TEJ), collected over the years 1999 to 2009.
- **Academic Citation**:
  > Liang, D., Lu, C.-J., Tsai, C.-F., & Shih, G.-A. (2016). *Financial ratio selection for business failure prediction*. Neurocomputing, 173, 383–389. DOI: [10.1016/j.neucom.2015.08.064](https://doi.org/10.1016/j.neucom.2015.08.064)
- **License**: Creative Commons Attribution 4.0 International ([CC BY 4.0](https://creativecommons.org/licenses/by/4.0/))
- **Access Date**: October 29, 2026
- **Format**: CSV, 6,819 instances, 96 attributes (95 financial features + 1 binary target).

---

## 2. Target Variable & Class Distribution

The target variable is binary: `Bankrupt?`:
- `0` (Negative Class): Non-bankrupt / solvent company. Total: **6,599 instances (96.77%)**
- `1` (Positive Class): Bankrupt / financially distressed company. Total: **220 instances (3.23%)**
- **Imbalance Ratio**: Approximately **29.99 : 1** (For every 30 solvent firms, there is only 1 defaulting firm).

### Practical Implications for Machine Learning:
1. **Accuracy is a Deceptive Metric**: A naive dummy classifier predicting all zeroes achieves 96.77% accuracy while failing to detect 100% of defaulting companies.
2. **Prioritization of Recall & PR-AUC**: In financial risk analysis, missing a bankruptcy (False Negative) is catastrophic, whereas requesting a secondary audit on a healthy firm (False Positive) is merely inconvenient.
3. **Class Weighting & Stratified Sampling**: Models must incorporate inverse class frequency penalties or cost-sensitive objectives.

---

## 3. Financial Feature Categories

The 95 features represent normalized financial ratios covering four major dimensions of corporate accounting:

### A. Profitability & Return Ratios
- `ROA(C) before interest and depreciation before interest`: Operating return on total assets before debt service.
- `ROA(A) before interest and % after tax`: Effective operating return after taxes.
- `ROA(B) before interest and depreciation after tax`: Net cash generation efficiency relative to total capital.
- `Operating Gross Margin`, `Realized Sales Gross Margin`: Product margin health and pricing power.
- `Operating Profit Rate`, `Pre-tax net Interest Rate`, `After-tax net Interest Rate`: Operating and bottom-line margin strength.

### B. Solvency, Leverage & Debt Service
- `Debt ratio %`: Total liabilities divided by total assets. High values indicate elevated structural leverage.
- `Current Liability to Assets`: Near-term obligations relative to total resource base.
- `Borrowing dependency`: Reliance on external financial debt to fund daily operations.
- `Interest Coverage Ratio (Interest expense to EBIT)`: Capacity of operating earnings to service debt interest payments.

### C. Liquidity & Working Capital
- `Current Ratio`: Current assets divided by current liabilities. Standard measure of short-term liquidity.
- `Quick Ratio`: Liquid assets (excluding illiquid inventory) relative to short-term liabilities.
- `Cash / Total Assets`: Cash reserves cushion against liquidity shocks.
- `Working Capital to Total Assets`: Net liquid capital available for operational stability.

### D. Asset Turnover & Operating Efficiency
- `Inventory Turnover Rate (times)`: Efficiency of inventory conversion into revenue.
- `Fixed Assets Turnover Frequency`: Sales generated per dollar of fixed capital invested.
- `Total Asset Turnover`: Overall velocity of business assets.
- `Cash Turnover Rate`: Velocity of cash conversions.

---

## 4. Methodological Limitations & Integrity Disclosures

### Lack of Explicit Fiscal-Year Timestamps
- **Limitation**: While the underlying TEJ data spans 1999–2009, individual record rows in the public UCI release lack discrete annual timestamps or individual company stock tickers to preserve anonymity.
- **Handling**: A pure rolling time-split is structurally impossible without company identifiers. Therefore, we utilize **Stratified Shuffle Splitting** (80% train, 20% test) to prevent distribution shift while preserving the exact 3.23% minority class prevalence across both splits.
- **Zero Leakage**: All imputations (median) and scalings (`RobustScaler`) are fitted strictly on the training partition ($N = 5,455$) and transformed onto the test partition ($N = 1,364$).
