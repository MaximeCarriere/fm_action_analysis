"""Build, save and load the time-course activation dataset.

The heavy step reads every subject's neuron-level spike file and reduces it to
an activation count (``size`` = number of distinct active neurons) per
(Network, pattern, time-step, area, stimulation). That reduction is done once by
``build_activation`` and written to ``data/activation_{p1,p2}.csv``; the analysis
then calls ``load_activation``, which expands the table to include zero-activation
combinations and returns an analysis-ready frame.

Note: the neuron *identities* (a huge ``List`` column in the original notebook)
are never needed for TCA — only the count — so they are dropped immediately,
which keeps the processed tables small.
"""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

from . import constants as C
from .config import processed_path


# ── build (raw → processed) ──────────────────────────────────────────────────

def get_subfolders(directory: str | Path) -> list[str]:
    """Return the sorted list of immediate sub-directories of ``directory``."""
    subfolders = [f.path for f in os.scandir(directory) if f.is_dir()]
    subfolders.sort()
    return subfolders


def get_tca_size(df: pd.DataFrame) -> pd.DataFrame:
    """Reduce a raw neuron-spike table to an activation count per group.

    ``size`` is the number of distinct neurons active per
    (Network, patt_no, stp, area, Stim).
    """
    df = df.loc[df["patt_no"].between(1, 18)]
    return (
        df.groupby(["Network", "patt_no", "stp", "area", "Stim"])["neuron"]
        .nunique()
        .reset_index(name="size")
    )


def _load_condition(result_dirs, raw_file, condition, stim_min):
    frames = []
    for net_dir in result_dirs:
        path = os.path.join(net_dir, raw_file)
        try:
            df = pd.read_csv(path, sep=r" |\t", engine="python")
        except FileNotFoundError:
            print(f"  missing: {path}")
            continue
        if stim_min is not None:
            df = df[df["Stim"] > stim_min]
        sub = get_tca_size(df)
        sub["Net"] = net_dir
        sub["Cond"] = condition
        frames.append(sub)
    return frames


def build_activation(paradigm: str, sighted_dir, blind_dir) -> pd.DataFrame:
    """Read the raw simulation folders and return the processed activation table.

    Applies the paradigm-specific cleaning: drop runaway networks, restrict the
    time-step range and presentations, keep the retained subjects, and map the
    network index to a presentation number.
    """
    cfg = C.PARADIGMS[paradigm]

    frames = []
    frames += _load_condition(get_subfolders(sighted_dir), cfg["raw_file"], "Sighted", cfg["stim_min"])
    frames += _load_condition(get_subfolders(blind_dir), cfg["raw_file"], "Blind", cfg["stim_min"])
    data = pd.concat(frames, ignore_index=True)

    data["File"] = paradigm
    data["Net2"] = data["Net"].str[-2:].astype(int)

    # Drop runaway networks (size above threshold at a specific network level).
    if cfg["outlier_network_op"] == ">":
        bad = data["Network"] > cfg["outlier_network_val"]
    else:  # "=="
        bad = data["Network"] == cfg["outlier_network_val"]
    bad_nets = data.loc[(data["size"] > C.OUTLIER_SIZE_GT) & bad, "Net"].unique()
    data = data[~data["Net"].isin(bad_nets)]

    # Time-step window and retained subjects.
    data = data[data["stp"] < cfg["stp_max"]]
    data = data[data["Net2"].isin(C.SUBJECTS_TO_KEEP)]

    # Map network index to presentation number, keep the analysed presentations.
    data["Presentation"] = data["Network"].map(cfg["network_to_presentation"])
    data = data[data["Presentation"].isin(cfg["presentations"])]

    cols = ["Net", "Net2", "Network", "Presentation", "patt_no", "stp", "area", "Stim", "size", "Cond", "File"]
    return data[cols].reset_index(drop=True)


def save_activation(data: pd.DataFrame, paradigm: str) -> Path:
    """Write the processed activation table for a paradigm to CSV."""
    path = processed_path(paradigm)
    path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(path, index=False)
    return path


# ── load (processed → analysis-ready) ────────────────────────────────────────

def add_zero_combos(data: pd.DataFrame, group_cols, patt_range) -> pd.DataFrame:
    """Expand ``data`` so every combination of ``group_cols`` is present.

    Missing combinations are filled with ``size = 0`` (an area that was silent
    for a given pattern/time-step still contributes a zero, not a gap). ``patt_no``
    is forced to the full ``patt_range``; other columns use their observed levels.
    """
    group_cols = tuple(c for c in group_cols if c in data.columns)
    if not group_cols:
        raise ValueError("No valid grouping columns found in `data`.")

    levels = {}
    for c in group_cols:
        if c == "patt_no" and patt_range is not None:
            lo, hi = patt_range
            levels[c] = list(range(lo, hi + 1))
        else:
            levels[c] = pd.unique(data[c].dropna())

    full = (
        pd.MultiIndex.from_product([levels[c] for c in group_cols], names=group_cols)
        .to_frame(index=False)
    )
    merged = full.merge(data[list(group_cols) + ["size"]], on=list(group_cols), how="left")
    merged["size"] = merged["size"].fillna(0).astype(int)
    return merged


def load_activation(paradigm: str) -> pd.DataFrame:
    """Load the analysis-ready activation frame for a paradigm.

    Reads the processed CSV, fills in zero-activation combinations per condition,
    aggregates to one value per (Presentation, Net2, stp, area, Stim, patt_no,
    Cond), and (for P1) tags the speech type and applies the Stim<5 filter.
    """
    cfg = C.PARADIGMS[paradigm]
    path = processed_path(paradigm)
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Build it first with "
            f"`python scripts/build_activation.py --paradigm {paradigm} ...`."
        )
    data = pd.read_csv(path)

    group_cols = ("Net2", "patt_no", "stp", "area", "Stim", "Presentation", "File", "Cond")
    parts = [
        add_zero_combos(data[data["Cond"] == cond], group_cols, cfg["patt_range"])
        for cond in ("Sighted", "Blind")
    ]
    frame = (
        pd.concat(parts, ignore_index=True)
        .groupby(list(group_cols), as_index=False)["size"]
        .mean()
    )

    if cfg["has_spe"]:
        frame["Spe"] = frame["patt_no"].apply(C.spe_of_pattern)
    if cfg["load_stim_lt"] is not None:
        frame = frame[frame["Stim"] < cfg["load_stim_lt"]]

    return frame.reset_index(drop=True)
