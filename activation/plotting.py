"""Time-course activation figure: a 2×6 grid of per-area response curves.

Each panel shows the number of active neurons over time-steps for Blind vs
Sighted, with the half-max response window shaded and the stimulated area marked.

Colour convention (shared with the connectivity figures): Blind = purple,
Sighted = yellow. The original P1 notebook cell paired ``hue_order``/``palette``
positionally in a way that swapped these; here the mapping is by condition name
so both figure families agree.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

from . import constants as C
from .config import FIGURES_DIR
from .window import activation_window

# Which area receives external stimulation, per speech type.
_STIM_TARGET = {"WF": "A1", "Action": "M1L"}
# Default axis limits per paradigm.
_LIMITS = {"P1": {"xlim": (5, 25), "ylim": (0, 25)},
           "P2": {"xlim": (0, 35), "ylim": (0, 30)}}


def _default_title(paradigm, spe, presentation):
    if paradigm == "P1":
        return ("Auditory Word Recognition ·  Time Course Phase 1" if spe == "WF"
                else "Action Execution ·  Time Course Phase 1")
    return f"Time Course Phase 2 ·  Presentation {presentation}"


def plot_timecourse_grid(frame, paradigm, presentation, *, spe=None, window=None,
                         stim_lt="auto", xlim=None, ylim=None, title=None,
                         save_path=None, fontsize=26):
    """Plot the 2×6 per-area activation time-course grid.

    Parameters
    ----------
    frame : analysis frame from ``load_activation``.
    paradigm : 'P1' or 'P2'.
    presentation : presentation to plot.
    spe : speech type (P1: 'WF' or 'Action'); ignored for P2.
    window : half-max windows (from ``activation_window``); computed if None.
    stim_lt : keep Stim < this in the plotted subset ('auto' uses the paradigm
        default, None keeps all).
    """
    cfg = C.PARADIGMS[paradigm]
    if not cfg["has_spe"]:
        spe = None
    if window is None:
        window = activation_window(frame, presentation=presentation, spe=spe)
    if stim_lt == "auto":
        stim_lt = cfg["plot_stim_lt"]
    lim = _LIMITS[paradigm]
    xlim = xlim or lim["xlim"]
    ylim = ylim or lim["ylim"]

    sns.set_theme(context="talk", style="whitegrid", rc={
        "font.family": "DejaVu Sans", "axes.spines.top": False,
        "axes.spines.right": False, "axes.edgecolor": "#3a3a3a",
        "axes.linewidth": 1.2, "grid.linewidth": 0.6, "grid.color": "#d9d9d9",
        "axes.labelcolor": "#212121", "xtick.color": "#212121", "ytick.color": "#212121",
    })

    fig, axes = plt.subplots(2, 6, figsize=(22, 10),
                             gridspec_kw={"wspace": 0.07, "hspace": 0.13})
    handles = labels = None

    for i in range(12):
        ax = axes[i // 6, i % 6]
        subset = frame[(frame["area"] == i) & (frame["Presentation"] == presentation)]
        if spe is not None:
            subset = subset[subset["Spe"] == spe]
        if stim_lt is not None:
            subset = subset[subset["Stim"] < stim_lt]

        if not subset.empty:
            sns.lineplot(
                data=subset, x="stp", y="size", hue="Cond",
                hue_order=C.COND_ORDER, palette=C.COND_PALETTE,
                ax=ax, linewidth=4, marker="o", markersize=8,
                markeredgecolor="black", markeredgewidth=0.5,
            )
            if handles is None:
                handles, labels = ax.get_legend_handles_labels()
            if i in window.index:
                w = window.loc[i]
                ax.axvspan(w["half_max_stp"], w["half_max_stp_2"], alpha=0.1, color="red")

        ax.set(xlabel="", ylabel="", xlim=xlim, ylim=ylim)
        ax.set_title(C.AREA_ORDER[i], fontsize=fontsize + 4, fontweight="bold")
        ax.tick_params(axis="x", labelrotation=70, labelsize=fontsize - 2 if i > 5 else 0)
        ax.tick_params(axis="y", labelsize=fontsize - 2 if i in (0, 6) else 0)
        if ax.legend_:
            ax.legend_.remove()

    _mark_stim_site(axes, spe or "WF", fontsize)

    if handles:
        fig.legend(handles, labels, title="Model", title_fontsize=fontsize,
                   fontsize=fontsize - 2, loc="center right",
                   bbox_to_anchor=(0.90, 1), ncol=2, borderaxespad=0.1)
    fig.suptitle(title or _default_title(paradigm, spe, presentation),
                 fontsize=fontsize + 5, fontweight="bold", x=0.4, y=1.02, ha="center")
    fig.supylabel("Number of Neurons", x=0.07, fontsize=fontsize)
    fig.supxlabel("Time-Step", fontsize=fontsize)

    if save_path is None:
        tag = f"{paradigm}_{spe}" if spe else f"{paradigm}_P{presentation}"
        save_path = FIGURES_DIR / f"timecourse_{tag}.jpg"
    save_path = Path(save_path)
    if not save_path.is_absolute():
        save_path = FIGURES_DIR / save_path
    fig.savefig(save_path, bbox_inches="tight", dpi=300, format=save_path.suffix.lstrip("."))
    print(f"Saved → {save_path}")
    plt.show()


def _mark_stim_site(axes, spe, fontsize):
    """Draw a red arrow into the panel of the stimulated area."""
    target = _STIM_TARGET.get(spe)
    if target is None or target not in C.AREA_ORDER:
        return
    idx = C.AREA_ORDER.index(target)
    ax = axes[idx // 6, idx % 6]
    ax.annotate("", xy=(-0.01, 0.5), xytext=(-0.22, 0.5),
                xycoords="axes fraction", textcoords="axes fraction",
                arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.3",
                                color="red", lw=4.5), annotation_clip=False)
    ax.text(-0.24, 0.5, "Stim", transform=ax.transAxes, fontsize=fontsize - 8,
            color="red", fontweight="bold", ha="right", va="center", clip_on=False)
