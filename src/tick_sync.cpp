#include "spotvol/tick_sync.hpp"

#include <algorithm>
#include <iterator>

namespace spotvol {

std::vector<double> synchronizeTicks(
    const std::vector<SpotTick>& spotTicks,
    const std::vector<OptionTick>& optionTicks
) {
    // is spotTick after optionTick
    auto isAfter = [](long long timestamp, const SpotTick& spotTick) {
        return timestamp < spotTick.timestamp;
        };

    std::vector<double> output;
    output.reserve(optionTicks.size());

    for (const OptionTick& optionTick : optionTicks) {
        // do binary search on sorted spotTicks stream
        const auto after = std::upper_bound(spotTicks.begin(), spotTicks.end(),
            optionTick.timestamp, isAfter);

        if (after == spotTicks.begin()) {
            output.push_back(kNoSpotPrice);
        }
        else {
            output.push_back(std::prev(after)->price);
        }
    }

    return output;
}

}
