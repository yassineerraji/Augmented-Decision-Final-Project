# Executed at the end of the notebook by make_figures.py: exports slide-ready figures from the notebook's own results
import glob
import os
import matplotlib as mpl
from matplotlib import font_manager

OUT = os.environ["FIG_DIR"]
for font in glob.glob(os.path.expanduser("~/Library/Caches/TectonicProject.Tectonic/bundles/data/*/IBMPlex*.otf")) + \
            glob.glob("/usr/local/texlive/*/texmf-dist/fonts/opentype/ibm/plex/*/*.otf"):
    font_manager.fontManager.addfont(font)

# Deck palette (same values as in main.tex)
PAPER, INK, MUTED, RULE = "#F6F3EC", "#16181D", "#6B6F78", "#D9D2C5"
RISK, MODEL, GREY, GREY_LIGHT = "#B42318", "#155E63", "#A39E93", "#CFC9BD"

mpl.rcdefaults()
mpl.rcParams.update({
    "font.family": os.environ.get("FIG_FONT", "Arial"), "font.size": 9, "text.color": INK, "axes.labelcolor": INK, "axes.edgecolor": MUTED,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": RULE, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "axes.facecolor": "none", "figure.facecolor": "none", "savefig.transparent": True,
    "axes.titlesize": 9.5, "axes.titleweight": "semibold", "axes.titlelocation": "left", "legend.frameon": False,
})
save = lambda fig, name: (fig.savefig(f"{OUT}/{name}.pdf", bbox_inches="tight", pad_inches=0.02), plt.close(fig))

# 1. Spearman correlation matrix (1.3)
cmap = mpl.colors.LinearSegmentedColormap.from_list("deck", [MODEL, "#FBFAF6", RISK])
fig, ax = plt.subplots(figsize=(3.0, 2.7))
im = ax.imshow(corr, cmap=cmap, vmin=-1, vmax=1)
ax.set(xticks=[], yticks=[]); ax.grid(False); [s.set_visible(False) for s in ax.spines.values()]
cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03); cb.outline.set_visible(False); cb.set_label("Spearman correlation")
save(fig, "heatmap")

# 2. LASSO path: CV log-loss and number of selected variables (2.2)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(5.7, 1.85))
m, s = -lasso_cv.cv_results_["mean_test_score"], lasso_cv.cv_results_["std_test_score"] / np.sqrt(5)
a1.fill_between(C_grid, m - s, m + s, color=MODEL, alpha=0.15, lw=0)
a1.plot(C_grid, m, "o-", color=MODEL, ms=3.5, lw=1.4)
a1.set(xscale="log", xlabel="C (log scale)", ylabel="CV log-loss", title="Cross-validated log-loss")
a2.plot(C_grid, n_selected, "o-", color=INK, ms=3.5, lw=1.4)
a2.set(xscale="log", xlabel="C (log scale)", ylabel="ratios kept", title="Number of selected ratios")
for a in (a1, a2):
    a.axvline(best_C, color=RISK, ls="--", lw=1)
a2.annotate(f"C ≈ {best_C:.2f}: 43 ratios", xy=(best_C, 43), xytext=(0.0012, 52), color=RISK, fontsize=8.5,
            arrowprops=dict(arrowstyle="-", color=RISK, lw=0.8))
fig.tight_layout(w_pad=2.5)
save(fig, "lasso_path")

# 3. Bootstrap selection frequency as a "barcode" (2.4)
f = freq[freq > 0]
fig, ax = plt.subplots(figsize=(5.7, 1.55))
ax.bar(range(len(f)), f.values, color=np.where(f.index.isin(selected.index), MODEL, GREY_LIGHT), width=0.78)
ax.axhline(0.8, color=RISK, ls="--", lw=1)
ax.text(len(f) - 1, 0.84, "80 % of resamples", color=RISK, ha="right", fontsize=8.5)
ax.set(xticks=[], xlim=(-1, len(f)), ylim=(0, 1.08), ylabel="selection frequency", xlabel=f"{len(f)} ratios, sorted by frequency")
ax.grid(axis="x", visible=False)
ax.legend(handles=[Patch(color=MODEL, label="in the 43-ratio shortlist"), Patch(color=GREY_LIGHT, label="not in the shortlist")],
          loc="upper right", bbox_to_anchor=(1, 0.78), fontsize=8.5)
save(fig, "stability")

