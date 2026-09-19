import numpy as np
import pandas as pd

from spotvol.black_scholes import implied_vol


def _mid(aligned: pd.DataFrame) -> pd.Series:
    return (aligned["bid"] + aligned["ask"]) / 2


def _invert_iv(
    aligned: pd.DataFrame,
    mids: pd.Series,
    is_call: bool = True,
) -> pd.Series:
    rows = zip(mids, aligned["spot"], aligned["strike"], aligned["expiry"])
    ivs = [implied_vol(m, s, k, t, 0.0, is_call) for m, s, k, t in rows]
    return pd.Series(ivs, index=aligned.index)


def build_features(aligned: pd.DataFrame, is_call: bool = True) -> pd.DataFrame:
    mid = _mid(aligned)
    iv = _invert_iv(aligned, mid, is_call=is_call)

    return pd.DataFrame({
        "time": aligned["time"],
        "spot": aligned["spot"],
        "mid": mid,
        "iv": iv,
        "d_log_spot": np.log(aligned["spot"] / aligned["spot"].shift(1)),
        "d_log_iv": np.log(iv / iv.shift(1)),
    }).dropna()
