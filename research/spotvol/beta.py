from typing import NamedTuple

import numpy as np
import pandas as pd


class BetaResult(NamedTuple):
    beta: float
    intercept: float
    r_squared: float


def estimate_beta(features: pd.DataFrame) -> BetaResult:
    x = features["d_log_spot"].values
    y = features["d_log_iv"].values

    X = np.column_stack([np.ones_like(x), x])
    coeffs, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    intercept, beta = float(coeffs[0]), float(coeffs[1])

    y_pred = intercept + beta * x
    ss_res = float(np.sum((y - y_pred) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0.0 else float("nan")

    return BetaResult(beta=beta, intercept=intercept, r_squared=r_squared)
