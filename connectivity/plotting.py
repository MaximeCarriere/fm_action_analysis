"""Publication figures: connectivity heatmaps and change bar plots.

All heatmaps share a common look (viridis / coolwarm, coloured axis labels and
functional-group brackets) applied by :func:`_decorate_area_heatmap`.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from . import constants as C
from .aggregate import get_area_matrix
from .config import FIGURES_DIR

# Offsets (axes fraction) for the group brackets.
_BAR_X_LEFT, _TEXT_X_LEFT = -0.13, -0.17
_BAR_Y_BOT, _TEXT_Y_BOT = -0.12, -0.14


def _triangle_mask(mat: pd.DataFrame, triangle: str | None) -> np.ndarray | None:
    """Boolean mask that hides the unwanted triangle of a square matrix."""
    if triangle == "upper":
        return np.tril(np.ones_like(mat, dtype=bool), k=-1)
    if triangle == "lower":
        return np.triu(np.ones_like(mat, dtype=bool), k=1)
    if triangle is None:
        return None
    raise ValueError("triangle must be 'upper', 'lower' or None")


def _decorate_area_heatmap(ax, areas, title, colour_labels=True, show_groups=True):
    """Apply the shared styling (title, coloured labels, group brackets)."""
    n = len(areas)
    cbar = ax.collections[0].colorbar
    if cbar is not None:
        cbar.ax.tick_params(labelsize=17)

    ax.set_title(title, fontsize=25, fontweight="bold", pad=14)
    ax.set_xlabel("")
    ax.set_ylabel("")

    ax.tick_params(axis="x", rotation=45, labelsize=19)
    ax.tick_params(axis="y", rotation=0, labelsize=19)
    for lbl in ax.get_xticklabels():
        if colour_labels:
            lbl.set_color(C.AREA_COLORS.get(lbl.get_text(), "black"))
        lbl.set_fontweight("bold")
        lbl.set_ha("right")
    for lbl in ax.get_yticklabels():
        if colour_labels:
            lbl.set_color(C.AREA_COLORS.get(lbl.get_text(), "black"))
        lbl.set_fontweight("bold")

    if not show_groups:
        return
    for label, start, end, color in C.GROUPS:
        mid = (start + end) / 2
        ax.plot([_BAR_X_LEFT, _BAR_X_LEFT], [1 - start / n, 1 - end / n],
                transform=ax.transAxes, color=color, linewidth=7,
                solid_capstyle="butt", clip_on=False)
        ax.text(_TEXT_X_LEFT, 1 - mid / n, label, transform=ax.transAxes,
                ha="center", va="center", rotation=90,
                fontsize=15, fontweight="bold", color=color)
        ax.plot([start / n, end / n], [_BAR_Y_BOT, _BAR_Y_BOT],
                transform=ax.transAxes, color=color, linewidth=7,
                solid_capstyle="butt", clip_on=False)
        ax.text(mid / n, _TEXT_Y_BOT, label, transform=ax.transAxes,
                ha="center", va="top",
                fontsize=15, fontweight="bold", color=color)


def _save(fig, save_path: str | Path | None, default_name: str):
    """Save ``fig`` (into ``figures/`` by default) and report the location."""
    if save_path is None:
        save_path = FIGURES_DIR / default_name
    save_path = Path(save_path)
    if not save_path.is_absolute():
        save_path = FIGURES_DIR / save_path
    fig.savefig(save_path, bbox_inches="tight", dpi=300, format=save_path.suffix.lstrip("."))
    print(f"Saved → {save_path}")


def _heatmap(mat, mask, *, cmap, center=None, vmin=None, vmax=None, annotate=False, fmt=".2f"):
    """Draw one styled square heatmap and return (fig, ax)."""
    fig, ax = plt.subplots(figsize=(9.5, 8.5))
    sns.heatmap(
        mat, mask=mask, cmap=cmap, center=center, vmin=vmin, vmax=vmax,
        square=True, annot=annotate, fmt=fmt,
        linewidths=0.5, linecolor="white", cbar=True,
        annot_kws={"size": 20}, cbar_kws={"shrink": 0.8}, ax=ax,
    )
    return fig, ax


def plot_connectivity_triangle(
    area_df, file_, cond, presentation, *,
    vmax=None, vmin=None, triangle="lower", annotate=False, fmt=".2f",
    colour_labels=True, show_groups=True, undirected=True, save_path=None,
):
    """Absolute connectivity matrix for one condition/presentation (viridis)."""
    mat = get_area_matrix(area_df, file_, cond, presentation,
                          areas=C.AREA_ORDER, undirected=undirected)
    mask = _triangle_mask(mat, triangle)
    fig, ax = _heatmap(mat, mask, cmap="viridis", vmin=vmin, vmax=vmax,
                       annotate=annotate, fmt=fmt)
    _decorate_area_heatmap(ax, C.AREA_ORDER,
                           f"Area connectivity ·  Presentation {presentation}  ·  {cond}",
                           colour_labels, show_groups)
    plt.tight_layout()
    _save(fig, save_path, f"connectivity_{file_}_P{presentation}_{cond}.jpg")
    plt.show()
    return mat


def plot_diff_blind_sighted_triangle(
    area_df, file_, presentation=0, *,
    vmax=None, vmin=None, triangle="lower", annotate=False, fmt=".2f",
    colour_labels=True, show_groups=True, undirected=True, save_path=None,
):
    """Blind − Sighted connectivity difference at one presentation (coolwarm)."""
    mat_b = get_area_matrix(area_df, file_, "Blind", presentation,
                            areas=C.AREA_ORDER, undirected=undirected)
    mat_s = get_area_matrix(area_df, file_, "Sighted", presentation,
                            areas=C.AREA_ORDER, undirected=undirected)
    diff = mat_b - mat_s
    mask = _triangle_mask(diff, triangle)
    fig, ax = _heatmap(diff, mask, cmap="coolwarm", center=0, vmin=vmin, vmax=vmax,
                       annotate=annotate, fmt=fmt)
    _decorate_area_heatmap(ax, C.AREA_ORDER,
                           f"Δ Blind − Sighted connectivity  ·  Presentation {presentation}",
                           colour_labels, show_groups)
    plt.tight_layout()
    _save(fig, save_path, f"blind_minus_sighted_P{presentation}_{file_}.jpg")
    plt.show()
    return diff


def plot_change_heatmap(
    area_df, file_, cond, *, v1=100, v2=5000,
    vmax=None, vmin=None, triangle=None, annotate=False, fmt=".2f",
    colour_labels=True, show_groups=True, undirected=True, save_path=None,
):
    """Connectivity change (P{v2} − P{v1}) within one condition (coolwarm)."""
    mat1 = get_area_matrix(area_df, file_, cond, v1, areas=C.AREA_ORDER, undirected=undirected)
    mat2 = get_area_matrix(area_df, file_, cond, v2, areas=C.AREA_ORDER, undirected=undirected)
    diff = (mat2 - mat1).reindex(index=C.AREA_ORDER, columns=C.AREA_ORDER).fillna(0)
    mask = _triangle_mask(diff, triangle)
    fig, ax = _heatmap(diff, mask, cmap="coolwarm", center=0, vmin=vmin, vmax=vmax,
                       annotate=annotate, fmt=fmt)
    _decorate_area_heatmap(ax, C.AREA_ORDER,
                           f"Connectivity change  ({v2} − {v1})   ·  {cond}",
                           colour_labels, show_groups)
    plt.tight_layout()
    _save(fig, save_path, f"connectivity_change_{v2}-{v1}_{file_}_{cond}.jpg")
    plt.show()
    return diff


def plot_change_contrast_heatmap(
    area_df, file_, *, cond_a="Blind", cond_b="Sighted", v1=100, v2=5000,
    vmax=None, vmin=None, triangle=None, annotate=False, fmt=".2f",
    colour_labels=True, show_groups=True, undirected=True, save_path=None,
):
    """Contrast of the two conditions' changes: ΔA(v2−v1) − ΔB(v2−v1)."""
    a1 = get_area_matrix(area_df, file_, cond_a, v1, areas=C.AREA_ORDER, undirected=undirected)
    a2 = get_area_matrix(area_df, file_, cond_a, v2, areas=C.AREA_ORDER, undirected=undirected)
    delta_a = (a2 - a1).reindex(index=C.AREA_ORDER, columns=C.AREA_ORDER).fillna(0)
    b1 = get_area_matrix(area_df, file_, cond_b, v1, areas=C.AREA_ORDER, undirected=undirected)
    b2 = get_area_matrix(area_df, file_, cond_b, v2, areas=C.AREA_ORDER, undirected=undirected)
    delta_b = (b2 - b1).reindex(index=C.AREA_ORDER, columns=C.AREA_ORDER).fillna(0)
    contrast = delta_a - delta_b
    mask = _triangle_mask(contrast, triangle)
    fig, ax = _heatmap(contrast, mask, cmap="coolwarm", center=0, vmin=vmin, vmax=vmax,
                       annotate=annotate, fmt=fmt)
    _decorate_area_heatmap(ax, C.AREA_ORDER,
                           f"Δ ({cond_a} (P{v2}−P{v1})  −  {cond_b} (P{v2}−P{v1}))",
                           colour_labels, show_groups)
    plt.tight_layout()
    _save(fig, save_path, f"contrast_{cond_a}-{cond_b}_P{v2}-P{v1}_{file_}.jpg")
    plt.show()
    return contrast


