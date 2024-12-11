/*
 * Author: Akash Pal (AP)
 */

#ifndef __MEM_RUBY_STRUCTURES_CACHEPREDICTOR_HH__
#define __MEM_RUBY_STRUCTURES_CACHEPREDICTOR_HH__

#include <iostream>
#include <vector>
#include <unordered_map>
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
struct PredictorKeyHash
{
    std::size_t operator()(const PredictorKey &key) const
    {
        return std::hash<Addr>()(key.pcAddress) ^ (std::hash<Addr>()(key.cacheBlockAddress) << 1);
    }
};

class CachePredictor
{
public:
    CachePredictor();
    ~CachePredictor();

    uint64_t makeKey(Addr pcAddress, Addr cacheBlockAddress) const;

    // Adds a new entry to the predictor table
    void addEntry(Addr pcAddress, Addr cacheBlockAddress, int sequence);

    // Checks if an entry exists for a given PC and cache block address
    bool lookupEntry(Addr pcAddress, Addr cacheBlockAddress) const;

    // Prints the content by the key of the predictor table
    // void printByKey(PredictorKey key, ostream &out) const;

    // Prints the contents of the predictor table
    void print(ostream &out) const;

private:
    // A hash map to store predictor entries (key: PC and cache block address)
    unordered_map<PredictorKey, int, PredictorKeyHash> predictorTable;
};

inline ostream &
operator<<(ostream &out, const CachePredictor &obj)
{
    obj.print(out);
    out << flush;
    return out;
}

#endif // __MEM_RUBY_STRUCTURES_CACHEPREDICTOR_HH__
