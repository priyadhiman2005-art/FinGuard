# FinGuard — Methodological Limitations & Future Scope

## 1. Educational & Prototype Boundaries
- **Educational Context:** FinGuard is an educational engineering prototype built for Zeckathon (PS2: Financial Risk & Fraud Analytics). It is not an authorized credit rating agency, legal audit report, or investment recommendation.
- **Probabilistic Nature:** Model outputs are statistical estimates of historical vulnerability and do not guarantee future corporate events.

## 2. Dataset Limitations
- **Omission of Annual Timestamps in Public Release:** While the underlying TEJ data covers 1999–2009, individual record rows in the public UCI ML Repository release omit discrete annual timestamps and ticker symbols to preserve corporate anonymity. A rolling time-aware split is structurally impossible without dates; hence, Stratified Shuffle Splitting was used to maintain the exact 3.23% default rate across partitions.
- **Cross-Border GAAP Variations:** The primary dataset is compiled under Taiwan Economic Journal GAAP standards. While accounting ratios are largely normalized, cross-border nuances exist between Indian Ind-AS, US GAAP, and IFRS.

## 3. Scope Distinction: Solvency vs Fraud
- **Separate Constructs:** Bankruptcy prediction (liquidity exhaustion) is structurally distinct from accounting fraud (intentional misrepresentation). A distressed company may default with transparent accounting, while an aggressive accounting manipulator may appear liquid and solvent on paper.

## 4. Explainability & Non-Causality Disclosure
- **Statistical Correlation vs Legal Proof:** SHAP attributions and heuristic score breakdowns reflect mathematical feature associations learned from historical financial ratios. They do NOT constitute forensic verification, statutory evidence, or legal proof of intentional management fraud or regulatory wrongdoing.

## 5. Future Engineering Scope
- **Financial NLP:** Ingest qualitative text from Annual Reports (MD&A sections, auditor resignation notes, qualified audit opinions).
- **Sequential Temporal Models:** Train LSTM or Transformer networks on multi-year longitudinal filing sequences.
- **Macroeconomic Stress Testing:** Integrate interest rate cycles, inflation, and sector supply chain shocks.

