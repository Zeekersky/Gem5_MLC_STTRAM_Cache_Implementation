/*
 * Copyright (c) 1999-2008 Mark D. Hill and David A. Wood
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met: redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer;
 * redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution;
 * neither the name of the copyright holders nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#ifndef __MEM_RUBY_SYSTEM_SC3_L2_SEQUENCER_HH__
#define __MEM_RUBY_SYSTEM_SC3_L2_SEQUENCER_HH__

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
#include "params/SC3L2Sequencer.hh"

class SC3L2Sequencer : public Sequencer
{
  public:
    typedef SC3L2SequencerParams Params;
    SC3L2Sequencer(const Params *);
    ~SC3L2Sequencer();

    void writeCallback(Addr address, DataBlock& data,
                       int& cache_level,
                       const bool externalHit = false,
                       const MachineType mach = MachineType_NUM,
                       const Cycles initialRequestTime = Cycles(0),
                       const Cycles forwardRequestTime = Cycles(0),
                       const Cycles firstResponseTime = Cycles(0));

  void readCallback(Addr address,
                    DataBlock& data,
                    int& cache_level,
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
    void invalidateDataCache(int type, int level);
    void writebackDataCache(int type, int level);
    void invWbDataCache(int type, int level);
    void finishInvWbDataCache();
    void replyInvWbReq();

    // overriden functions
    RequestStatus makeRequest(PacketPtr pkt);
    void issueRequest(PacketPtr pkt, RubyRequestType secondary_type,
                      RubyRequestType primary_type);
    void hitCallback(SequencerRequest* request, DataBlock& data,
                     int& cache_level,
                     bool llscSuccess,
                     const MachineType mach, const bool externalHit,
                     const Cycles initialRequestTime,
                     const Cycles forwardRequestTime,
                     const Cycles firstResponseTime);

  public:
    SC3L2Sequencer(const SC3L2Sequencer& obj) = delete;
    SC3L2Sequencer& operator=(const SC3L2Sequencer& obj) = delete;

  private:
    size_t m_outstanding_invalidate;
    size_t m_outstanding_writeback;
    // a queue to store the invalidate/writeback
    std::queue<PacketPtr> m_invwb_packets;
};

#endif // __MEM_RUBY_SYSTEM_SC3_L2_SEQUENCER_HH__
