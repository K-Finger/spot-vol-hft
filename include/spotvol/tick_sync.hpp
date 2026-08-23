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

std::vector<double> synchronizeTicks(
    const std::vector<SpotTick>& spotTicks,
    const std::vector<OptionTick>& optionTicks
);

}  
