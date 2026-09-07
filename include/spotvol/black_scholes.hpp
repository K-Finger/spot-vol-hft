#pragma once

namespace spotvol {

double bsPrice(double S, double K, double T, double r, double sigma, bool isCall);

/// Returns NaN when no solution exists: T <= 0, price <= 0, or price < intrinsic.
double impliedVol(double marketPrice, double S, double K, double T, double r, bool isCall);

}
