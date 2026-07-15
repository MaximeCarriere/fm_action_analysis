"""Constants for the time-course activation (TCA) analysis.

Activation is measured as the number of active neurons ("size") per area at each
simulation time-step, for two paradigms:

* **P1** — Phase 1 (isolated word/action learning). Patterns split into
  *Action* (patt_no 1-6) and *WF* (word-form, patt_no 7-12). Analysed at
  presentation 5000.
* **P2** — Phase 2 (sentence context). Word patterns (patt_no 7-12), analysed
  across presentations, with statistics at presentation 50.
"""
from __future__ import annotations

# Canonical order of the 12 modelled areas (index -> label).
AREA_ORDER = [
    "V1", "TO", "AT",      # Visual
    "PFL", "PML", "M1L",   # Motor
    "A1", "AB", "PB",      # Auditory
    "PFI", "PMI", "M1I",   # Articulatory
]
AREA_INDEX = {i: a for i, a in enumerate(AREA_ORDER)}

# Per-area colours (from the original notebook).
AREA_COLORS = {
    "V1": "darkgreen", "TO": "mediumseagreen", "AT": "lightgreen",
    "PFL": "gold", "PML": "orange", "M1L": "darkgoldenrod",
    "A1": "darkblue", "AB": "steelblue", "PB": "darkturquoise",
    "PFI": "deeppink", "PMI": "lightpink", "M1I": "crimson",
}

# Condition colours for the time-course lines.
COND_PALETTE = {"Blind": "#6A00FF", "Sighted": "#FFD500"}
COND_ORDER = ["Sighted", "Blind"]

# Area-index groupings used by the statistics (repeated-measures factors).
SYSTEM_BY_AREA = {
    **{a: "Visual" for a in (0, 1, 2)},
    **{a: "Motor" for a in (3, 4, 5)},
    **{a: "Auditory" for a in (6, 7, 8)},
    **{a: "Articulatory" for a in (9, 10, 11)},
}
ROLE_BY_AREA = {
    **{a: "Primary" for a in (0, 5, 6, 11)},
    **{a: "Secondary" for a in (1, 4, 7, 10)},
    **{a: "Central" for a in (2, 3, 8, 9)},
}
PERI_EXTRA_BY_AREA = {
    **{a: "Extra" for a in range(0, 6)},
    **{a: "Peri" for a in range(6, 12)},
}

# Subjects (network index) retained for analysis.
SUBJECTS_TO_KEEP = [
    1, 2, 3, 5, 6, 7, 9, 10, 11, 12, 13, 14,
    18, 19, 20, 22, 24, 25, 27, 28, 29, 30,
]

# Per-paradigm configuration.
PARADIGMS = {
    "P1": {
        "raw_file": "neurons_CA_detailed_Phase_1_aud.txt",
        "stim_min": None,                       # no Stim filter on load
        "network_to_presentation": {0: 10, 1: 50, 2: 1000, 3: 3000, 4: 5000},
        "outlier_network_op": ">",              # drop nets with size>80 & Network>5
        "outlier_network_val": 5,
        "stp_max": 38,                          # keep stp < 38
        "presentations": [5000],                # presentations retained
        "patt_range": (1, 12),                  # zero-combo pattern range
        "has_spe": True,                        # split Action / WF
        "load_stim_lt": 5,                      # keep Stim < 5 for all P1 analysis
        "plot_stim_lt": None,                   # no extra plot-only Stim filter
        "analysis_presentation": 5000,          # presentation used for window + stats
    },
    "P2": {
        "raw_file": "neurons_CA_detailed_Phase_2_1000.txt",
        "stim_min": 1,                          # keep Stim > 1 on load
        "network_to_presentation": {
            0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 10, 7: 15, 8: 20, 9: 25, 10: 50,
        },
        "outlier_network_op": "==",             # drop nets with size>80 & Network==10
        "outlier_network_val": 10,
        "stp_max": 35,                          # keep stp < 35
        "presentations": [0, 5, 10, 20, 25, 50],
        "patt_range": (7, 12),
        "has_spe": False,
        "load_stim_lt": None,                   # keep all Stim>1 for stats
        "plot_stim_lt": 4,                      # plots only: keep Stim < 4
        "analysis_presentation": 50,
    },
}

OUTLIER_SIZE_GT = 80   # size threshold for dropping runaway networks


def spe_of_pattern(patt_no: int) -> str:
    """Map a pattern number to its speech type (P1 only)."""
    return "Action" if patt_no < 7 else "WF"