def plot_delta_barplot(
    data, file_, source_areas, *, v1=0, v2=50, target_areas=None,
    title=None, save_path=None,
):
    """Per-network connectivity change (P{v2} − P{v1}) as grouped bars.

    One subplot per *from* area in ``source_areas``; bars show mean ± SE across
    networks for each *to* area, split by condition.  Restricts the analysis to
    connections among ``target_areas`` (defaults to ``source_areas``).
    """
    if target_areas is None:
        target_areas = source_areas

    sub = data[
        (data["File"] == file_)
        & data["area1"].isin(source_areas)
        & data["area2"].isin(target_areas)
    ].copy()

    pivot = (
        sub.pivot_table(index=["Cond", "Net", "area1", "area2"],
                        columns="Presentation", values="sum", aggfunc="first")
        .reset_index()
        .dropna(subset=[v1, v2])
    )
    pivot["delta"] = pivot[v2] - pivot[v1]

    fig, axes = plt.subplots(1, len(source_areas), figsize=(2.5 * len(source_areas), 3),
                             sharey=True, squeeze=False)
    axes = axes[0]

    for ax, src in zip(axes, source_areas):
        part = pivot[pivot["area1"] == src]
        if part.empty:
            ax.set_visible(False)
            continue
        sns.barplot(
            data=part, x="area2", y="delta", hue="Cond",
            hue_order=["Blind", "Sighted"], palette=C.COND_PALETTE,
            errorbar="se", ax=ax,
        )
        ax.axhline(0, color="black", linewidth=1)
        ax.set_title(f"From {src}")
        ax.set_xlabel("To area")
        ax.set_ylabel(f"Δ conn ({v2} − {v1})")
        ax.tick_params(axis="x", rotation=45)
        if ax.legend_ is not None:
            ax.legend_.remove()

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, title="Condition", loc="upper right",
               bbox_to_anchor=(1.05, 1.1))
    fig.suptitle(title or f"Connectivity change ({v2} − {v1})  ·  {file_}", y=1.03)
    plt.tight_layout()
    _save(fig, save_path, f"delta_bars_{file_}_{'-'.join(source_areas)}_{v2}-{v1}.jpg")
    plt.show()