# 4. Validation curves of M2 (3.3)
res = pd.DataFrame(m2.cv_results_)
fig, axes = plt.subplots(1, 2, figsize=(5.7, 1.85), sharey=True)
for ax, leaf, title in zip(axes, [1, best_leaf], ["Leaves of 1 firm: overfitting", f"Leaves of ≥ {best_leaf} firms: stable"]):
    r = res[res["param_estimator__tree__min_samples_leaf"] == leaf]
    depth = r["param_estimator__tree__max_depth"].fillna("none").astype(str)
    ax.plot(depth, -r["mean_train_score"], "o-", color=GREY, ms=3.5, lw=1.4, label="training")
    ax.plot(depth, -r["mean_test_score"], "o-", color=MODEL, ms=3.5, lw=1.4, label="cross-validation")
    ax.set(title=title, xlabel="maximum depth")
axes[0].set_ylabel("cost per firm"); axes[0].legend(loc="lower left", fontsize=8.5)
fig.tight_layout(w_pad=2)
save(fig, "validation")

# 5. Cross-validated cost of the four candidates (3.4)
labels = ["Never flag (M0)", "Tree, all 94 ratios (M1)", "LASSO + tree (M2)", "LASSO, joint C + tree (M3)"]
vals, ses = comparison["CV cost"].values, comparison["SE"].values
fig, ax = plt.subplots(figsize=(5.4, 1.6))
ax.barh(labels, vals, xerr=ses, color=[GREY_LIGHT, GREY, MODEL, GREY], height=0.58, error_kw=dict(ecolor=INK, lw=0.8, capsize=2))
for i, v in enumerate(vals):
    ax.text(v + ses[i] + 0.006, i, f"{v:.3f}", va="center", fontsize=8.5, weight="semibold" if i == 2 else "normal")
ax.invert_yaxis(); ax.set(xlim=(0, 0.37), xlabel="cross-validated cost per firm (± 1 SE)"); ax.grid(axis="y", visible=False)
save(fig, "candidates")

# 6. Paired per-fold comparison of M1 and M2 (3.4)
fig, ax = plt.subplots(figsize=(2.15, 2.0))
for k in range(5):
    ax.plot([0, 1], fold_costs.iloc[k][["M1 all features", "M2 LASSO, C fixed"]], "o-", color=MODEL, ms=4, lw=1.2)
ax.set(xticks=[0, 1], xticklabels=["M1\nall ratios", "M2\nLASSO"], xlim=(-0.35, 1.35), ylabel="cost per firm (one line per fold)")
ax.grid(axis="x", visible=False)
save(fig, "paired")

# 7. Test costs with 95 % bootstrap intervals (4.2)
q = boot_costs.quantile([0.025, 0.975])
est = {"Final model": avg_cost(y_test, y_pred), "Baseline": avg_cost(y_test, y_base)}
fig, ax = plt.subplots(figsize=(5.4, 1.15))
for i, (name, col) in enumerate([("Final model", MODEL), ("Baseline", GREY)]):
    ax.plot(q[name], [i, i], color=col, lw=6, solid_capstyle="round", alpha=0.35)
    ax.plot(est[name], i, "o", color=col, ms=7)
    ax.text(q[name].iloc[1] + 0.01, i, f"{est[name]:.3f}   [{q[name].iloc[0]:.3f}, {q[name].iloc[1]:.3f}]", va="center", fontsize=8.5)
ax.set(yticks=[0, 1], yticklabels=["Final model", "Never flag"], ylim=(-0.6, 1.6), xlim=(0.1, 0.56), xlabel="test cost per firm, with 95 % bootstrap interval")
ax.invert_yaxis(); ax.grid(axis="y", visible=False)
save(fig, "bootstrap")

# 8. Switching cost ratio of each leaf (4.3)
lt = leaf_table.sort_values("bankruptcy share", ascending=False)
y = np.arange(len(lt))
cols = np.where(lt["flagged at 1/11"], RISK, GREY)
fig, ax = plt.subplots(figsize=(3.75, 2.15))
ax.hlines(y, 1, lt["switching ratio r*"], color=cols, lw=1.3)
ax.scatter(lt["switching ratio r*"], y, color=cols, s=26, zorder=3)
for r in (5, 10, 20):  # reference lines stop below the header so the label stays clear
    ax.vlines(r, -0.6, len(lt) - 0.5, color=INK if r == 10 else MUTED, ls="-" if r == 10 else ":", lw=1)
ax.text(10, -1.05, "our ratio: 10", ha="center", va="center", fontsize=8.5, color=INK, weight="semibold")
ax.set(xscale="log", yticks=y, xlabel="switching cost ratio r*", xticks=[1, 2, 5, 10, 20, 50, 100, 300],
       yticklabels=[f"{s:.1%} · {n:,} firms" for s, n in zip(lt["bankruptcy share"], lt["training firms"])])
ax.set_xticklabels(["1", "2", "5", "10", "20", "50", "100", "300"]); ax.minorticks_off()
ax.set_ylim(len(lt) - 0.5, -1.6); ax.grid(axis="y", visible=False)
save(fig, "switching")
print("figures written to", OUT)
