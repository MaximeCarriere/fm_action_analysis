"""Aggregate the per-subject data into area-pair connectivity matrices."""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import constants as C


def area_connectivity(data: pd.DataFrame) -> pd.DataFrame:
    """Mean connection strength per (paradigm, condition, presentation, pair).

    Averages the ``sum`` column across subjects, keeping direction (area1->area2).
    """
    return (
        data.groupby(["File", "Cond", "Presentation", "area1", "area2"], as_index=False)["sum"]
        .mean()
    )


def undirected_bidir(area_conn: pd.DataFrame) -> pd.DataFrame:
    """Collapse direction, then re-expand to both directions symmetrically.

    For each unordered pair {a, b} the two directed strengths are summed, and the
    result is written back into both (a, b) and (b, a) so that either orientation
    can be looked up.
    """
    df = area_conn.copy()
    df["area_lo"] = np.minimum(df["area1"], df["area2"])
    df["area_hi"] = np.maximum(df["area1"], df["area2"])

    undirected = (
        df.groupby(["File", "Cond", "Presentation", "area_lo", "area_hi"], as_index=False)["sum"]
        .sum()
        .rename(columns={"area_lo": "area1", "area_hi": "area2"})
    )

    bidir = pd.concat(
        [undirected, undirected.rename(columns={"area1": "area2", "area2": "area1"})],
        ignore_index=True,
    )
    return bidir.drop_duplicates(subset=["File", "Cond", "Presentation", "area1", "area2"])


def get_area_matrix(
    area_conn: pd.DataFrame,
    file_: str,
    cond: str,
    presentation: float,
    areas: list[str] | None = None,
    undirected: bool = False,
) -> pd.DataFrame:
    """Return the area-by-area connectivity matrix for one condition/presentation.

    Missing cells are filled with 0.  When ``undirected`` is True the matrix is
    symmetrised by filling each empty cell from its transpose.
    """
    if areas is None:
        areas = C.AREA_ORDER

    df = area_conn[
        (area_conn["File"] == file_)
        & (area_conn["Cond"] == cond)
        & (area_conn["Presentation"] == presentation)
    ]
    mat = (
        df.pivot_table(index="area1", columns="area2", values="sum", aggfunc="sum")
        .reindex(index=areas, columns=areas)
    )
    if undirected:
        mat = mat.combine_first(mat.T)
    return mat.fillna(0)
