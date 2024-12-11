/*
 * Author: Akash Pal (AP)
 */

#include "mem/ruby/structures/CachePredictor.hh"
using namespace std;

CachePredictor::CachePredictor() {}

CachePredictor::~CachePredictor() {}

uint64_t CachePredictor::makeKey(Addr pcAddress, Addr cacheBlockAddress) const
{
    return ((~0x3F) & pcAddress) | (cacheBlockAddress & 0x3F);
}

// Adds a new entry to the predictor table
void CachePredictor::addEntry(Addr pcAddress, Addr cacheBlockAddress, int index_sequence)
{
    PredictorKey key(pcAddress, cacheBlockAddress);
    // // uint64_t key = makeKey(pcAddress, cacheBlockAddress);
    // if (!lookupEntry(pcAddress, cacheBlockAddress) || predictorTable[key] != index_sequence)
    // {
    //     predictorTable.insert({key, index_sequence});
    // }
    cout << "PCAddress: " << key.pcAddress
         << " CacheBlSockAddress: " << key.cacheBlockAddress
         << " Sequence: " << index_sequence << endl;
}

// Checks if an entry exists for a given PC and cache block address
bool CachePredictor::lookupEntry(Addr pcAddress, Addr cacheBlockAddress) const
{
    PredictorKey key(pcAddress, cacheBlockAddress);
    // uint64_t key = makeKey(pcAddress, cacheBlockAddress);
    return predictorTable.find(key) != predictorTable.end();
}

// Prints the content by the key of the predictor table
// void CachePredictor::printByKey(PredictorKey key, ostream &out) const
// {
//     PredictorKey
//     auto it = predictorTable.find(key);
//     if (it != predictorTable.end())
//     {
//         out << "Key: " << key
//             << ", PC Address: " << (((~0x3F) & key) >> 6)
//             << ", Cache Block Address: " << (key & 0x3F)
//             << ", Sequence: " << it->second << endl;
//     }
//     else
//         out << "Key not found..." << endl;
// }

// Prints the contents of the predictor table
void CachePredictor::print(ostream &out) const
{
    for (const auto &entry : predictorTable)
    {
        const auto &key = entry.first;
        // out << "Key: " << entry.first
        //     << ", Sequence: " << entry.second << endl;

        // out << "PC Address: " << (((~0x3F) & key) >> 6)
        //     << ", Cache Block Address: " << (key & 0x3F)
        //     << ", Sequence: " << entry.second << endl;

        out << "PC Address: " << key.pcAddress
            << ", Cache Block Address: " << key.cacheBlockAddress
            << ", Sequence: " << entry.second << endl;
    }
}
