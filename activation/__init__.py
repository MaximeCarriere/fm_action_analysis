"""Time-course activation (TCA) analysis for the Blind vs Sighted modelling paper.

Typical use::

    from activation import load_activation, activation_window, plotting, stats

    frame = load_activation("P1")
    win = activation_window(frame, presentation=5000, spe="WF")
    plotting.plot_timecourse_grid(frame, "P1", 5000, spe="WF", window=win)
    stats.activation_rm_anova(frame, win, presentation=5000, spe="WF")
"""
from __future__ import annotations

from . import constants, plotting, stats
from .data import build_activation, load_activation, save_activation
from .window import activation_window

__all__ = [
    "constants",
    "plotting",
    "stats",
    "build_activation",
    "load_activation",
    "save_activation",
    "activation_window",
]
