# Step 2 — Variable Selection (plan)

Everything in this step uses the training set only (`X_train`, `y_train`).

## 1. Method: LASSO logistic regression

The outcome is binary, so the LASSO of Lecture 4 becomes an **L1-penalised logistic regression**, with an unpenalised intercept:

$$\min_{b_0,\,\beta}\; -\frac{1}{n}\sum_{i=1}^{n}\Big[y_i \log p_i + (1-y_i)\log(1-p_i)\Big] + \lambda \lVert\beta\rVert_1, \qquad p_i = \frac{1}{1+e^{-(b_0 + x_i^\top\beta)}}$$

In scikit-learn the penalty is expressed as `C` $= 1/(n\lambda)$: a smaller `C` means a stronger penalty and fewer variables.

**Why LASSO rather than forward selection (Lecture 3.2):**
- One parameter controls the number of variables.
- It copes with the 50 highly correlated pairs found in Step 1.
- One fit takes about 0.5 s, so it can be refit inside every cross-validation fold of Step 3, as the brief requires.
- Forward selection is greedy and would need thousands of model fits per selection (up to 94 candidates per step), repeated again in every fold.

**Role in the pipeline:** the LASSO only *chooses* the variables. The decision tree in Step 3 receives those variables with their **raw values**, so its split thresholds stay in the original ratio units.

## 2. Decisions (each one becomes a short markdown cell)

1. **The LASSO input is transformed with a rank-based quantile transform** (to a standard normal), fitted inside each fold. This transform is not passed on to the tree.
   - Why not cap the extreme values at 1: they carry signal. Within the extreme-value group of `Total Asset Growth Rate`, the magnitude alone gives an AUC of 0.72. Capping would erase that.
   - What the transform does: it keeps the order of the values, removes the magnitude problem, and puts all features on the same scale, which a fair L1 penalty needs.
   - Evidence, 5-fold CV log-loss on the training set:

     | Transform | CV log-loss |
     |---|---|
     | Quantile | **0.085** |
     | Cap at 1 + standardise | 0.098 |
     | log + standardise | 0.100 |
     | Standardise only | 0.100 |

2. **The intercept stays unpenalised, as in the course.**
   - The problem: scikit-learn's `liblinear` solver penalises the intercept by default, which visibly distorts the path at strong penalties.
   - The fix: setting `intercept_scaling=100` makes that penalty negligible.
   - Check: the `saga` solver, which never penalises the intercept, gives the same path but runs about 6× slower and raises a convergence warning.
3. **No class weights in the selector.** It is a penalised maximum-likelihood fit. The misclassification costs enter in Step 3, where the decision is made.
4. **`C` is chosen by 5-fold stratified cross-validation, minimising log-loss.**
   - Why log-loss: it is a proper scoring rule for probabilities, the classification counterpart of the validation MSE used in Lectures 3–4.
   - Grid: 13 values of `C` from $10^{-3}$ to $1$, evenly spaced on a log scale.
   - The same CV splitter (`StratifiedKFold(5, shuffle=True, random_state=SEED)`) is reused in Step 3.
5. **Selection stability is measured with 100 stratified bootstrap resamples** of the training set (Lecture 4). `C` stays fixed and the full procedure is refit on each resample. The resulting selection frequencies are **descriptive** and do not change the selected set.
6. **Hand-off to Step 3:** the selection procedure is wrapped as a scikit-learn `SelectFromModel` object. It sits in front of the tree and is **refit inside every CV fold**, with `C` fixed at the value chosen here.
   - Step 3 also compares this fixed `C` with tuning `C` together with the tree, on the decision cost.
   - Both versions use the same folds and the same metric.
   - The joint version is preferred only if its CV cost is lower by more than one standard error across folds.

## 3. Notebook structure

```
## 2. Variable Selection
### 2.1 Method                     ← objective, why LASSO, decision cells 1–3
### 2.2 Choice of the penalty      ← CV over C, path plot
### 2.3 Selected variables         ← coefficients at the chosen C
### 2.4 Selection stability        ← bootstrap frequencies
### 2.5 Step 2 takeaways
```

## 4. Planned code cells (one task each)

New imports go into the existing Setup cell.

| # | Cell |
|---|---|
| 1 | Define the 5-fold stratified CV splitter (reused in Step 3) |
| 2 | Define the LASSO pipeline: quantile transform, then L1 logistic regression |
| 3 | Cross-validate the grid of `C` values (log-loss) |
| 4 | Count the selected variables for each `C` (refit on the full training set) |
| 5 | Plot CV log-loss and the number of selected variables against `C`, with the chosen `C` marked |
| 6 | Fit the LASSO at the chosen `C`; list the selected variables with their coefficients |
| 7 | Bootstrap: selection frequency of each variable over 100 resamples |
| 8 | Bar chart of the selection frequencies |
| 9 | Build the selector for Step 3 (`SelectFromModel` wrapping the LASSO pipeline at the chosen `C`) |

**Preview from my checks:**
- **Chosen penalty:** the best `C` is about 0.18. It keeps **43 of the 94 variables**, with a CV log-loss of 0.085 against about 0.14 for the intercept-only model.
- **Stability:** of the selected variables, only about 18 appear in at least 80% of resamples, and the median selection frequency is 0.65. Correlated ratios swap places from one resample to the next, which is the instability Lecture 4 warns about.
- **Runtime:** Step 2 adds about 2 minutes to the notebook (40 s for the path, about 65 s for the bootstrap).

## 5. Points for you to confirm or change

- **Rule for choosing `C`: decided.** We use the lowest CV log-loss (course protocol). Step 3 compares it with tuning `C` together with the tree (see decision 6). The one-standard-error rule was dropped because its result depends on the solver.
- **Number of bootstrap resamples:** 100, which takes about 1 minute.
