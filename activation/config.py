"""Repository paths for the activation analysis.

Shares the repo-level ``data/`` and ``figures/`` directories with the
connectivity analysis. The analysis loads pre-processed per-paradigm tables
(``data/activation_p1.csv`` / ``activation_p2.csv``); raw simulation folders are
only needed to (re)build those, via ``scripts/build_activation.py``.
"""
from __future__ import annotations

from pathlib import Path

# Repository root (…/fm_action_analysis).
REPO_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = REPO_ROOT / "data"
FIGURES_DIR = REPO_ROOT / "figures" / "activation"

DATA_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def processed_path(paradigm: str) -> Path:
    """Path to the processed activation table for a paradigm ('P1'/'P2')."""
    return DATA_DIR / f"activation_{paradigm.lower()}.csv"
