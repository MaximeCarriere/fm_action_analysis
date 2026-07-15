"""Statistics on within-window activation.

Activation is averaged over each area's half-max response window to give one
value per (subject, condition, area). A repeated-measures ANOVA then tests the
Condition × System × Area design (with Greenhouse-Geisser correction), followed
by per-area Blind-vs-Sighted post-hoc Welch t-tests (FDR-corrected).
"""
from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd
from scipy.stats import f as f_dist
from scipy.stats import ttest_ind
from statsmodels.stats.anova import AnovaRM
from statsmodels.stats.multitest import multipletests

from . import constants as C

WITHIN = ["Cond", "System", "Area"]


# ── window-averaged per-subject table ────────────────────────────────────────

def build_within_window_means(frame, window, presentation, spe=None) -> pd.DataFrame:
    """Average activation within each area's half-max window per subject.

    Returns one row per (Cond, Net2, [Spe], area) with the mean ``size`` and the
    System / Area-role / Peri-Extra labels used by the ANOVA.
    """
    keys = ["Presentation", "Net2", "Cond"] + (["Spe"] if spe else []) + ["patt_no", "area", "stp"]
    aa = frame.groupby(keys, as_index=False)["size"].mean()
    aa = aa[aa["Presentation"] == presentation]
    if spe:
        aa = aa[aa["Spe"] == spe]

    parts = []
    for area in aa["area"].unique():
        sub = aa[aa["area"] == area]
        if area in window.index:
            w = window.loc[area]
            sub = sub[(sub["stp"] <= w["half_max_stp"]) & (sub["stp"] >= w["half_max_stp_2"])]
        parts.append(sub)

    ab_keys = ["Cond", "Net2"] + (["Spe"] if spe else []) + ["area"]
    ab = pd.concat(parts).groupby(ab_keys, as_index=False)["size"].mean()
    ab["System"] = ab["area"].map(C.SYSTEM_BY_AREA)
    ab["Area"] = ab["area"].map(C.ROLE_BY_AREA)
    ab["Peri_Extra"] = ab["area"].map(C.PERI_EXTRA_BY_AREA)
    return ab


# ── Greenhouse-Geisser epsilon ───────────────────────────────────────────────

def gg_epsilon(Y: np.ndarray, cond_df: pd.DataFrame, effect: list) -> float:
    """Greenhouse-Geisser epsilon for a within-subject effect.

    Y : (n_subjects, n_conditions) repeated-measures matrix.
    cond_df : (n_conditions, n_factors) factor labels for Y's columns.
    effect : columns of cond_df defining the effect.
    """
    groups = cond_df.groupby(effect).groups
    n_subj = Y.shape[0]
    g = len(groups)

    M = np.zeros((n_subj, g))
    for j, level in enumerate(groups):
        M[:, j] = Y[:, list(groups[level])].mean(axis=1)

    M_centered = M - M.mean(axis=0)
    W = (M_centered.T @ M_centered) / n_subj
    return np.trace(W) ** 2 / ((g - 1) * np.trace(W @ W))


# ── repeated-measures ANOVA ──────────────────────────────────────────────────

def activation_rm_anova(frame, window, presentation, spe=None, verbose=True):
    """Condition × System × Area RM-ANOVA with Greenhouse-Geisser correction.

    Returns a dict with the raw ANOVA table (``anova``), the GG-corrected table
    (``gg``), and the filtered per-subject frame (``ab``). Only subjects with the
    full set of 24 (Cond × System × Area) cells are kept.
    """
    ab = build_within_window_means(frame, window, presentation, spe=spe)

    counts = ab.groupby("Net2").size()
    complete = counts[counts == 24].index
    ab_f = ab[ab["Net2"].isin(complete)].copy()

    rm = AnovaRM(ab_f, depvar="size", subject="Net2", within=WITHIN,
                 aggregate_func="mean").fit()
    anova = rm.anova_table.reset_index().rename(columns={"index": "Effect"})

    wide = ab_f.pivot_table(index="Net2", columns=WITHIN, values="size")
    Y = wide.values
    cond_df = wide.columns.to_frame(index=False)

    rows = []
    for k in range(1, len(WITHIN) + 1):
        for combo in combinations(WITHIN, k):
            eff = list(combo)
            name = ":".join(eff)
            eps = gg_epsilon(Y, cond_df, eff)
            r = anova.loc[anova["Effect"] == name].iloc[0]
            rows.append({
                "Effect": name, "epsilon": eps,
                "num_df": r["Num DF"], "den_df": r["Den DF"],
                "num_df_gg": r["Num DF"] * eps, "den_df_gg": r["Den DF"] * eps,
                "F": r["F Value"], "p_uncorr": r["Pr > F"],
                "p_gg": 1 - f_dist.cdf(r["F Value"], r["Num DF"] * eps, r["Den DF"] * eps),
            })
    gg = pd.DataFrame(rows)

    if verbose:
        print(f"RM-ANOVA  ·  n subjects = {len(complete)}  ·  presentation {presentation}"
              + (f"  ·  {spe}" if spe else ""))
        print(rm.summary())
        with pd.option_context("display.float_format", "{:.4g}".format, "display.width", 160):
            print("\nGreenhouse-Geisser corrected:")
            print(gg.to_string(index=False))

    return {"anova": anova, "gg": gg, "ab": ab_f}


# ── post-hoc per-area Blind vs Sighted ───────────────────────────────────────

def activation_posthoc(ab, verbose=True, method="bonferroni") -> pd.DataFrame:
    """Per-area Blind-vs-Sighted Welch t-tests, multiple-comparison corrected.

    Matches the manuscript: Bonferroni correction over the 12 area comparisons
    (adjusted α = .05/12 ≈ .0042), i.e. an area is significant when its
    corrected p-value < .05. Pass ``method='fdr_bh'`` for Benjamini-Hochberg FDR.
    """
    rows = []
    for area in sorted(ab["area"].unique()):
        area_data = ab[ab["area"] == area]
        for a, b in combinations(area_data["Cond"].unique(), 2):
            d1 = area_data[area_data["Cond"] == a]["size"]
            d2 = area_data[area_data["Cond"] == b]["size"]
            t, p = ttest_ind(d1, d2, equal_var=False)
            rows.append({"area": C.AREA_ORDER[int(area)], "comparison": f"{a} vs {b}",
                         "t": t, "p": p})

    out = pd.DataFrame(rows)
    out["p_corr"] = multipletests(out["p"], method=method)[1]
    out["sig"] = out["p_corr"].apply(
        lambda p: "***" if p < .001 else "**" if p < .01 else "*" if p < .05 else "ns")

    if verbose:
        with pd.option_context("display.float_format", "{:.4g}".format, "display.width", 160):
            print(out.to_string(index=False))
    return out
