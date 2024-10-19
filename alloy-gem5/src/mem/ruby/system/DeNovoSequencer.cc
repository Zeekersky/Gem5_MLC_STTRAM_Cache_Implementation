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

#include "mem/ruby/system/DeNovoSequencer.hh"

#include "arch/x86/ldstflags.hh"
#include "base/logging.hh"
#include "base/str.hh"
#include "cpu/testers/rubytest/RubyTester.hh"
#include "debug/MemoryAccess.hh"
#include "debug/ProtocolTrace.hh"
#include "debug/RubyPort.hh"
#include "debug/RubySequencer.hh"
#include "debug/RubyStats.hh"
#include "mem/packet.hh"
#include "mem/protocol/PrefetchBit.hh"
#include "mem/protocol/RubyAccessMode.hh"
#include "mem/ruby/profiler/Profiler.hh"
#include "mem/ruby/slicc_interface/RubyRequest.hh"
#include "mem/ruby/system/RubySystem.hh"
#include "sim/system.hh"

using namespace std;

DeNovoSequencer *
DeNovoSequencerParams::create()
{
    return new DeNovoSequencer(this);
}

DeNovoSequencer::DeNovoSequencer(const Params *p)
  : Sequencer(p), m_outstanding_invalidate(0)
{
}

DeNovoSequencer::~DeNovoSequencer()
{
}

void
DeNovoSequencer::invalidateDataCache()
{
    int size = m_dataCache_ptr->getNumBlocks();
    int inv_count = 0;
    for (int i = 0; i < size; i++) {
        Addr addr = m_dataCache_ptr->getAddressAtIdx(i);
        if (addr == 0) {
            continue; // skip invalid entries
        }
        std::shared_ptr<RubyRequest> msg = std::make_shared<RubyRequest>(
            clockEdge(), addr, (uint8_t*)0, 0, 0,
            RubyRequestType_INVALIDATE, RubyAccessMode_Supervisor,
            nullptr);
        assert(m_mandatory_q_ptr != NULL);
        m_mandatory_q_ptr->enqueue(msg, clockEdge(), m_data_cache_hit_latency);
        m_outstanding_invalidate++;
        inv_count++;
    }
    if (m_outstanding_invalidate == 0) {
        // no cache lines to flush, finish without callback
        finishInvWbDataCache();
    }
    DPRINTF(RubySequencer, "Invalidate %d cache lines\n", inv_count);
}

void
DeNovoSequencer::invalidateCallback(Addr address)
{
    assert(m_outstanding_invalidate > 0);
    // Finished one flush request
    m_outstanding_invalidate--;
    assert(address == makeLineAddress(address));

    DPRINTF(RubyPort, "Invalidate response callback for 0x%x\n",
            address);
    DPRINTF(RubySequencer, "Invalidate address 0x%x done, "
            "%lu outstanding invalidates left\n",
            address, m_outstanding_invalidate);

    if (m_outstanding_invalidate == 0) {
        // reply to the requestor
        finishInvWbDataCache();
    }
}

void
DeNovoSequencer::replyInvWbReq()
{
    assert(m_invwb_packets.size() == 1);
    PacketPtr pkt = m_invwb_packets.front();
    m_invwb_packets.pop();
    // find out which port should reply to
    RubyPort::SenderState *senderState =
        safe_cast<RubyPort::SenderState *>(pkt->popSenderState());
    MemSlavePort *port = senderState->port;
    assert(port != NULL);
    delete senderState;
    pkt->makeResponse();

    // send the packet to the requestor
    port->responseCallback(pkt);
    trySendRetries();
    testDrainComplete();
}

void
DeNovoSequencer::finishInvWbDataCache()
{
    assert(m_invwb_packets.size() == 1);
    PacketPtr pkt = m_invwb_packets.front();
    assert(pkt->isMemFence());

    if (pkt->req->isRelease()) {
        // release-only fence
        replyInvWbReq();
    } else if (pkt->req->isAcquire()) {
        // acquire-only fence
        if (m_outstanding_invalidate == 0) {
            replyInvWbReq();
        }
    } else {
        panic("Unexpected inv/wb request type\n");
    }
}

