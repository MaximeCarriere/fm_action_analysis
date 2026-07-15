"""Half-maximum activation-window detection.

For each area, the mean activation time-course (averaged over conditions) rises
to a peak and falls back. The *response window* is the full width at half maximum:
the interval between the last ascending time-step below half-max and the last
descending time-step above half-max. This window is used both to shade the
time-course plots and to define the interval over which activation is averaged
for the statistics.
"""
from __future__ import annotations

import pandas as pd


def activation_window(frame: pd.DataFrame,
                      presentation: float | None = None,
                      spe: str | None = None) -> pd.DataFrame:
    """Return the half-max activation window per area.

    Parameters
    ----------
    frame : analysis frame from ``load_activation``.
    presentation : restrict to this presentation (None = use all present).
    spe : restrict to this speech type (P1 only; None = ignore).

    Returns a DataFrame indexed by ``area`` with columns ``max``, ``half_max``,
    ``max_stp``, ``half_max_stp`` (descending crossing), ``half_max_stp_2``
    (ascending crossing). Areas whose time-course never crosses half-max on both
    sides are omitted.
    """
    dfS = frame
    if presentation is not None:
        dfS = dfS[dfS["Presentation"] == presentation]
    if spe is not None and "Spe" in dfS.columns:
        dfS = dfS[dfS["Spe"] == spe]

    # Mean time-course per area, averaging conditions equally.
    per_cond = dfS.groupby(["Cond", "area", "stp"])["size"].mean().reset_index()
    a1 = per_cond.groupby(["area", "stp"])["size"].mean().reset_index()
    max_value = a1.groupby("area")["size"].max()

    rows = []
    for area in a1["area"].unique():
        eph = a1[a1["area"] == area]
        eph_max = max_value[area]
        eph_half = eph_max * 0.5
        max_stp = eph[eph["size"] == eph_max].iloc[-1]["stp"]
        try:
            hi = int(eph[(eph["size"] > eph_half) & (eph["stp"] > max_stp)].iloc[-1]["stp"])
            lo = int(eph[(eph["size"] < eph_half) & (eph["stp"] < max_stp)].iloc[-1]["stp"])
        except IndexError:
            continue
        rows.append({
            "area": area,
            "max": eph_max,
            "half_max": eph_half,
            "max_stp": max_stp,
            "half_max_stp": hi,
            "half_max_stp_2": lo,
        })

    return pd.DataFrame(rows).set_index("area", drop=False)
