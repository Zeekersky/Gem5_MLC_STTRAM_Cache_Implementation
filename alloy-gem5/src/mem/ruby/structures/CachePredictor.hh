/*
 * Author: Akash Pal (AP)
 */

#ifndef __MEM_RUBY_STRUCTURES_CACHEPREDICTOR_HH__
#define __MEM_RUBY_STRUCTURES_CACHEPREDICTOR_HH__

#include <iostream>
#include <vector>
#include <utility>
#include "base/types.hh"
#include "mem/ruby/common/Address.hh"

using namespace std;

// Composite Key Structure
struct PredictorKey
{
    Addr pcAddress;
    Addr cacheBlockAddress;

    PredictorKey(Addr pc, Addr cacheBlock)
        : pcAddress(pc), cacheBlockAddress(cacheBlock) {}

    bool operator==(const PredictorKey &other) const
    {
        return pcAddress == other.pcAddress && cacheBlockAddress == other.cacheBlockAddress;
    }
};

// Hash Function for the Composite Key
// struct PredictorKeyHash
// {
//     std::size_t operator()(const PredictorKey &key) const
//     {
//         // Apply mid-square hashing and limited the space to 1024 entries
//         // Concate the two addresses and square the result
//         std::size_t keyVal = std::hash<Addr>()((key.pcAddress << 6) | (key.cacheBlockAddress & 0x3F));
//         std::size_t hashVal = keyVal * keyVal;
//         // take mid 10 bits
//         return (hashVal >> 22) & 0x3FF;
//     }
// };

class CachePredictor
{
private:
    // A Table to store the predictor entries
    vector<pair<PredictorKey, int>> predictorTable;

public:
    CachePredictor()
    {
        predictorTable = vector<pair<PredictorKey, int>>(512, pair<PredictorKey, int>(PredictorKey(0, 0), 0));
    };

    // get the index of predictorTable
    int getTableIndex(Addr pcAddress, Addr cacheBlockAddress);

    // Adds a new entry to the predictor table
    void addEntry(Addr pcAddress, Addr cacheBlockAddress, int sequence);
};

#endif // __MEM_RUBY_STRUCTURES_CACHEPREDICTOR_HH__