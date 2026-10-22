# Step 1 — Problem Formulation & EDA (plan)

## 1. Problem formulation

| Element | Proposal |
|---|---|
| **Target** | `Bankrupt?` (1 = the firm went bankrupt under Taiwan Stock Exchange rules, 0 = it did not) |
| **Inputs** | 95 financial ratios, assumed to be known *before* the outcome (so no leakage) |
| **Decision supported** | A credit analyst decides whether to **flag** a firm as high-risk (deny or reprice credit, start a closer review) or **not flag** it |
| **Actions** | a = 1 flag, a = 0 do not flag |

**Loss table (Lecture 1)**. This is an assumption, not an estimate:

| | Healthy (Y = 0) | Bankrupt (Y = 1) |
|---|---|---|
| Not flag (a = 0) | 0 | **C_FN = 10** (credit loss) |
| Flag (a = 1) | **C_FP = 1** (unnecessary review, lost client) | 0 |

- **Bayes decision rule:** flag a firm when P(bankrupt | x) ≥ C_FP / (C_FP + C_FN) = **1/11 ≈ 0.09**.
- **Primary metric:** average misclassification cost per firm, (10·FN + 1·FP) / n. This is the empirical risk under the loss table, so lower is better.
- **Secondary metrics:** the confusion matrix, recall (share of bankruptcies caught) and precision (share of flags that are real bankruptcies).
- **Why not accuracy:** only 3.2% of firms are bankrupt, so "never flag" already reaches 96.8% accuracy.
- **Reference baseline:** "never flag" (the majority class) costs about 10 × 0.032 ≈ **0.32 per firm**. Every model has to beat this.
- **Sensitivity:** in Step 4 we will re-run the evaluation with cost ratios of 5 and 20, because 10 is a stated assumption.

## 2. Assumptions and decisions (each one becomes a short markdown cell)

1. **The data has no firm ID and no year, so firms are treated as independent draws.** A time-based split is impossible, so we use a random stratified split. This becomes a stated limitation in Step 4.
2. **Drop `Net Income Flag`.** It has the same value in every row, so it carries no information.
3. **Hold out a stratified 80/20 train/test split right after loading** (`random_state = 42`). That gives a test set of about 1,364 firms, about 44 of them bankrupt. The test set stays locked until Step 4.
4. **Run the EDA on the training set only**, so that no later decision uses test information (Lecture 2: "condition on every choice made using training data").
5. **Leave the raw values unchanged in Step 1.** 24 columns mix values in [0, 1] with values between about 6e5 and 1e10. Some columns have only a few such values; for others it is most rows (e.g. `Total Asset Growth Rate`: 6,017 of 6,819). These values look like an encoding artifact. A decision tree only depends on the order of the values, so it is unaffected. A linear selector (LASSO) is affected, so its treatment is decided in Step 2 and fitted inside the cross-validation folds.

## 3. Notebook structure (applies to the whole notebook)

```
# Taiwanese Bankruptcy Prediction        ← title, dataset citation, 4-step overview
## 0. Setup                              ← imports, constants (SEED, C_FN, C_FP, THRESHOLD)
## 1. Problem Formulation & EDA
### 1.1 Problem formulation
### 1.2 Data loading and integrity checks
### 1.3 Train/test split
### 1.4 Exploratory analysis (training set)
### 1.5 Step 1 takeaways
## 2. Variable Selection                 ← same sub-structure, defined in Step 2's plan
...
```

- Decisions and assumptions are blockquotes: `> **Decision:** …` or `> **Assumption:** …`.
- Findings are one-line `**Observation:** …` cells placed after the output they describe.
- Dataset citation: UCI ML Repository, *Taiwanese Bankruptcy Prediction*, DOI 10.24432/C5004D. Original study: Liang et al. (2016), *European Journal of Operational Research* 252(2).

## 4. Planned code cells (one task each)

| # | Cell |
|---|---|
| 1 | Imports |
| 2 | Constants: `SEED`, `C_FN`, `C_FP`, `THRESHOLD` |
| 3 | Load the CSV and strip the leading spaces from column names |
| 4 | Shape and first rows |
| 5 | Missing values and duplicate rows |
| 6 | Target counts and proportions |
| 7 | Bar plot of the target |
| 8 | Find the constant columns, then drop them |
| 9 | Split into X and y, then stratified train/test split |
| 10 | Check the bankrupt rate in train and test |
| 11 | Scale check: columns with values > 1 (count per column) |
| 12 | Redundancy: number of feature pairs with \|r\| > 0.95, plus the top pairs |
| 13 | Univariate signal: ROC-AUC of each feature alone, top 10 |
| 14 | Boxplots of the 4 strongest features by class |

What I expect to find, from a first look: 23 feature pairs with |r| > 0.95, several of them exact duplicates (r = 1.00). Profitability ratios (EPS, ROA, net income / assets) separate the classes best on their own, with AUC around 0.86–0.89. Both points motivate Step 2.

## 5. Points for you to confirm or change

- **Cost ratio C_FN : C_FP = 10 : 1.** Alternatives: about 30 : 1, which roughly corresponds to balancing the two classes, or a non-cost metric such as F1 or recall at a fixed precision.
- **Test size of 20%.** Moving to 25% gives about 55 bankrupt firms in the test set instead of 44.
- **EDA on the full dataset.

## Environment

The project has a `.venv` created with `uv` (Python 3.12), and the dependencies are pinned in `requirements.txt`. The notebook will be saved with its outputs, at `notebooks/bankruptcy_prediction.ipynb`.
