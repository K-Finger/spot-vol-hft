#include "spotvol/tick_sync.hpp"

#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include <vector>

using spotvol::OptionTick;
using spotvol::SpotTick;
using spotvol::synchronizeTicks;

using ::testing::DoubleNear;
using ::testing::IsEmpty;
using ::testing::Pointwise;
using ::testing::SizeIs;

namespace {

constexpr double kTol = 1e-9;
constexpr double kNone = -1.0;

}  

TEST(TickSync, ExampleFromSpec) {
    std::vector<SpotTick> spot{{100, 500.00}, {105, 500.20}, {110, 499.90}};
    std::vector<OptionTick> options{{103, 4.20}, {108, 4.30}, {115, 4.10}};

    EXPECT_THAT(synchronizeTicks(spot, options),
                Pointwise(DoubleNear(kTol), std::vector<double>{500.00, 500.20, 499.90}));
}

TEST(TickSync, OptionBeforeAnySpotTickYieldsSentinel) {
    std::vector<SpotTick> spot{{100, 500.00}};
    std::vector<OptionTick> options{{50, 4.20}, {99, 4.25}, {100, 4.30}};

    EXPECT_THAT(synchronizeTicks(spot, options),
                Pointwise(DoubleNear(kTol), std::vector<double>{kNone, kNone, 500.00}));
}

TEST(TickSync, ExactTimestampMatchIsInclusive) {
    std::vector<SpotTick> spot{{100, 500.00}, {200, 501.00}};
    std::vector<OptionTick> options{{100, 4.20}, {200, 4.30}};

    EXPECT_THAT(synchronizeTicks(spot, options),
                Pointwise(DoubleNear(kTol), std::vector<double>{500.00, 501.00}));
}

TEST(TickSync, EmptySpotStreamYieldsAllSentinels) {
    std::vector<OptionTick> options{{100, 4.20}, {200, 4.30}};

    EXPECT_THAT(synchronizeTicks({}, options),
                Pointwise(DoubleNear(kTol), std::vector<double>{kNone, kNone}));
}

TEST(TickSync, EmptyOptionStreamYieldsEmptyOutput) {
    std::vector<SpotTick> spot{{100, 500.00}};

    EXPECT_THAT(synchronizeTicks(spot, {}), IsEmpty());
}

TEST(TickSync, BothStreamsEmpty) {
    EXPECT_THAT(synchronizeTicks({}, {}), IsEmpty());
}

TEST(TickSync, DuplicateSpotTimestampsUseMostRecent) {
    std::vector<SpotTick> spot{{100, 500.00}, {100, 501.00}, {100, 502.00}};
    std::vector<OptionTick> options{{100, 4.20}, {150, 4.30}};

    EXPECT_THAT(synchronizeTicks(spot, options),
                Pointwise(DoubleNear(kTol), std::vector<double>{502.00, 502.00}));
}

TEST(TickSync, ManyOptionsBetweenTwoSpotTicks) {
    std::vector<SpotTick> spot{{100, 500.00}, {200, 501.00}};
    std::vector<OptionTick> options{{110, 4.1}, {120, 4.2}, {130, 4.3}, {199, 4.4}};

    EXPECT_THAT(
        synchronizeTicks(spot, options),
        Pointwise(DoubleNear(kTol), std::vector<double>{500.00, 500.00, 500.00, 500.00}));
}

TEST(TickSync, AllOptionsAfterLastSpotTick) {
    std::vector<SpotTick> spot{{100, 500.00}, {110, 499.50}};
    std::vector<OptionTick> options{{500, 4.20}, {900, 4.30}};

    EXPECT_THAT(synchronizeTicks(spot, options),
                Pointwise(DoubleNear(kTol), std::vector<double>{499.50, 499.50}));
}

TEST(TickSync, ManySpotTicksSkippedBetweenOptions) {
    std::vector<SpotTick> spot{
        {1, 10.0}, {2, 11.0}, {3, 12.0}, {4, 13.0}, {5, 14.0}, {6, 15.0}};
    std::vector<OptionTick> options{{3, 0.1}, {6, 0.2}};

    EXPECT_THAT(synchronizeTicks(spot, options),
                Pointwise(DoubleNear(kTol), std::vector<double>{12.0, 15.0}));
}

TEST(TickSync, DuplicateOptionTimestamps) {
    std::vector<SpotTick> spot{{100, 500.00}, {200, 501.00}};
    std::vector<OptionTick> options{{150, 4.20}, {150, 4.25}, {150, 4.30}};

    EXPECT_THAT(synchronizeTicks(spot, options),
                Pointwise(DoubleNear(kTol), std::vector<double>{500.00, 500.00, 500.00}));
}

TEST(TickSync, SingleSpotSingleOption) {
    std::vector<SpotTick> spot{{100, 500.00}};
    std::vector<OptionTick> options{{100, 4.20}};

    EXPECT_THAT(synchronizeTicks(spot, options),
                Pointwise(DoubleNear(kTol), std::vector<double>{500.00}));
}

TEST(TickSync, EpochScaleTimestampsDoNotOverflow) {
    std::vector<SpotTick> spot{{1'700'000'000'000LL, 500.00},
                               {1'700'000'000'500LL, 500.25}};
    std::vector<OptionTick> options{{1'700'000'000'499LL, 4.20},
                                    {1'700'000'000'500LL, 4.30}};

    EXPECT_THAT(synchronizeTicks(spot, options),
                Pointwise(DoubleNear(kTol), std::vector<double>{500.00, 500.25}));
}

TEST(TickSync, OutputSizeAlwaysMatchesOptionCount) {
    std::vector<SpotTick> spot{{5, 1.0}};
    std::vector<OptionTick> options{{1, 0.0}, {2, 0.0}, {3, 0.0}, {9, 0.0}};

    EXPECT_THAT(synchronizeTicks(spot, options), SizeIs(options.size()));
}
