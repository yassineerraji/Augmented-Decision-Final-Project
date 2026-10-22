# Step 1 — Problem Formulation & EDA (recap)

**Notebook:** `notebooks/bankruptcy_prediction.ipynb`, sections 0 and 1. It runs end to end on the `.venv` kernel and is saved with its outputs.

## What was built

| Section | Content |
|---|---|
| Title | Short introduction, dataset citation, outline of the 4 steps |
| 0. Setup | Imports; constants `SEED = 42`, `C_FN = 10`, `C_FP = 1`, `THRESHOLD = 1/11` |
| 1.1 Problem formulation | Target, inputs, decision, loss table, Bayes rule, metric, baseline, plus 2 assumption cells (costs; no leakage and independent firms) |
| 1.2 Loading and integrity | Load and clean column names; shape; missing values and duplicates; class counts and bar plot; drop the constant column; separate X and y |
| 1.3 Exploratory analysis | Values above 1; Spearman correlation matrix (heatmap) and correlated pairs; AUC of each feature alone; boxplots of the top 4 features |
| 1.4 Train/test split | Stratified 80/20 split and a check of both sets |
| 1.5 Takeaways | 5 bullets that summarise the step |

There are 18 code cells and 7 blockquote cells (decisions and assumptions), plus one `**Observation:**` line after each output that needs interpreting.

## Key results

- **Data quality:** 6,819 firms, no missing values, no duplicate rows. `Net Income Flag` has the same value everywhere and is dropped, which leaves **94 features**.
- **Class imbalance:** 220 bankrupt firms (3.2%). The "never flag" baseline costs about **0.32 per firm**.
- **Extreme values:** 24 features mix values in [0, 1] with values between 6e5 and 1e10, with nothing in between. A few firms are affected in some features; 6,017 firms are affected in `Total Asset Growth Rate`.
- **Redundancy:** 50 pairs of features have Spearman |ρ| > 0.95. These pairs involve 47 of the 94 features, and 13 of the pairs have |ρ| > 0.999. The heatmap shows blocks of related ratios: profitability, per-share values, growth, leverage and cash flow.
- **Signal:** the strongest single predictors are profitability ratios (EPS, net income / assets, ROA), with AUC between 0.86 and 0.89. Bankrupt firms clearly score lower, but the two classes still overlap.
- **Split:** 5,455 firms for training (176 bankrupt) and 1,364 for testing (44 bankrupt).

## Differences from the plan

1. **Exploration on the full dataset.** I followed your edit in section 5 of the plan. Two places in the plan still say "training set only": §2 item 4 and the §3 outline. I treated your section 5 edit as the decision.
2. **Section order is now 1.3 EDA → 1.4 split** (the plan had split → EDA). Since the exploration uses the full data, splitting before it would serve no purpose, and the notebook reads more naturally this way. Tell me if you want the original order back.
3. **The "find constant columns, then drop them" step is two cells**, with the decision cell in between. This follows the "one task per cell" rule.
4. **Separating X and y has its own cell at the end of 1.2**, so the exploration and the split share the same `X` and `y`.
5. **The boxplots hide outliers** (`showfliers=False`, and the plot title says so). With outliers shown, the boxes were unreadable.

## Changes after your review

- **Added a correlation matrix** (heatmap of all 94 features, in column order) to section 1.3, just before the list of correlated pairs.
- **Switched from Pearson to Spearman correlation**, for the heatmap and for the list of pairs. A decision cell in the notebook records this.
  - Why: Pearson missed ratios that are inverses of each other, such as `Current Ratio` and `Current Liability to Current Assets` (ρ = 0.999), and it was distorted by the extreme values.
  - Effect: the count of redundant pairs went from 23 to 50.
  - Spearman measures order, which is all a tree uses.
  - To go back to Pearson, change `method="spearman"` in a single cell.
- **Wrote the math in LaTeX** (`$...$`) in every markdown cell that contains math. In 1.1, the decision rule and the cost metric are now displayed equations, and the rule includes its one-line derivation.
- **Corrected the cell counts** in this recap. The first version said 21 code cells and 7 decision cells; the real numbers were 16 and 6.

## Carried into Step 2

- The 24 features with extreme values need treatment before any linear or LASSO selector. That treatment must be fitted inside the cross-validation folds.
- Selection and tuning only see `X_train` and `y_train`. `X_test` and `y_test` are not touched until Step 4.
- New imports will be added to the single Setup cell rather than scattered through the notebook.