RequestStatus
DeNovoSequencer::makeRequest(PacketPtr pkt)
{
    if (m_outstanding_count >= m_max_outstanding_requests) {
        return RequestStatus_BufferFull;
    }

    RubyRequestType primary_type = RubyRequestType_NULL;
    RubyRequestType secondary_type = RubyRequestType_NULL;

    if (pkt->isMemFence()) {
        // Should only have one fence at a time
        assert(m_invwb_packets.size() == 0);
        m_invwb_packets.push(pkt);

        if (pkt->req->isAcquire()) {
            // acquire fence
            invalidateDataCache();
        } else if (pkt->req->isRelease()) {
            // release fense is no-op for DeNovo
            replyInvWbReq();
        } else {
            panic("Unsupported memory fence.\n");
        }
        return RequestStatus_Issued;
    }

    if (pkt->isLLSC()) {
        //
        // Alpha LL/SC instructions need to be handled carefully by the cache
        // coherence protocol to ensure they follow the proper semantics. In
        // particular, by identifying the operations as atomic, the protocol
        // should understand that migratory sharing optimizations should not
        // be performed (i.e. a load between the LL and SC should not steal
        // away exclusive permission).
        //
        if (pkt->isWrite()) {
            DPRINTF(RubySequencer, "Issuing SC\n");
            primary_type = RubyRequestType_Store_Conditional;
        } else {
            DPRINTF(RubySequencer, "Issuing LL\n");
            assert(pkt->isRead());
            primary_type = RubyRequestType_Load_Linked;
        }
        secondary_type = RubyRequestType_ATOMIC;
    } else if (pkt->req->isLockedRMW()) {
        //
        // x86 locked instructions are translated to store cache coherence
        // requests because these requests should always be treated as read
        // exclusive operations and should leverage any migratory sharing
        // optimization built into the protocol.
        //
        if (pkt->isWrite()) {
            DPRINTF(RubySequencer, "Issuing Locked RMW Write\n");
            primary_type = RubyRequestType_Locked_RMW_Write;
        } else {
            DPRINTF(RubySequencer, "Issuing Locked RMW Read\n");
            assert(pkt->isRead());
            primary_type = RubyRequestType_Locked_RMW_Read;
        }
        secondary_type = RubyRequestType_ST;
    } else {
        //
        // To support SwapReq, we need to check isWrite() first: a SwapReq
        // should always be treated like a write, but since a SwapReq implies
        // both isWrite() and isRead() are true, check isWrite() first here.
        //
        // moyang: amo are treated as ATOMIC_RETURN, it is handled by L1
        // SLICC controller
        if (pkt->isWrite() && !pkt->isAtomicOp()) {
            //
            // Note: M5 packets do not differentiate ST from RMW_Write
            //
            primary_type = secondary_type = RubyRequestType_ST;
        } else if (pkt->isRead() && !pkt->isAtomicOp()) {
            if (pkt->req->isInstFetch()) {
                primary_type = secondary_type = RubyRequestType_IFETCH;
            } else {
                bool storeCheck = false;
                // only X86 need the store check
                if (system->getArch() == Arch::X86ISA) {
                    uint32_t flags = pkt->req->getFlags();
                    storeCheck = flags &
                        (X86ISA::StoreCheck << X86ISA::FlagShift);
                }
                if (storeCheck) {
                    primary_type = RubyRequestType_RMW_Read;
                    secondary_type = RubyRequestType_ST;
                } else {
                    primary_type = secondary_type = RubyRequestType_LD;
                }
            }
        } else if (pkt->cmd == MemCmd::SwapReq && pkt->isAtomicOp()) {
            primary_type = secondary_type = RubyRequestType_ATOMIC_RETURN;
        } else if (pkt->isFlush()) {
          primary_type = secondary_type = RubyRequestType_FLUSH;
        } else {
            panic("Unsupported ruby packet type\n");
        }
    }

    RequestStatus status = insertRequest(pkt, primary_type);
    if (status != RequestStatus_Ready)
        return status;

    issueRequest(pkt, secondary_type, primary_type);

    // TODO: issue hardware prefetches here
    return RequestStatus_Issued;
}

