#include "spotvol/black_scholes.hpp"

#include <gtest/gtest.h>

#include <cmath>

namespace {

constexpr double kS = 100.0;
constexpr double kK = 100.0;
constexpr double kT = 1.0;
constexpr double kR = 0.0;
constexpr double kSigma = 0.2;
constexpr double kTol = 1e-6;

}

TEST(BlackScholes, RoundTripCall) {
    double price = spotvol::bsPrice(kS, kK, kT, kR, kSigma, true);
    EXPECT_NEAR(spotvol::impliedVol(price, kS, kK, kT, kR, true), kSigma, kTol);
}

TEST(BlackScholes, RoundTripPut) {
    double price = spotvol::bsPrice(kS, kK, kT, kR, kSigma, false);
    EXPECT_NEAR(spotvol::impliedVol(price, kS, kK, kT, kR, false), kSigma, kTol);
}

TEST(BlackScholes, PutCallParity) {
    double call = spotvol::bsPrice(kS, kK, kT, kR, kSigma, true);
    double put  = spotvol::bsPrice(kS, kK, kT, kR, kSigma, false);
    double expected = kS - kK * std::exp(-kR * kT);
    EXPECT_NEAR(call - put, expected, 1e-9);
}

TEST(BlackScholes, ExpiredOptionReturnsNaN) {
    EXPECT_TRUE(std::isnan(spotvol::impliedVol(5.0, kS, kK, 0.0, kR, true)));
}

TEST(BlackScholes, NegativePriceReturnsNaN) {
    EXPECT_TRUE(std::isnan(spotvol::impliedVol(-1.0, kS, kK, kT, kR, true)));
}

TEST(BlackScholes, BelowIntrinsicReturnsNaN) {
    EXPECT_TRUE(std::isnan(spotvol::impliedVol(0.01, 110.0, 100.0, kT, kR, true)));
}

TEST(BlackScholes, HighVolRoundTrip) {
    double price = spotvol::bsPrice(kS, kK, kT, kR, 0.8, true);
    EXPECT_NEAR(spotvol::impliedVol(price, kS, kK, kT, kR, true), 0.8, kTol);
}

TEST(BlackScholes, OTMCallRoundTrip) {
    double price = spotvol::bsPrice(100.0, 120.0, kT, kR, kSigma, true);
    EXPECT_NEAR(spotvol::impliedVol(price, 100.0, 120.0, kT, kR, true), kSigma, kTol);
}
