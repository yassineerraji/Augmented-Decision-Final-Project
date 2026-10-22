# Step 4 — Evaluation of the Final Model (recap)

**Notebook:** section 4 of `src/bankruptcy_prediction.ipynb`, which you moved from `notebooks/`. I applied the edits there and kept your `.venv` kernel selection. The full notebook runs end to end in about 4 minutes with no errors and is saved with its outputs.

**The test set was used exactly once**, on the frozen final model (M2) and the "never flag" baseline only.

## What was built

| Section | Content |
|---|---|
| Setup | New imports: `recall_score`, `precision_score`, `accuracy_score`, `ConfusionMatrixDisplay`, `plot_tree` |
| Step 3 | `avg_cost` gained optional `c_fn`/`c_fp` arguments, with the same defaults, so Step 3 results are unchanged (M2 still 0.1512) |
| 4.1 Test-set performance | 2 decision cells; `test_metrics` helper; predictions; metrics table; confusion matrix |
| 4.2 Uncertainty | Decision; Hoeffding half-width; 1,000-resample bootstrap; 95% intervals |
| 4.3 Sensitivity | Decision; test probabilities computed once; table for ratios 5/10/20; decision on switching points; leaf table with $r^*$ |
| 4.4 Interpretation | Decision (why no class labels); tree diagram with node ids |
| 4.5 Recommendation and limitations | Decision memo in Lecture 1's structure; 7 limitations |

Section 4 adds 11 code cells and 6 decision cells. The notebook now has 132 cells in total.

## Key results

| Test set (1,364 firms, 44 bankrupt) | Final model | Baseline |
|---|---|---|
| Average cost per firm | **0.179** | 0.323 |
| 95% bootstrap interval | [0.134, 0.233] | [0.235, 0.418] |
| Recall | 72.7% (32 of 44) | 0% |
| Precision | 20.5% | – |
| Flagged firms | 156 (about 1 in 9) | 0 |
| Accuracy | 90.0% | 96.8% |

- **The model cuts the cost by 45%.** The paired interval for the gain, [−0.228, −0.065], excludes 0.
- **The test cost (0.179) is higher than the CV cost (0.151),** but the CV value lies inside the test interval. The gap is consistent with the noise you'd expect from only 44 test bankruptcies.
- **Hoeffding's margin is ±0.37:** valid, but too wide to separate the two rules. This is what motivated using the bootstrap.
- **Sensitivity:** the model beats the baseline at every cost ratio, cutting the cost by 35% at r = 5, 45% at r = 10 and 59% at r = 20. Ratios 10 and 20 give identical decisions, and ratio 5 flags 68 firms.
- **Switching points:**
  - Nodes 1 and 13 are flagged for any ratio above 1.5.
  - Node 12 switches at 7.6.
  - Nodes 6 and 15 switch at 9.75, so they are flagged only narrowly.
  - No leaf switches between 9.75 and 24.8.
- **Interpretation.** The tree raises an alarm in three situations:
  - the lowest net value growth (42% bankrupt);
  - high borrowing combined with weak profitability, especially when the debt is expensive (40% and 12%);
  - two smaller pockets at about 9%.

  Node 9 holds 78% of the firms and has a bankruptcy share of only 0.3%.

## Differences from the plan

1. **The leaf table sits at the end of 4.3,** where it explains the sensitivity results, rather than in 4.4. Section 4.4 refers back to it to read the tree diagram.
2. **The tree diagram uses `precision=5`.** With 3 decimals, splits such as `Net Value Growth Rate <= 0.00037` displayed as `<= 0.0`. Colours and class labels are left out, as planned.
3. **Both results tables have one row per model or per ratio,** so counts display as whole numbers (156, not 156.0000).
4. **The notebook's location changed** (`notebooks/` → `src/`) partway through this step. The first run had already been written before the move, so I re-applied the final edits to `src/`.

## Notes

- `step4_plan.md` is still at the root of `AgentDiscussion/`. I put this recap in `AgentDiscussion/step4/` to match your new layout, and I left the plan where it is in case you have it open. Move it whenever you like.
- The recap files for Steps 1–3 still mention `notebooks/` as the notebook's location. I left them unchanged, since they record what was true at the time.
