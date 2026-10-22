# Step 4 — Evaluation of the Final Model (plan)

This step is the **first and only use of the test set** (1,364 firms, 44 bankrupt). Following Lecture 2, the frozen final model from Step 3 is evaluated once, and nothing is tuned or re-chosen afterwards.

**I wrote this plan without computing any test-set result.** That way, the choice of what to report cannot be influenced by the results. The previews below come from the training set only.

## 1. Decisions (each one becomes a short markdown cell)

1. **Only the final model (M2) and the "never flag" baseline are scored on the test set.** M1 and M3 are not.
   - Reporting the test scores of rejected candidates invites choosing again on the test set, which would make the test score part of model selection (Lecture 2).
2. **The test results are reported as:**
   - the average cost per firm (primary metric)
   - recall, precision and the number of flagged firms
   - the confusion matrix
   - accuracy, shown only to illustrate why it was rejected in 1.1
3. **Uncertainty: a bootstrap confidence interval, because Lecture 2's Hoeffding bound is too loose here.**
   - The loss lies in [0, 10] and there are 1,364 test firms. Hoeffding then gives a margin of **±0.37** at 95%. That is larger than the gap we want to measure (≈ 0.32 vs ≈ 0.15), so the bound is valid but uninformative (Lecture 2: "bounds larger than the loss range are valid but uninformative"). It is shown in one line.
   - Instead: a **95% percentile bootstrap** with 1,000 resamples of the test firms, keeping the predictions fixed. The interval is computed for the model's cost, the baseline's cost and their **paired difference**.
4. **Sensitivity to the cost ratio (announced in 1.1):** $C_{FN}/C_{FP} \in \{5, 10, 20\}$.
   - For each ratio $r$, the decision threshold becomes $1/(1+r)$ (Bayes rule). The tree is **not retrained**.
   - Each version is compared with the baseline under the same ratio.
   - In code, the probabilities are computed once (`predict_proba`) and thresholded per ratio, so `final_model` is never modified.
5. **Switching points:** for each leaf, the cost ratio at which its decision flips, $r^* = (1-\hat\eta)/\hat\eta$, computed from its training share $\hat\eta$. This explains the sensitivity results directly from the loss table (Lecture 1, "different costs can reverse the decision").
6. **Interpretation:**
   - **Tree diagram.** The final tree is drawn with `plot_tree`, in raw ratio units, with node ids.
   - **Leaf table.** Each leaf gets its training firms, its bankruptcy share and its decision (flag if the share is ≥ 1/11).
   - **Why the table is needed.** `plot_tree` labels each leaf with its *majority* class, which is "healthy" for all 9 leaves. That label would mislead, so the decision comes from the table instead.
7. **The notebook closes with a decision memo** following Lecture 1's structure: the action and the information used, the probability and loss assumptions, the comparison with a feasible alternative, and the limitations and conditions that would change the choice.

## 2. One small change to Step 3 code

`avg_cost` gets optional cost arguments: `def avg_cost(y_true, y_pred, c_fn=C_FN, c_fp=C_FP)`.
- Step 3 is unaffected, because the defaults are the same values.
- The sensitivity analysis can then reuse the function instead of repeating the formula.

## 3. Notebook structure

```
## 4. Evaluation of the Final Model
### 4.1 Test-set performance           ← decisions 1–2, metrics table, confusion matrix
### 4.2 Uncertainty of the test estimate ← Hoeffding (1 line), bootstrap intervals
### 4.3 Sensitivity to the cost ratio  ← ratios 5/10/20, switching points
### 4.4 Interpretation of the final tree ← tree diagram, leaf table
### 4.5 Recommendation and limitations ← decision memo (markdown)
```

## 4. Planned code cells (one task each)

New imports go into the Setup cell: `recall_score`, `precision_score`, `accuracy_score`, `ConfusionMatrixDisplay`, `plot_tree`.

| # | Cell |
|---|---|
| 1 | Helper `test_metrics(y_true, y_pred, c_fn)`: cost, recall, precision, accuracy, flagged firms |
| 2 | Test predictions of the final model and of the baseline (flags nobody) |
| 3 | Metrics table: final model vs baseline |
| 4 | Confusion matrix of the final model (plot) |
| 5 | Hoeffding half-width for the test cost (one line) |
| 6 | Bootstrap: 1,000 resamples of the test firms; costs of model, baseline and difference |
| 7 | 95% percentile intervals table |
| 8 | Test probabilities of the final model (computed once) |
| 9 | Sensitivity table for ratios 5, 10, 20: threshold, model cost, baseline cost, recall, precision |
| 10 | Leaf table: training firms, bankruptcy share, decision at 1/11, switching ratio $r^*$ |
| 11 | Plot of the final tree (node ids, proportions, raw units) |

## 5. Preview from the training set only

| Leaf share $\hat\eta$ | Training firms | Flagged at 1/6 (r = 5) | 1/11 (r = 10) | 1/21 (r = 20) | $r^*$ |
|---|---|---|---|---|---|
| 0.420 | 150 | ✔ | ✔ | ✔ | 1.4 |
| 0.397 | 121 | ✔ | ✔ | ✔ | 1.5 |
| 0.116 | 146 | – | ✔ | ✔ | 7.6 |
| 0.093 | 129 | – | ✔ | ✔ | 9.8 |
| 0.093 | 129 | – | ✔ | ✔ | 9.8 |
| 0.039 | 155 | – | – | – | 24.8 |
| 0.016, 0.015, 0.003 | 122, 264, 4,239 | – | – | – | > 60 |

- **Ratios 10 and 20 give identical decisions.** Every ratio between about 9.8 and 24.8 does, so the recommendation is robust to doubling the cost of a missed bankruptcy.
- **Ratio 5 flags only the two high-risk leaves:** 271 training firms instead of 675.
- **Two leaves (258 firms) are flagged only narrowly.** Their share of 0.093 is barely above 1/11, so with a cost ratio below 9.8 they would not be flagged. This goes into the limitations.
- **Runtime:** Step 4 adds only a few seconds.

## 6. Points for you to confirm or change

- **Score only M2 and the baseline on the test set: decided.**
- **Bootstrap: decided.** 1,000 resamples of the test firms, not stratified, so that the share of bankrupt firms also varies.
- **Switching-point column ($r^*$) in the leaf table: decided.** Kept, as an addition to the original Step 1 plan, which only mentioned ratios 5 and 20.