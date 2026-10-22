# Final review — changes applied

## Point 3: removed evidence that the notebook does not reproduce

Four decision cells cited numbers from preliminary checks that were never in the notebook. Following the simplicity rule, each number was removed and the reasoning kept. The edits are markdown only, so the outputs did not change and no rerun was needed.

| Cell | Removed | Reasoning that remains |
|---|---|---|
| 2.1, quantile transform | CV log-loss comparison (0.085 vs 0.098–0.100) | The AUC evidence that the extreme values carry signal; the transform keeps the order of values and puts features on one scale |
| 2.1, intercept | liblinear vs saga sentence | Course convention; `intercept_scaling=100` makes the intercept penalty negligible |
| 3.1, costs | Class weights vs threshold (0.162 vs 0.159) | Leaves read as probabilities; Step 4 can change the cost ratio without retraining |
| 3.2, grid | "A first grid stopping at 80 … extended" | The leaf-size rationale (Lecture 3; about 4 bankruptcies in a leaf of 120 firms) |

## Point 2: repeated firms across years

Markdown only, no rerun needed.

- **Assumption cell (1.1):** now says that each row is treated as an independent observation. It adds that, with no firm ID and no year, we cannot check whether a firm appears in several years, and that neither a time-based nor a firm-based split is possible.
- **Limitations (4.5):** new bullet, "Possibly repeated firms". If the same firm sits in both training and test, the test cost (0.179) may be optimistic for genuinely new firms (Lecture 2). This can be neither checked nor corrected.

## Point 1: scikit-learn version check

- **What was added:** a new code cell in Setup, after your glossary cell and before the constants. It stops with a clear message if scikit-learn is older than 1.8.
- **Why:** from scikit-learn 1.5 to 1.7, `l1_ratio=1` silently falls back to an L2 penalty, so the LASSO would keep all 94 variables without any error.
- **Rerun:** the notebook was rerun with no errors. Results are unchanged (M2 CV cost 0.1512; test cost 0.1789). The notebook now has 134 cells.

## Point 4: paired comparison and best-of-grid bias

- **Rule definition (3.2):** the standard error is now computed on the per-fold gains over M2, because all candidates share the same folds. Before, each model's own standard error was used.
- **Rule table (3.4):** replaced by two cells, one collecting each candidate's cost per fold and one applying the paired rule. The comparison table and bar chart still show each model's own standard error.

| Alternative | Mean gain over M2 | Paired SE | Folds cheaper than M2 | Replaces M2 |
|---|---|---|---|---|
| M1 all features | −0.0117 | 0.0047 | 0 (cheaper or tied for M2 on all 5) | No |
| M3 joint `C` | +0.0029 | 0.0069 | 3 | No |

- **Decision cell (3.4) and "Selection helps" takeaway (3.6):** they now quote $0.012 \pm 0.005$, cheaper or tied on every fold. The claim is stronger than the earlier "just over one SE".
- **Observation (4.2):** the CV-to-test gap (0.151 → 0.179) is now explained by test noise *and* best-of-grid optimism, since 0.151 is the best of 56 configurations.
- **Rerun:** no errors, and the final model is unchanged (M2, test cost 0.179). The notebook now has 135 cells.

## Point 5: leaves flagged within estimation noise

- **Where:** the existing "Few bankruptcies" limitation (4.5) was extended by one sentence; no bullet was added.
- **What it says:** nodes 6 and 15 are flagged with a share of 0.093, only 0.002 above the threshold, while that share's standard error is about $\sqrt{0.093 \times 0.907 / 129} \approx 0.026$. Their decision therefore lies within estimation noise.
- **Checkable:** the number is written as a formula, and its inputs are visible in the leaf table.
- Markdown only, no rerun needed.

## Performance: option A, measuring the price of interpretability

- **Context.** CV experiments on the training set only showed that tuning the single tree further does not help: pruning, logistic regression, gradient boosting and a forest on all features are all within noise of M2. Only a LASSO + random forest clearly beats it.
- **Decision (option A).** M2 stays the final model. The forest is added as **M4, a benchmark, not a candidate**: the brief asks for a decision tree, and the memo relies on reading its rules. M4 is cross-validated only and never scored on the test set.
- **Notebook changes:**
  - **Setup:** `RandomForestClassifier` import, plus one line in your glossary under **Models**.
  - **New section 3.6, "Benchmark: the price of interpretability":** a decision cell, the M4 grid search (300 trees, leaf size in {1, 5, 10, 20, 40}), the paired comparison with M2, and an observation.
  - **Renumbering:** the Step 3 takeaways are now 3.7, with a new "Price of interpretability" bullet.
  - **4.1 decision cell:** M4 is listed among the models not scored on the test set.
  - **Memo, point 3:** one sentence. A forest would lower the CV cost by about 10%, but without the readable rules.
- **Result:** M4 costs 0.136 per firm vs 0.151 for M2, a gain of 0.015 ± 0.007, cheaper on all 5 folds (about 10%).
- **Rerun:** no errors. M2 and all test results are unchanged. The notebook now has 140 cells and runs in about 4.5 minutes.

## Still open (optional)

- **#6:** logistic regression as a candidate. Probably unnecessary: in the CV experiments it was within noise of M2 (+0.002 ± 0.004).
- **#7:** `clone`, and splitting the long cells.
- ~~**README.**~~ Done: `README.md` at the project root.
