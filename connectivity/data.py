"""Build, save and load the connectivity dataset.

The heavy step (reading every subject folder) is done once by
``build_dataset`` and written to ``data/connectivity_data.csv`` via
``save_dataset``.  Day-to-day analysis just calls ``load_dataset``.

Build pipeline:
    1. Read ``connections_area_P1.txt`` / ``connections_area_P2.txt`` for every
       Sighted and Blind subject folder.
    2. Keep only the retained subjects.
    3. Map network index -> presentation number and area index -> area label.
    4. Replace the P1 presentation-0 rows with the pre-computed tally baseline.

The resulting frame has one row per (paradigm, condition, subject, presentation,
area1, area2) with the connection strength in column ``sum``.
"""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

from . import constants as C
from .config import PROCESSED_DATA


def get_subfolders(directory: str | Path) -> list[str]:
    """Return the sorted list of immediate sub-directories of ``directory``."""
    subfolders = [f.path for f in os.scandir(directory) if f.is_dir()]
    subfolders.sort()
    return subfolders


def _load_condition(result_dirs: list[str], condition: str) -> list[pd.DataFrame]:
    """Read every paradigm file for a set of subject folders in one condition."""
    frames = []
    for paradigm, filename in C.CONNECTION_FILES.items():
        for net_dir in result_dirs:
            df = pd.read_csv(os.path.join(net_dir, filename), sep=r" |\t", engine="python")
            df["File"] = paradigm
            df["Net"] = net_dir
            df["Cond"] = condition
            frames.append(df)
    return frames


def load_raw_connections(sighted_dir: str | Path, blind_dir: str | Path) -> pd.DataFrame:
    """Concatenate the raw connection tables for both conditions."""
    frames = []
    frames += _load_condition(get_subfolders(sighted_dir), "Sighted")
    frames += _load_condition(get_subfolders(blind_dir), "Blind")
    return pd.concat(frames, ignore_index=True)


def filter_subjects(data: pd.DataFrame) -> pd.DataFrame:
    """Keep only the retained subjects (network index from the folder name)."""
    data = data.copy()
    data["Net2"] = data["Net"].str[-2:].astype(int)
    return data[data["Net2"].isin(C.SUBJECTS_TO_KEEP)]


def map_labels(data: pd.DataFrame) -> pd.DataFrame:
    """Map network index -> presentation and area index -> area label."""
    data = data.copy()
    for paradigm, mapping in C.NETWORK_TO_PRESENTATION.items():
        rows = data["File"] == paradigm
        data.loc[rows, "Presentation"] = data.loc[rows, "Network"].map(mapping)
    data["area1"] = data["area1"].map(C.AREA_INDEX)
    data["area2"] = data["area2"].map(C.AREA_INDEX)
    return data


def load_tally_baseline(tally_baseline: str | Path) -> pd.DataFrame:
    """Load the pre-computed P1 presentation-0 baseline for both conditions.

    The baseline is condition-independent, so it is duplicated into Sighted and
    Blind copies.
    """
    base = pd.read_csv(tally_baseline).drop(columns="Unnamed: 0")
    base["File"] = "P1"
    sighted = base.copy()
    sighted["Cond"] = "Sighted"
    blind = base.copy()
    blind["Cond"] = "Blind"
    return pd.concat([sighted, blind], ignore_index=True)


def build_dataset(
    sighted_dir: str | Path,
    blind_dir: str | Path,
    tally_baseline: str | Path,
) -> pd.DataFrame:
    """Read the raw simulation folders and return the processed dataset."""
    data = load_raw_connections(sighted_dir, blind_dir)
    data = filter_subjects(data)
    data = map_labels(data)

    # Replace the modelled P1 presentation-0 rows with the tally baseline.
    data = data[~((data["File"] == "P1") & (data["Presentation"] == 0))]
    data = pd.concat([data, load_tally_baseline(tally_baseline)], ignore_index=True)
    return data.reset_index(drop=True)


def save_dataset(data: pd.DataFrame, path: str | Path = PROCESSED_DATA) -> Path:
    """Write the processed dataset to CSV and return its path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(path, index=False)
    return path


def load_dataset(path: str | Path = PROCESSED_DATA) -> pd.DataFrame:
    """Load the processed dataset produced by :func:`build_dataset`."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Build it first with `python scripts/build_dataset.py`."
        )
    return pd.read_csv(path)
