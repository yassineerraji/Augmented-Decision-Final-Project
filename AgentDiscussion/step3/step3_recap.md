# Step 3 — Model Selection and Decision Tree Tuning (recap)

**Notebook:** section 3 of `notebooks/bankruptcy_prediction.ipynb`. The whole notebook runs end to end in about 4 minutes; tuning M3 takes about 2 of them. It is saved with its outputs, and Step 3 uses the training set only.

## What was built

| Section | Content |
|---|---|
| Setup | New imports added to the single imports cell |
| 3.1 Decision rule and metric | Leaf share as $\hat\eta(x)$, flag when ≥ 1/11, empirical-risk formula (LaTeX); decision on threshold vs class weights; `avg_cost` and `cost_scorer` |
| 3.2 Candidates and grid | Decisions on the grid, the 4 candidates and the selection rule; `tree_grid` |
| 3.3 Cross-validated tuning | M0, M1, M2, M3, each with its own cell; M2 validation curve (2 panels) |
| 3.4 Model comparison | Comparison table, bar chart with ±1 standard-error bars, rule table, decision cell |
| 3.5 Final model | `final_model` frozen; description (variables selected and used, depth, leaves) |
| 3.6 Takeaways | 6 bullets |

Section 3 adds 13 code cells and 5 decision cells.

## Key results (identical to the plan's preview)

| Candidate | CV cost per firm | SE | Depth | Leaf | `C` | Variables |
|---|---|---|---|---|---|---|
| M0 never flag | 0.3226 | 0.0016 | – | – | – | 0 |
| M1 all features | 0.1630 | 0.0090 | 4 | 120 | – | 94 |
| **M2 LASSO, `C` fixed** | **0.1512** | 0.0077 | 4 | 120 | 0.178 | 43 |
| M3 LASSO, `C` joint | 0.1483 | 0.0087 | 3 | 10 | 0.01 | 7 |

- **M2 is kept by the agreed rule.**
  - M3's gain is 0.003, well below its standard error of 0.009.
  - M1 is worse by 0.012, more than one standard error, so the variable selection helps.
- **Final model:** the LASSO keeps 43 variables, followed by a depth-4 tree with **9 leaves that uses only 8 variables**. Those 8 are profitability (EPS, continuous interest rate), debt and its cost (borrowing dependency, interest-bearing debt rate, interest coverage), growth (net value growth) and activity (inventory/working capital, quick asset turnover).
- **Validation curve:**
  - With leaves of 1 firm, training cost falls to 0 as depth grows, while CV cost rises from 0.17 to 0.23. That is clear overfitting.
  - With leaves of at least 120 firms, the gap between training and CV cost stays small, and depth 4 is best.

## Differences from the plan

1. **M2's grid states `C` explicitly** (`[best_C]`) instead of relying on the value preset inside `selector`. This is more robust and makes M2 and M3 directly parallel, since M3 just swaps in `C_grid[4:11]`.
2. **"Apply the rule and keep the final model" became two cells** (the rule table, then the freeze), to keep one task per cell. That is why there are 13 code cells instead of 12.
3. **Section 3.1 shows the metric as an empirical-risk formula**, and `avg_cost` computes exactly that: the mean of the per-firm losses.
4. **Two pandas 3 adjustments:**
   - In the validation-curve plot, depth "None" is converted to the label "no limit" before plotting.
   - The comparison table uses `convert_dtypes()`, so depths and leaf sizes display as whole numbers.

## Carried into Step 4

- **What Step 4 uses:**
  - `final_model`, frozen: a `FixedThresholdClassifier` whose `predict()` returns the flag decision.
  - `avg_cost`.
  - The never-flag baseline, for comparison on the test set.
- **First use of the test set:**
  - test cost compared with the baseline
  - confusion matrix, recall and precision
  - drawing the tree for interpretation
- **Cost-ratio sensitivity (5 and 20):** `final_model.set_params(threshold=...)` changes the threshold (1/6, 1/21) **without refitting**.
- **Limitations to discuss:**
  - no time-based split
  - the costs are stipulated
  - CV noise (SE about 0.008, with only about 35 bankruptcies per fold)
  - no nested CV for the M2 vs M3 comparison
  - moderate stability of the LASSO selection
