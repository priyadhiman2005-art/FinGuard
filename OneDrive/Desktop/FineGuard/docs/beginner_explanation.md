# FinGuard — Beginner-Friendly Project Explanation

*Written for a student who wants to understand and explain every component of FinGuard.*

---

## 1. What Does FinGuard Do in Simple Words?
Imagine a bank lending money to 1,000 different companies. Most companies will pay their loans back on time, but 30 or 40 might run out of cash and go bankrupt. 

If the bank waits until a company actually defaults, it loses millions of dollars. **FinGuard is an intelligent software system that acts like an early medical check-up for companies.** It looks at their accounting numbers (like how much debt they have, how much profit they make, and how much cash they have in the bank) and warns the bank 1 to 2 years before disaster happens.

---

## 2. Why Can't We Just Use Normal Accuracy to Judge Our AI?
In our dataset of 6,819 companies:
- 6,599 companies are healthy (solvent).
- Only 220 companies went bankrupt.

If you write a simple 2-line program that always guesses "Healthy" without looking at any numbers:
- It gets 6,599 right out of 6,819.
- **Its accuracy is 96.8%!**

Sounds amazing, right? But it caught **zero bankrupt companies**. In the real world, that bank would go out of business.

That is why we use:
- **Recall:** Out of all the companies that actually went bankrupt, what percentage did we catch?
- **PR-AUC (Precision-Recall Area Under Curve):** A fair score that measures how good the model is at catching rare events without drowning the bank in false alarms.

---

## 3. What is "Data Leakage" and How Did We Prevent It?
Data leakage is when your machine learning model accidentally peeks at the test questions before taking the test.

For example, if you calculate the average debt of ALL companies (both training and test) and use that to fill in missing values, your training process now contains secret information about the test data.

**How FinGuard prevented it:**
1. We split the data into 80% Training and 20% Testing FIRST.
2. We calculated the median and scaling factors **ONLY on the 80% Training data**.
3. We used those saved training rules to scale the 20% Test data. Zero cheating!

---

## 4. The Four Major Formulas Used in FinGuard

### A. Random Forest Classifier (Machine Learning)
- Instead of relying on a single decision, Random Forest builds **150 different decision trees**.
- Each tree votes on whether a company is at risk.
- We told the trees: *"Bankrupt companies are rare, so pay 30 times more attention when you see one!"* (This is called `class_weight='balanced'`).

### B. Altman Z-Score (Solvency Risk)
- Invented by NYU Professor Edward Altman in 1968.
- Combines 5 ratios: Working Capital, Retained Earnings, EBIT, Market Equity, and Sales.
- If $Z < 1.81$ (or $Z'' < 1.10$ for service firms), the company is in the **Distress Zone** (high risk of bankruptcy within 2 years).

### C. Beneish M-Score (Accounting Manipulation / Fraud Risk)
- Invented by Professor Messod Beneish in 1999.
- It caught Enron before it collapsed!
- It checks if accounts receivables are growing way faster than real sales (a sign of fake revenue), or if expenses are being hidden as assets.
- If $M > -1.78$, the company is flagged as a **Likely Manipulator**.

### D. Piotroski F-Score (Fundamental Health)
- Invented by Stanford Professor Joseph Piotroski in 2000.
- Gives a company 1 point for each of 9 fundamental checks (e.g., positive cash flow, lower debt, higher gross margins).
- A score of $8 - 9$ is very strong; a score of $0 - 4$ is weak.

---

## 5. What is the 20:1 Cost Ratio?
In lending:
- **False Positive (False Alarm):** You flag a healthy company. A credit analyst spends 2 hours doing a manual review. Cost: ~$1,000 in staff time.
- **False Negative (Missed Default):** You miss a failing company. The company defaults on a $500,000 loan. Cost: ~$100,000.

Missing a default is roughly **20 times more expensive** than a false alarm. That is why our threshold optimization looks for the cutoff that minimizes:
$$\text{Cost} = (1 \times \text{False Alarms}) + (20 \times \text{Missed Defaults})$$

---

## 6. What is SHAP?
Machine learning models are often called "black boxes" because people don't know why the computer made a decision.

**SHAP (SHapley Additive exPlanations)** opens the black box. For any company, SHAP draws a chart showing:
- *Red bars:* Things that pushed the risk UP (e.g., debt increased by 40%).
- *Green bars:* Things that pulled the risk DOWN (e.g., cash reserves are still high).

It allows an analyst to explain the prediction in plain English to the credit committee.

