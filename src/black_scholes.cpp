#include "spotvol/black_scholes.hpp"

#include <algorithm>
#include <cmath>
#include <limits>

namespace spotvol {

static double normCdf(double x) {
    return 0.5 * (1.0 + std::erf(x / std::sqrt(2.0)));
}

double bsPrice(double S, double K, double T, double r, double sigma, bool isCall) {
    double sqrtT = std::sqrt(T);
    double d1 = (std::log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * sqrtT);
    double d2 = d1 - sigma * sqrtT;
    if (isCall) {
        return S * normCdf(d1) - K * std::exp(-r * T) * normCdf(d2);
    }
    return K * std::exp(-r * T) * normCdf(-d2) - S * normCdf(-d1);
}

double impliedVol(double marketPrice, double S, double K, double T, double r, bool isCall) {
    if (T <= 0.0 || marketPrice <= 0.0) {
        return std::numeric_limits<double>::quiet_NaN();
    }

    double disc = std::exp(-r * T);
    double intrinsic = isCall
        ? std::max(S - K * disc, 0.0)
        : std::max(K * disc - S, 0.0);

    if (marketPrice < intrinsic) {
        return std::numeric_limits<double>::quiet_NaN();
    }

    double lo = 1e-6, hi = 5.0;
    for (int i = 0; i < 100; ++i) {
        double mid = 0.5 * (lo + hi);
        if (bsPrice(S, K, T, r, mid, isCall) < marketPrice) {
            lo = mid;
        } else {
            hi = mid;
        }
    }

    if (hi - lo < 1e-8) {
        return 0.5 * (lo + hi);
    }
    return std::numeric_limits<double>::quiet_NaN();
}

}
