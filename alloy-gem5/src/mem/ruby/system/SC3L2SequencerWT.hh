/*
 * Sequencer used for Two-level SC3 protocol with write-through L1 cache
 */

#ifndef __MEM_RUBY_SYSTEM_SC3_L2_SEQUENCER_WT_HH__
#define __MEM_RUBY_SYSTEM_SC3_L2_SEQUENCER_WT_HH__

#include <iostream>
#include <queue>
#include <unordered_map>

#include "mem/protocol/MachineType.hh"
#include "mem/protocol/RubyRequestType.hh"
#include "mem/protocol/SequencerRequestType.hh"
#include "mem/ruby/common/Address.hh"
#include "mem/ruby/structures/CacheMemory.hh"
#include "mem/ruby/system/RubyPort.hh"
#include "mem/ruby/system/Sequencer.hh"
#include "params/SC3L2SequencerWT.hh"

class SC3L2SequencerWT : public Sequencer
{
  public:
    typedef SC3L2SequencerWTParams Params;
    SC3L2SequencerWT(const Params *);
    ~SC3L2SequencerWT();

    // Override base Sequencer
    void writeCallback(Addr address, DataBlock& data,
                       const bool externalHit = false,
                       const MachineType mach = MachineType_NUM,
                       const Cycles initialRequestTime = Cycles(0),
                       const Cycles forwardRequestTime = Cycles(0),
                       const Cycles firstResponseTime = Cycles(0));

    // Additional functions that are not in base
    // Sequencer.
    void invalidateCallback(Addr address);
    void writebackCallback(Addr address);
    void atomicCallback(Addr address, DataBlock& data,
                        bool sc_success = true,
                        const MachineType mach = MachineType_NUM,
                        const Cycles initialRequestTime = Cycles(0),
                        const Cycles forwardRequestTime = Cycles(0),
                        const Cycles firstResponseTime = Cycles(0));

  protected:
    // invalidate clean lines and write-back (flush) dirty lines
    void invalidateDataCache();
    void writebackDataCache();
    void invWbDataCache();
    void finishInvWbDataCache();
    void replyInvWbReq();

    // overriden functions
    RequestStatus makeRequest(PacketPtr pkt);
    void issueRequest(PacketPtr pkt, RubyRequestType secondary_type,
                      RubyRequestType primary_type);
    void hitCallback(SequencerRequest* request, DataBlock& data,
                     bool llscSuccess,
                     const MachineType mach, const bool externalHit,
                     const Cycles initialRequestTime,
                     const Cycles forwardRequestTime,
                     const Cycles firstResponseTime);

  public:
    SC3L2SequencerWT(const SC3L2SequencerWT& obj) = delete;
    SC3L2SequencerWT& operator=(const SC3L2SequencerWT& obj) = delete;

  private:
    size_t m_outstanding_invalidate;
    size_t m_outstanding_writeback;
    // a queue to store the invalidate/writeback
    std::queue<PacketPtr> m_invwb_packets;
};

#endif // __MEM_RUBY_SYSTEM_SC3_L2_SEQUENCER_WT_HH__
