<div align="center">

# Taiwanese Bankruptcy Prediction

**Cost-sensitive bankruptcy screening with LASSO variable selection and an interpretable decision tree**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/release/python-3120/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.9-F7931E?logo=scikitlearn&logoColor=white)](https://scikit-learn.org/stable/)
[![pandas](https://img.shields.io/badge/pandas-3.0-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Data](https://img.shields.io/badge/data-UCI%20·%20CC%20BY%204.0-lightgrey)](https://archive.ics.uci.edu/dataset/572/taiwanese+bankruptcy+prediction)

*Augmented Decision · Final project · October 2026*

</div>

---

## Overview

A credit analyst must decide whether to **flag** a listed firm as high-risk using its financial ratios. Bankruptcies are rare (**3.2%** of 6,819 firms), and missing one is costly, so the model is judged on **decision cost** rather than accuracy:

| | Healthy firm | Bankrupt firm |
|---|:---:|:---:|
| **Not flagged** | 0 | **10** (missed bankruptcy) |
| **Flagged** | **1** (false alarm) | 0 |

Under this loss table, the optimal decision rule flags a firm when its estimated bankruptcy probability is **at least 1/11**.

## Method

```
94 financial ratios
   │  quantile transform + L1-penalised logistic regression (LASSO, C ≈ 0.18, chosen by CV log-loss)
   ▼
43 selected ratios (raw values)
   │  decision tree: depth 4, at least 120 firms per leaf (tuned by 5-fold CV on decision cost)
   ▼
share of bankrupt firms in the leaf  →  flag the firm if it is ≥ 1/11
```

The final tree has **9 leaves and uses 8 ratios**, so every decision can be read as a short rule. Examples: weak net value growth; heavy borrowing combined with low profitability.

## Key results

**Test set** (1,364 unseen firms, used exactly once):

| | Never flag (baseline) | **Final model** |
|---|:---:|:---:|
| Average cost per firm | 0.323 | **0.179** (−45%) |
| Bankruptcies caught | 0 / 44 | **32 / 44** (73%) |
| False alarms | 0 | 124 |
| Firms flagged | 0 | 156 (about 1 in 9) |

The 95% bootstrap interval for the cost reduction is **0.065 to 0.228 per firm**, so the gain over the baseline is not due to chance.

**Model comparison** (5-fold CV on the training set, average cost per firm):

| Model | CV cost | Notes |
|---|:---:|---|
| Tree on all 94 ratios | 0.163 | |
| **LASSO + tree (final)** | **0.151** | Beats the tree on all ratios by 0.012 ± 0.005 (paired across folds) |
| LASSO (penalty tuned with the tree) + tree | 0.148 | Within noise of the final model |
| LASSO + random forest *(benchmark only)* | 0.136 | About 10% cheaper, but without readable rules |

## Notebook roadmap

| Step | Content |
|---|---|
| **1 · Problem formulation & EDA** | Loss table and decision rule, data checks, extreme values, 50 highly correlated ratio pairs, stratified 80/20 split |
| **2 · Variable selection** | LASSO logistic regression, penalty chosen by CV, stability check on 100 bootstrap resamples |
| **3 · Model selection & tuning** | Four candidates on the same folds, paired one-standard-error rule, random forest benchmark |
| **4 · Evaluation** | Single use of the test set, bootstrap intervals, cost-ratio sensitivity, tree interpretation, decision memo and limitations |

Every assumption and decision is stated in its own markdown cell.

## Getting started

```bash
# 1. Create the environment (Python 3.12) and install the pinned dependencies
uv venv --python 3.12
uv pip install -r requirements.txt        # or: python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt

# 2. Run the full notebook headlessly (about 4.5 minutes), or open it and select the .venv kernel
.venv/bin/jupyter nbconvert --to notebook --execute --inplace src/bankruptcy_prediction.ipynb
```

> [!IMPORTANT]
> The notebook requires **scikit-learn ≥ 1.8** and stops with a clear message otherwise. Older versions would silently replace the LASSO penalty with an L2 penalty.

## Repository structure

```
ADE-Final/
├── src/
│   └── bankruptcy_prediction.ipynb   # the deliverable: 4 steps, executed with outputs
├── data/
│   ├── data.csv                      # 6,819 firms × 96 columns
│   └── README.md                     # variable descriptions (UCI)
├── report/
│   ├── main.tex / main.pdf           # final report (LaTeX, compiled with Tectonic or XeLaTeX)
│   ├── figures/                      # report figures (IBM Plex Sans)
│   ├── appendix/                     # LLM-assistance appendix: prompt log and rendered discussion files
│   └── build_appendix.py             # regenerates appendix/ (pandoc rendering, verbatim prompts)
├── slides/
│   ├── main.tex / main.pdf           # final presentation (Beamer, set in Arial)
│   ├── figures/                      # slide figures (Arial)
│   └── make_figures.py               # re-runs the notebook and exports the figures of both
├── AgentDiscussion/                  # plan and recap of each step, final review log
├── INSTRUCTIONS.md                   # coding and workflow rules
├── requirements.txt                  # pinned dependencies
└── README.md
```

## Rigour and reproducibility

- **The test set is used once**, on the frozen final model and the baseline only.
- **Variable selection and preprocessing are refit inside every cross-validation fold**, so no information leaks from the validation folds.
- **The seed is fixed** (`SEED = 42`) and the dependencies are pinned, so a full rerun reproduces every number.
- **Limitations are discussed in section 4.5:** costs are assumed rather than measured, there is no time dimension, there are few bankruptcies, and some firms may repeat across years.

## Data and citation

Taiwan Economic Journal, 1999–2009, via the UCI Machine Learning Repository: *Taiwanese Bankruptcy Prediction*, [doi:10.24432/C5004D](https://doi.org/10.24432/C5004D), licensed under CC BY 4.0.
Original study: Liang, D., Lu, C.-C., Tsai, C.-F., & Shih, G.-A. (2016). *Financial ratios and corporate governance indicators in bankruptcy prediction: A comprehensive study.* European Journal of Operational Research, 252(2), 561–572.