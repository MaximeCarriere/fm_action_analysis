"""Shared constants: area ordering, colours, functional groups and index maps.

All modelled areas belong to one of four functional systems (Visual, Motor,
Auditory, Articulatory), each with three areas.  The canonical ``AREA_ORDER``
is used everywhere so that matrices and figures are always laid out the same
way.
"""
from __future__ import annotations

# Canonical order of the 12 modelled areas (grouped by functional system).
AREA_ORDER = [
    "V1", "TO", "AT",      # Visual
    "PFL", "PML", "M1L",   # Motor (lateral)
    "A1", "AB", "PB",      # Auditory
    "PFI", "PMI", "M1I",   # Articulatory (inferior)
]

# Integer index -> area label, as emitted by the raw connections_area_*.txt files.
AREA_INDEX = {i: area for i, area in enumerate(AREA_ORDER)}

# Per-area colours, matching panel A of the manuscript figure.
AREA_COLORS = {
    "V1":  "#1b5e20", "TO":  "#43a047", "AT":  "#80cbc4",
    "PFL": "#fdd835", "PML": "#fb8c00", "M1L": "#5d4037",
    "A1":  "#1a237e", "AB":  "#42a5f5", "PB":  "#81d4fa",
    "PFI": "#e91e63", "PMI": "#ff8a80", "M1I": "#d32f2f",
}

# Functional groups for figure brackets: (label, start_idx, end_idx, colour).
GROUPS = [
    ("Visual",       0,  3, "#2e7d32"),
    ("Motor",        3,  6, "#6d4c41"),
    ("Auditory",     6,  9, "#1565c0"),
    ("Articulatory", 9, 12, "#c2185b"),
]

# Functional groups as area-label lists (used by the statistics).
GROUPS_AREAS = {
    "Visual":       ["V1", "TO", "AT"],
    "Motor":        ["PFL", "PML", "M1L"],
    "Auditory":     ["A1", "AB", "PB"],
    "Articulatory": ["PFI", "PMI", "M1I"],
}

# Condition colours for bar plots.
COND_PALETTE = {
    "Blind":   "#6A00FF",   # electric purple
    "Sighted": "#FFD500",   # electric yellow
}

# Raw per-subject connection files, keyed by paradigm.
CONNECTION_FILES = {
    "P1": "connections_area_P1.txt",
    "P2": "connections_area_P2.txt",
}

# Network-index -> presentation number, per paradigm.
NETWORK_TO_PRESENTATION = {
    "P1": {0: 0, 1: 10, 2: 20, 3: 50, 4: 100, 5: 500, 6: 1000, 7: 3000, 8: 5000},
    "P2": {
        0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 10, 7: 15,
        8: 20, 9: 25, 10: 30, 11: 35, 12: 40, 13: 45, 14: 50,
    },
}

# Subjects (network index) retained for analysis.
SUBJECTS_TO_KEEP = [
    1, 2, 3, 5, 6, 7, 9, 10, 11, 12, 13, 14,
    18, 19, 20, 22, 24, 25, 27, 28, 29, 30,
]
