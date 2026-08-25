# Generates synthetic tick data with a known beta 
# Used to VALIDATE the pipeline end-to-end by seeing if recovered beta matches

import numpy as np
import pandas as pd
from spotvol.black_scholes import black_scholes_price

"""
    Returns two dataframes:

    spot_df (time, spot, iv)
    option_df (time, bid, ask, strike, expiry)
"""
def generate(
    n_spot: int = 500,
    n_option: int = 300,
    S0: float = 100.0,
    iv0: float = 0.20,
    beta: float = -3.0,
    spot_vol: float = 0.01,
    iv_noise: float = 0.005,
    r: float = 0.0,
    K: float = 100.0,
    T: float = 1.0,
    spread: float = 0.05,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)

    # spot ticks at irregular times
    spot_times = np.cumsum(rng.exponential(1.0, n_spot))
    log_returns = rng.normal(0, spot_vol, n_spot)
    spot_prices = S0 * np.exp(np.cumsum(log_returns))

    # IV driven by spot moves with known beta
    iv_values = np.empty(n_spot)
    iv_values[0] = iv0
    for i in range(1, n_spot):
        d_log_iv = beta * log_returns[i] + rng.normal(0, iv_noise)
        iv_values[i] = max(iv_values[i - 1] * np.exp(d_log_iv), 1e-4)

    spot_df = pd.DataFrame({"time": spot_times, "spot": spot_prices, "iv": iv_values})

    # option ticks at different irregular times within the same window
    opt_times = np.sort(rng.uniform(spot_times[0], spot_times[-1], n_option))
    # snap each option time to nearest spot tick to get a sensible price
    idx = np.searchsorted(spot_times, opt_times).clip(0, n_spot - 1)
    mids = np.array([
        black_scholes_price(spot_prices[i], K, T, r, iv_values[i], is_call=True)
        for i in idx
    ])
    option_df = pd.DataFrame({
        "time": opt_times,
        "bid": mids - spread / 2,
        "ask": mids + spread / 2,
        "strike": K,
        "expiry": T,
    })

    return spot_df, option_df
