"""Repository paths.

The analysis reads a single pre-processed table, ``data/connectivity_data.csv``.
Raw simulation folders are only needed once, to (re)build that table — see
``scripts/build_dataset.py`` — and their locations are passed to that script
rather than stored here.
"""
from __future__ import annotations

from pathlib import Path

# Repository root (…/connectivity_analysis).
REPO_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = REPO_ROOT / "data"
FIGURES_DIR = REPO_ROOT / "figures" / "connectivity"

# The single processed dataset the analysis loads.
PROCESSED_DATA = DATA_DIR / "connectivity_data.csv"

DATA_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
