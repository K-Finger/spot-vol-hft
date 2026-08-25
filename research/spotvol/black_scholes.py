import math

def _norm_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

# European option using Black-Scholes model
def black_scholes_price(S: float, K: float, T: float, r: float, sigma: float, is_call: bool) -> float:
    # z-scores measuring distance from strike 
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if is_call:
        return S * _norm_cdf(d1) - K * math.exp(-r * T) * _norm_cdf(d2)
    else:
        # put
        return K * math.exp(-r * T) * _norm_cdf(-d2) - S * _norm_cdf(-d1)

def implied_vol(market_price: float, S: float, K: float, T: float, r: float, is_call: bool) -> float:
    if T <= 0 or market_price <= 0:
        return math.nan

    # option worth right now if exercised
    intrinsic = max(S - K * math.exp(-r * T), 0) if is_call else max(K * math.exp(-r * T) - S, 0)

    # bad data 
    if market_price < intrinsic:
        return math.nan

    # bisection for vol
    lo, hi = 1e-6, 5.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if black_scholes_price(S, K, T, r, mid, is_call) < market_price:
            lo = mid
        else:
            hi = mid

    if hi - lo < 1e-8:
        return mid
    return math.nan
