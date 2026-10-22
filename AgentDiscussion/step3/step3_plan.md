# Step 3 — Model Selection and Decision Tree Tuning (plan)

Everything in this step uses the training set only, with the 5 folds `cv` from Step 2. The test set is first used in Step 4.

## 1. Decision rule and metric

- **The tree estimates probabilities and the loss table decides (Lectures 1 and 3).**
  - A standard Gini tree is grown.
  - Each leaf estimates $\hat\eta(x) = P(Y=1 \mid x)$ by its share of bankrupt firms.
  - A firm is flagged when $\hat\eta(x) \geq 1/11$, the Bayes threshold from 1.1.
  - In code, scikit-learn's `FixedThresholdClassifier(..., threshold=THRESHOLD)` wraps the model, so `predict()` returns the cost-optimal decision directly.
- **The metric is the average cost per firm**, $(C_{FN}\cdot\text{FN} + C_{FP}\cdot\text{FP})/n$. It is turned into a scikit-learn scorer and used for all tuning and comparisons.

## 2. Decisions (each one becomes a short markdown cell)

1. **The costs enter through the threshold, not through class weights.**
   - The alternative: grow the tree with cost-weighted Gini (`class_weight={0: 1, 1: 10}`).
   - What I found: that gives the same CV cost within one standard error (0.162 vs 0.159 in my check).
   - Why the threshold: it keeps the course's reading of leaves as probability estimates. It also lets Step 4 re-run the cost-ratio sensitivity by changing only the threshold, with no retraining.
2. **Tuning grid (Gini criterion, `random_state = SEED`):**

   | Parameter | Values |
   |---|---|
   | `max_depth` | 2, 3, 4, 5, 6, 8, None (no limit) |
   | `min_samples_leaf` | 1, 10, 20, 40, 80, 120, 160, 200 |

   Why the leaf sizes go so high:
   - Leaf shares are only trusted as probabilities if leaves are large enough (Lecture 3: "small leaves make probability estimates unstable").
   - With a 3.2% bankruptcy rate, a leaf of 120 firms contains only about 4 bankruptcies on average.
   - My first grid stopped at 80, and that edge value won, so I extended the grid.
3. **Four candidates, all cross-validated on the same `cv` folds.** The selection step is refit inside every fold.

   | | Candidate | Tuned |
   |---|---|---|
   | M0 | Baseline: never flag | – |
   | M1 | Tree on all 94 features | depth, leaf |
   | M2 | LASSO selector (`C` fixed at 0.178, from Step 2) + tree | depth, leaf |
   | M3 | LASSO selector + tree, with `C` tuned jointly | `C`, depth, leaf |

   For M3, `C` takes the 7 values of Step 2's grid from 0.01 to 0.316. That range includes 0.178, so M3 contains M2 as one of its options.
4. **Selection rule (as agreed in Step 2):** M2, the course protocol, is the reference. An alternative replaces it only if its CV cost is lower by more than one standard error. Standard error = standard deviation across the 5 folds / √5.
5. **The final model** is the chosen candidate refit on the full training set with its best parameters. It is then **frozen** for Step 4.

## 3. Notebook structure

```
## 3. Model Selection and Decision Tree Tuning
### 3.1 Decision rule and metric        ← cost function, scorer
### 3.2 Candidates and tuning grid      ← decision cells 1–4, grid
### 3.3 Cross-validated tuning          ← M0, M1, M2, M3, validation curve
### 3.4 Model comparison                ← table, plot, selection rule
### 3.5 Final model                     ← frozen pipeline, what it uses
### 3.6 Step 3 takeaways
```

## 4. Planned code cells (one task each)

New imports go into the Setup cell: `DecisionTreeClassifier`, `FixedThresholdClassifier`, `DummyClassifier`, `Pipeline`, `make_scorer`, `confusion_matrix`, `cross_val_score`.

| # | Cell |
|---|---|
| 1 | Cost function: average misclassification cost per firm |
| 2 | Scorer built from the cost function |
| 3 | Tree grid (`max_depth`, `min_samples_leaf`) |
| 4 | M0: CV cost of "never flag" |
| 5 | M1: grid search, thresholded tree on all features |
| 6 | M2: grid search, thresholded pipeline (selector with fixed `C`, then tree) |
| 7 | M3: same as M2, with `C` added to the grid |
| 8 | Validation curve for M2: training and CV cost against depth, for leaf size 1 and for the chosen leaf size |
| 9 | Comparison table: CV cost ± standard error, number of variables, best parameters (M0–M3) |
| 10 | Bar chart of the comparison with ±1 standard-error bars |
| 11 | Apply the selection rule and keep the final model |
| 12 | Describe the final model: parameters, variables selected, variables the tree actually uses, number of leaves |

## 5. Preview from my checks (same folds and seed, so the notebook should reproduce them)

| Candidate | CV cost per firm | Best parameters |
|---|---|---|
| M0 never flag | 0.323 ± 0.002 | – |
| M1 all features | 0.163 ± 0.009 | depth 4, leaf 120 |
| **M2 LASSO, fixed `C`** | **0.151 ± 0.008** | depth 4, leaf 120 (43 selected; the tree uses 8) |
| M3 LASSO, joint `C` | 0.148 ± 0.009 | `C` = 0.01 (about 7 variables), depth 3, leaf 10 |

- **All trees roughly halve the baseline cost.**
- **Selection helps:** M2 beats M1 by 0.012, which is more than one standard error.
- **M3 does not beat M2 by enough:** its gain of 0.003 is well below one standard error, so the rule keeps **M2**.
  - Interesting side result: tuning `C` on the decision cost picks a much sparser selection (about 7 variables) at practically the same cost.
  - In practice the final M2 tree uses only 8 variables anyway, so the two models are similarly interpretable.
- **The validation curve tells the overfitting story (Lecture 2):** with leaves of size 1, training cost falls to 0 as depth grows, while CV cost rises from 0.17 to 0.23. With leaves of 120, depth 4 is best.
- **Runtime:** Step 3 adds about 2.5 minutes, almost all of it for M3.

## 6. Points for you to confirm or change

**Decided (you approved the recommendations):**
- The costs enter through the threshold.
- The grid stays as listed in decision 2.
- The agreed rule stays as it is, with no tie-breaker for fewer variables.

The original points are kept below for reference.

- **How costs enter:** through the threshold (recommended), or through class weights.
- **The grid in decision 2.**
- **Keeping the agreed rule, even though M3 reaches the same cost with about 7 variables.** The alternative is to add a tie-breaker: "within one standard error, prefer fewer selected variables", which would pick M3. I recommend keeping the agreed rule. It was set before seeing these results, and changing a rule after seeing the results weakens it.
