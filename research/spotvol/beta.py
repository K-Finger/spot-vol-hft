import numpy as np
import pandas as pd


def estimate_beta(features: pd.DataFrame) -> float:
    x = features["d_log_spot"].values
    y = features["d_log_iv"].values
    X = np.column_stack([np.ones_like(x), x])
    coeffs, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    return float(coeffs[1])
