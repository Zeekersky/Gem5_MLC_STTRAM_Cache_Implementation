/*
 * Author: Akash Pal (AP)
 */

#include <vector>
#include "mem/ruby/structures/CachePredictor.hh"
using namespace std;

// get the index of predictorTable
int CachePredictor::getTableIndex(Addr pcAddress, Addr cacheBlockAddress)
{
    cout << "Getting table index..." << endl;

    PredictorKey key(pcAddress, cacheBlockAddress);
    cout << "Key: " << key.pcAddress << ", " << key.cacheBlockAddress << endl;
    // Use mid square hashing to get the index
    std::size_t keyVal = std::hash<Addr>()((key.pcAddress << 6) | (key.cacheBlockAddress & 0x3F));
    std::size_t hashVal = keyVal * keyVal;
    int index = (hashVal >> 22) & 0x1FF;
    std::cout << "Index: " << index % 512 << endl;
    return index % 512;
}

// Adds a new entry to the predictor table
void CachePredictor::addEntry(Addr pcAddress, Addr cacheBlockAddress, int index_sequence)
{
    int index = getTableIndex(pcAddress, cacheBlockAddress);
    cout << "Index: " << index << endl;
    cout << "Size: " << predictorTable.size() << endl;
    cout << "Index Sequence: " << predictorTable[0].second << endl;
    if (index < predictorTable.size())
        predictorTable[index] = pair<PredictorKey, int>(PredictorKey(pcAddress, cacheBlockAddress), index_sequence);
    else
        cout << "Index out of range..." << endl;
    cout << "Index: " << index
         << " PC Address: " << predictorTable[index].first.pcAddress
         << " Cache Block Address: " << predictorTable[index].first.cacheBlockAddress
         << " Sequence: " << predictorTable[index].second
         << endl;
}