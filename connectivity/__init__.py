"""Inter-area connectivity analysis for the Blind vs Sighted modelling paper.

Typical use::

    from connectivity import load_dataset, area_connectivity, undirected_bidir
    from connectivity import plotting, stats

    data = load_dataset()
    area_conn = area_connectivity(data)
    area_undirected = undirected_bidir(area_conn)
"""
from __future__ import annotations

from . import constants, plotting, stats
from .aggregate import area_connectivity, get_area_matrix, undirected_bidir
from .data import build_dataset, load_dataset, save_dataset

__all__ = [
    "constants",
    "plotting",
    "stats",
    "area_connectivity",
    "undirected_bidir",
    "get_area_matrix",
    "build_dataset",
    "load_dataset",
    "save_dataset",
]
