import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from spotvol.beta import BetaResult

# Categorical slots 1 (blue) and 2 (orange) from the validated palette, plus
# neutral ink/grid tones. One hue per entity, held constant across every
# chart: spot is always blue, IV (and anything derived from it) is orange.
SPOT_COLOR = "#2a78d6"
IV_COLOR = "#eb6834"
GRID_COLOR = "#e3e2dd"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"


def _style_ax(ax: Axes) -> None:
    ax.set_axisbelow(True)
    ax.grid(True, linewidth=0.6, color=GRID_COLOR)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(GRID_COLOR)
    ax.tick_params(colors=TEXT_SECONDARY, labelsize=9)
    ax.xaxis.label.set_color(TEXT_SECONDARY)
    ax.yaxis.label.set_color(TEXT_SECONDARY)
    ax.title.set_color(TEXT_PRIMARY)


def plot_price_and_iv(
    features: pd.DataFrame,
    axes: tuple[Axes, Axes] | None = None,
) -> tuple[Axes, Axes]:
    """Spot price and recovered IV over time, as two stacked single-axis
    panels sharing a time axis -- never one plot with two y-scales, since
    the series live on unrelated units and a shared scale would just
    misrepresent one of them."""
    if axes is None:
        _, axes = plt.subplots(2, 1, figsize=(8, 5), sharex=True)
    ax_spot, ax_iv = axes

    ax_spot.plot(features["time"], features["spot"], color=SPOT_COLOR, linewidth=1.5)
    ax_spot.set_ylabel("Spot")
    ax_spot.set_title(
        "Spot price and recovered implied vol", loc="left", fontsize=11, fontweight="bold"
    )

    ax_iv.plot(features["time"], features["iv"], color=IV_COLOR, linewidth=1.5)
    ax_iv.set_ylabel("Implied vol")
    ax_iv.set_xlabel("Time")

    for ax in axes:
        _style_ax(ax)

    return ax_spot, ax_iv


def plot_spot_vol_beta(
    features: pd.DataFrame,
    result: BetaResult,
    ax: Axes | None = None,
) -> Axes:
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 5))

    x = features["d_log_spot"].values
    y = features["d_log_iv"].values

    ax.scatter(x, y, s=14, alpha=0.45, color=SPOT_COLOR, edgecolors="none", zorder=2)

    x_line = np.linspace(x.min(), x.max(), 200)
    y_line = result.intercept + result.beta * x_line
    ax.plot(x_line, y_line, color=IV_COLOR, linewidth=2, zorder=3)

    # Direct-label the fit line itself rather than leaning on a legend box.
    ax.annotate(
        f"β = {result.beta:.2f}\nR² = {result.r_squared:.2f}",
        xy=(x_line[-1], y_line[-1]),
        xytext=(6, 0),
        textcoords="offset points",
        color=IV_COLOR,
        fontsize=9,
        fontweight="bold",
        va="center",
    )

    ax.axhline(0, color=GRID_COLOR, linewidth=0.8, linestyle="--", zorder=1)
    ax.axvline(0, color=GRID_COLOR, linewidth=0.8, linestyle="--", zorder=1)
    ax.set_xlabel("Δ log spot")
    ax.set_ylabel("Δ log IV")
    ax.set_title("Spot-vol beta", loc="left", fontsize=11, fontweight="bold")
    _style_ax(ax)

    return ax


def plot_residuals(
    features: pd.DataFrame,
    result: BetaResult,
    ax: Axes | None = None,
) -> Axes:
    """Fit residuals against Δ log spot -- a pattern here (fanning, curvature)
    would mean the linear beta model is missing something the scatter alone
    can hide under the fit line."""
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 5))

    x = features["d_log_spot"].values
    y = features["d_log_iv"].values
    residuals = y - (result.intercept + result.beta * x)

    ax.scatter(x, residuals, s=14, alpha=0.45, color=SPOT_COLOR, edgecolors="none", zorder=2)
    ax.axhline(0, color=IV_COLOR, linewidth=1.5, zorder=3)

    ax.set_xlabel("Δ log spot")
    ax.set_ylabel("Residual")
    ax.set_title("Fit residuals", loc="left", fontsize=11, fontweight="bold")
    _style_ax(ax)

    return ax


def plot_beta_recovery(
    betas_by_n: dict[int, list[float]],
    true_beta: float,
    ax: Axes | None = None,
) -> Axes:
    """Median recovered beta, with a 16th-84th percentile band across seeds,
    as the option tick count grows -- the pipeline's core validation claim
    made visible: does the estimate converge, and does its spread shrink.

    Median/percentile rather than mean/+-1SE: the synthetic IV path
    occasionally random-walks into its floor and produces a genuine but
    heavy-tailed outlier beta, and a robust summary shows the real
    convergence instead of either hiding those seeds or letting one of them
    dominate the mean.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 5))

    ns = sorted(betas_by_n)
    medians = [float(np.median(betas_by_n[n])) for n in ns]
    lo = [float(np.percentile(betas_by_n[n], 16)) for n in ns]
    hi = [float(np.percentile(betas_by_n[n], 84)) for n in ns]

    ax.axhline(true_beta, color=GRID_COLOR, linewidth=1.2, linestyle="--", zorder=1)
    ax.annotate(
        f"injected β = {true_beta:.2f}",
        xy=(ns[-1], true_beta),
        xytext=(-6, 6),
        textcoords="offset points",
        ha="right",
        color=TEXT_SECONDARY,
        fontsize=9,
    )

    ax.fill_between(ns, lo, hi, color=SPOT_COLOR, alpha=0.15, zorder=1, label="16th-84th pct")
    ax.plot(
        ns, medians, "o-", color=SPOT_COLOR, linewidth=1.5, markersize=6, zorder=2,
        label="median recovered β",
    )

    ax.set_xscale("log")
    ax.set_xlabel("Option ticks (n)")
    ax.set_ylabel("Recovered β")
    ax.set_title("Beta recovery vs. sample size", loc="left", fontsize=11, fontweight="bold")
    ax.legend(framealpha=0.8, fontsize=8, loc="lower left")
    _style_ax(ax)

    return ax


def make_report_figure(features: pd.DataFrame, result: BetaResult) -> Figure:
    """A single hero figure: the raw spot/IV process, the fitted
    relationship, and the fit diagnostic, side by side."""
    fig = plt.figure(figsize=(11, 7), facecolor="#fcfcfb")
    gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 1.6], hspace=0.5, wspace=0.3)

    ax_spot = fig.add_subplot(gs[0, :])
    ax_iv = fig.add_subplot(gs[1, :], sharex=ax_spot)
    ax_scatter = fig.add_subplot(gs[2, 0])
    ax_resid = fig.add_subplot(gs[2, 1])

    plot_price_and_iv(features, axes=(ax_spot, ax_iv))
    plot_spot_vol_beta(features, result, ax=ax_scatter)
    plot_residuals(features, result, ax=ax_resid)

    fig.suptitle(
        "Spot-vol beta: synthetic pipeline validation",
        x=0.02, ha="left", fontsize=13, fontweight="bold", color=TEXT_PRIMARY,
    )

    return fig
