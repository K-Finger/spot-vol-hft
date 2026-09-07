import math

from spotvol.black_scholes import black_scholes_price, implied_vol

ATM = dict(S=100.0, K=100.0, T=1.0, r=0.0)
SIGMA = 0.2


def test_round_trip_call():
    price = black_scholes_price(**ATM, sigma=SIGMA, is_call=True)
    assert abs(implied_vol(price, **ATM, is_call=True) - SIGMA) < 1e-6


def test_round_trip_put():
    price = black_scholes_price(**ATM, sigma=SIGMA, is_call=False)
    assert abs(implied_vol(price, **ATM, is_call=False) - SIGMA) < 1e-6


def test_put_call_parity():
    call = black_scholes_price(**ATM, sigma=SIGMA, is_call=True)
    put = black_scholes_price(**ATM, sigma=SIGMA, is_call=False)
    expected = ATM["S"] - ATM["K"] * math.exp(-ATM["r"] * ATM["T"])
    assert abs((call - put) - expected) < 1e-9


def test_expired_returns_nan():
    assert math.isnan(implied_vol(5.0, S=100.0, K=100.0, T=0.0, r=0.0, is_call=True))


def test_negative_price_returns_nan():
    assert math.isnan(implied_vol(-1.0, **ATM, is_call=True))


def test_below_intrinsic_returns_nan():
    assert math.isnan(implied_vol(0.01, S=110.0, K=100.0, T=1.0, r=0.0, is_call=True))
