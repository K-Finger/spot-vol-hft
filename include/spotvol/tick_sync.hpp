#pragma once

#include <vector>

namespace spotvol {

struct SpotTick {
    long long timestamp;
    double price;
};

struct OptionTick {
    long long timestamp;
    double price;
};

/// Price reported for an option tick that predates every spot tick.
inline constexpr double kNoSpotPrice = -1.0;

/// @brief Finds the latest spotTick per optionTick in a stream
/// @param spotTicks is a spotTick stream, sorted by non-decreasing timestamp
/// @param optionTicks is an optionTick stream
/// @return per optionTick, the price of the last spotTick at or before its
///         timestamp, or kNoSpotPrice if none exists
std::vector<double> synchronizeTicks(
    const std::vector<SpotTick>& spotTicks,
    const std::vector<OptionTick>& optionTicks
);

}  
