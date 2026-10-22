# Step 2 — Variable Selection (recap)

**Notebook:** section 2 of `notebooks/bankruptcy_prediction.ipynb`. The whole notebook runs end to end in about 1.5 minutes and is saved with its outputs. Step 2 uses `X_train` and `y_train` only.

## What was built

| Section | Content |
|---|---|
| Setup | New imports added to your imports cell; your `ggplot` style is kept |
| 2.1 Method | The LASSO objective (LaTeX); decision LASSO vs forward selection; evidence that the extreme values carry signal; decisions on the quantile transform, the unpenalised intercept and the absence of class weights; definition of the `lasso` pipeline |
| 2.2 Choice of the penalty | Decision on CV log-loss; the `cv` splitter; cross-validation over a 13-value grid of `C`; number of variables per `C`; a 2-panel plot of the path |
| 2.3 Selected variables | The 43 coefficients at the chosen `C` |
| 2.4 Selection stability | Decision on the bootstrap; 100 stratified resamples; bar chart of the frequencies; decision on the hand-off; the `selector` object plus a check cell |
| 2.5 Takeaways | 5 bullets |

Section 2 adds 11 code cells and 7 decision cells.

## Key results

- **Extreme values carry signal.** Among the 4,816 training firms whose `Total Asset Growth Rate` exceeds 1, the value alone gives an AUC of 0.72 (0.28 with the direction flipped). This confirms that capping them at 1 would lose information.
- **Chosen penalty:** **C ≈ 0.178**, which keeps **43 of the 94 variables**. Its CV log-loss is 0.0855, against 0.143 with no variable. The curve is flat: every value from 21 to 59 variables is within one standard error (0.002) of the best.
- **What was selected:** leverage, profitability, liquidity and activity ratios. For the leading variables the signs make sense: more debt raises the risk, and more profit or liquidity lowers it.
- **Stability is moderate.**
  - Only 15 of the 43 selected variables appear in at least 80% of resamples. The median frequency is 0.69 and the lowest is 0.25.
  - `Research and development expense rate` is not selected on the full training set, yet appears in 81% of resamples.
  - The LASSO keeps both members of a practically identical pair (`Current Liabilities/Liability` and `Current Liability to Liability`), each with a tiny coefficient.
  - The variable list is a predictive shortlist, not a set of causes.
- **Check passed:** `selector`, fitted on the full training set, keeps exactly the 43 variables listed in 2.3.

## Differences from the plan

1. **Extra evidence cell in 2.1** (the AUC within the extreme-value group). It backs up the quantile-transform decision inside the notebook. The comparison of the four transforms (0.085 vs 0.098–0.100) is *cited* from my preliminary check rather than re-run, because re-running it would add about 6 minutes to the notebook.
2. **"LASSO rather than forward selection" is its own decision cell**, instead of a paragraph inside the method text.
3. **Extra check cell after the selector**, to confirm it reproduces the 43 variables.
4. **The cross-validation over `C` runs in parallel** (`n_jobs=-1`). This brings the whole notebook down to about 1.5 minutes.
5. **The stability chart shows all 92 variables that were selected at least once.** It is tall. If you want a more compact figure for the report, I can limit it to the top 40.

## Changes after your review

- **The stability chart has a proper legend.** Blue means "in the 43-variable shortlist" and grey means "not in the shortlist". A dashed line marks 80% of resamples, the boundary for robust selection.
- **The chart title is now "Bootstrap selection frequency (100 resamples)".** This needed `from matplotlib.patches import Patch` in the Setup cell.
- **The observation cell points to the dashed line.**
- **Your explanation cell under the chart is unchanged.**

## Carried into Step 3

- `cv` (the 5 stratified folds) and `selector` (unfitted; it is refit inside every fold) are ready.
- The comparison of fixed `C` against `C` tuned together with the tree, using the decision rule agreed on: prefer the joint version only if its CV cost is lower by more than one standard error.
- The misclassification costs have to enter the tree, through class weights or the threshold of 1/11. That is a decision for the Step 3 plan.
