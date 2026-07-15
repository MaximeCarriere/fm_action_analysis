"""Network-level statistics comparing Blind vs Sighted connectivity."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from . import constants as C


def system_pair_blind_vs_sighted_by_net(
    data: pd.DataFrame,
    file_: str,
    presentation: float,
    groups: dict[str, list[str]] | None = None,
    include_diagonal: bool = True,
    agg: str = "sum",
    paired: bool | None = None,
    correction: str = "bonferroni",
    verbose: bool = True,
) -> pd.DataFrame:
    """Compare Blind vs Sighted connectivity for every functional-system pair.

    For each system pair the connectivity is aggregated per (subject, condition)
    into one value per network, then Blind is compared with Sighted across
    networks.  A paired t-test is used when every network has both conditions
    (auto-detected unless ``paired`` is set explicitly); otherwise Student's
    independent-samples t-test is used.

    ``data`` must be the raw, per-subject frame (not pre-averaged across ``Net``).
    Returns one row per system pair with test statistics, effect size and a
    multiple-comparison-corrected p-value.
    """
    if groups is None:
        groups = C.GROUPS_AREAS

    base = data[(data["File"] == file_) & (data["Presentation"] == presentation)]
    gnames = list(groups.keys())
    rows = []

    for i, gi in enumerate(gnames):
        for j, gj in enumerate(gnames):
            if j < i:
                continue
            ai, aj = groups[gi], groups[gj]

            mask = base["area1"].isin(ai) & base["area2"].isin(aj)
            if i != j:  # cross-system: include the reverse direction too
                mask |= base["area1"].isin(aj) & base["area2"].isin(ai)
            sub = base[mask]
            if not include_diagonal:
                sub = sub[sub["area1"] != sub["area2"]]

            per_net = sub.groupby(["Net", "Cond"], as_index=False)["sum"].agg(agg)
            pivot = per_net.pivot(index="Net", columns="Cond", values="sum")

            common_nets = pivot.dropna().index
            if paired is None:
                use_paired = len(common_nets) >= 2 and len(common_nets) == len(pivot)
            else:
                use_paired = bool(paired)

            if use_paired:
                b_vals = pivot.loc[common_nets, "Blind"].to_numpy()
                s_vals = pivot.loc[common_nets, "Sighted"].to_numpy()
                t, p = stats.ttest_rel(b_vals, s_vals)
                test_used, n_b, n_s = "paired", len(common_nets), len(common_nets)

                diffs = b_vals - s_vals
                eff_size = diffs.mean() / diffs.std(ddof=1) if diffs.std(ddof=1) > 0 else np.nan
                eff_kind = "d_z"
            else:
                b_vals = pivot["Blind"].dropna().to_numpy()
                s_vals = pivot["Sighted"].dropna().to_numpy()
                t, p = stats.ttest_ind(b_vals, s_vals, equal_var=True)
                test_used, n_b, n_s = "student", len(b_vals), len(s_vals)

                pooled_sd = np.sqrt(
                    ((n_b - 1) * b_vals.var(ddof=1) + (n_s - 1) * s_vals.var(ddof=1))
                    / (n_b + n_s - 2)
                )
                eff_size = (b_vals.mean() - s_vals.mean()) / pooled_sd if pooled_sd > 0 else np.nan
                eff_kind = "d"

            rows.append({
                "system_a": gi,
                "system_b": gj,
                "kind": "within" if i == j else "cross",
                "n_blind": n_b,
                "n_sighted": n_s,
                "test": test_used,
                "mean_blind": b_vals.mean(),
                "mean_sighted": s_vals.mean(),
                "mean_diff": b_vals.mean() - s_vals.mean(),
                "effect_size": eff_size,
                "effect_kind": eff_kind,
                "t": t,
                "p": p,
            })

    out = pd.DataFrame(rows)

    if correction == "bonferroni":
        out["p_corrected"] = np.minimum(out["p"] * len(out), 1.0)
    elif correction == "fdr_bh":
        from scipy.stats import false_discovery_control
        out["p_corrected"] = false_discovery_control(out["p"].values)
    else:
        out["p_corrected"] = out["p"]

    out["sig"] = out["p_corrected"].apply(
        lambda p: "***" if p < .001 else "**" if p < .01 else "*" if p < .05 else "ns"
    )

    if verbose:
        with pd.option_context(
            "display.float_format", "{:.4g}".format,
            "display.max_columns", None, "display.width", 160,
        ):
            print(out.to_string(index=False))
    return out


def within_group_change_test(
    data: pd.DataFrame,
    file_: str,
    p_start: float = 0,
    p_end: float = 50,
    areas: tuple[str, ...] = ("V1", "TO", "AT"),
    include_diagonal: bool = True,
    verbose: bool = True,
) -> dict[str, float]:
    """Test whether the within-group connectivity change differs by condition.

    The change ``Δ = P{p_end} − P{p_start}`` in connectivity within ``areas`` is
    computed per network, then compared between Blind and Sighted with Student's
    independent-samples t-test (Cohen's d reported).
    """
    def per_net_within(presentation: float) -> pd.DataFrame:
        sub = data[
            (data["File"] == file_)
            & (data["Presentation"] == presentation)
            & (data["area1"].isin(areas))
            & (data["area2"].isin(areas))
        ]
        if not include_diagonal:
            sub = sub[sub["area1"] != sub["area2"]]
        return sub.groupby(["Net", "Cond"])["sum"].sum().unstack("Cond")

    delta = per_net_within(p_end) - per_net_within(p_start)
    b = delta["Blind"].dropna().to_numpy()
    s = delta["Sighted"].dropna().to_numpy()

    t, p = stats.ttest_ind(b, s, equal_var=True)
    pooled_sd = np.sqrt(
        ((len(b) - 1) * b.var(ddof=1) + (len(s) - 1) * s.var(ddof=1))
        / (len(b) + len(s) - 2)
    )
    d = (b.mean() - s.mean()) / pooled_sd

    if verbose:
        print(f"Δ within-{'/'.join(areas)} (P{p_end} − P{p_start}):")
        print(f"  Blind:   M={b.mean():.1f}  SD={b.std(ddof=1):.1f}  n={len(b)}")
        print(f"  Sighted: M={s.mean():.1f}  SD={s.std(ddof=1):.1f}  n={len(s)}")
        print(f"  t({len(b)+len(s)-2}) = {t:.2f},  p = {p:.3g},  Cohen's d = {d:.2f}")

    return {"t": t, "p": p, "d": d, "mean_blind": b.mean(), "mean_sighted": s.mean()}
