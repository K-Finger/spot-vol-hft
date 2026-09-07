import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from spotvol.beta import BetaResult


def plot_spot_vol_beta(
    features: pd.DataFrame,
    result: BetaResult,
    ax: Axes | None = None,
) -> Axes:
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 5))

    x = features["d_log_spot"].values
    y = features["d_log_iv"].values

    ax.scatter(x, y, s=10, alpha=0.4, color="steelblue", label="observations")

    x_line = np.linspace(x.min(), x.max(), 200)
    ax.plot(
        x_line,
        result.intercept + result.beta * x_line,
        color="tomato",
        linewidth=1.5,
        label=f"β = {result.beta:.3f},  R² = {result.r_squared:.3f}",
    )

    ax.axhline(0, color="gray", linewidth=0.5, linestyle="--")
    ax.axvline(0, color="gray", linewidth=0.5, linestyle="--")
    ax.set_xlabel("Δ log Spot")
    ax.set_ylabel("Δ log IV")
    ax.legend(framealpha=0.8)

    return ax
