/*
 * Sequencer for two-level SC3 protocol with write-through L1s
 */

#include "mem/ruby/system/SC3L2SequencerWT.hh"

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

SC3L2SequencerWT *
SC3L2SequencerWTParams::create()
{
    return new SC3L2SequencerWT(this);
}

SC3L2SequencerWT::SC3L2SequencerWT(const Params *p)
    : Sequencer(p)
{
    m_outstanding_invalidate = 0;
    m_outstanding_writeback = 0;
}

SC3L2SequencerWT::~SC3L2SequencerWT()
{
}

void
SC3L2SequencerWT::invalidateDataCache()
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
SC3L2SequencerWT::invWbDataCache()
{
    int size = m_dataCache_ptr->getNumBlocks();

    // invalidate
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
    }

    // write-back (flush)
    // since the L1 is write-through, we simply wait for all writeback ACKs to
    // come back

    if (m_outstanding_writeback + m_outstanding_invalidate == 0) {
        // no cache lines to inv/flush
        finishInvWbDataCache();
    }

    DPRINTF(RubySequencer, "Inv/Writeback %d/%d cache lines\n",
            m_outstanding_invalidate, m_outstanding_writeback);
}

void
SC3L2SequencerWT::invalidateCallback(Addr address)
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
SC3L2SequencerWT::writebackDataCache()
{
    // write-back (flush)
    // since the L1 is write-through, we simply wait for all writeback ACKs to
    // come back

    if (m_outstanding_writeback == 0) {
        // no cache lines to flush, finish without callback
        finishInvWbDataCache();
    }

    DPRINTF(RubySequencer, "Writeback %d cache lines\n",
            m_outstanding_writeback);
}

void
SC3L2SequencerWT::writebackCallback(Addr address)
{
    assert(m_outstanding_writeback > 0);
    // Finished one flush request
    m_outstanding_writeback--;
    assert(address == makeLineAddress(address));

    DPRINTF(RubyPort, "Writeback response callback for 0x%x\n",
            address);
    DPRINTF(RubySequencer, "Writeback address 0x%x done, "
            "%lu outstanding writebacks left\n",
            address, m_outstanding_writeback);

    if (m_invwb_packets.size() > 0 && m_outstanding_writeback == 0) {
        // reply to the requestor
        finishInvWbDataCache();
    }
}

void
SC3L2SequencerWT::replyInvWbReq()
{
    DPRINTF(RubySequencer, "replyInvWbReq\n");
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
SC3L2SequencerWT::finishInvWbDataCache()
{
    assert(m_invwb_packets.size() == 1);
    PacketPtr pkt = m_invwb_packets.front();
    assert(pkt->isMemFence());

    DPRINTF(RubySequencer, "finishInvWbDataCache  wb  %d inv %d\n",
            m_outstanding_writeback, m_outstanding_invalidate);

    if (pkt->req->isAcquire() && pkt->req->isRelease()) {
        // acquire&release fence
        if (m_outstanding_writeback +
            m_outstanding_invalidate == 0) {
            replyInvWbReq();
        }
    } else if (pkt->req->isRelease()) {
        // release-only fence
        if (m_outstanding_writeback == 0) {
            replyInvWbReq();
        }
    } else if (pkt->req->isAcquire()) {
        // acquire-only fence
        if (m_outstanding_invalidate == 0) {
            replyInvWbReq();
        }
    } else {
        panic("Unexpected inv/wb request type\n");
    }
}

void
SC3L2SequencerWT::writeCallback(Addr address, DataBlock& data,
                              const bool externalHit,
                              const MachineType mach,
                              const Cycles initialRequestTime,
                              const Cycles forwardRequestTime,
                              const Cycles firstResponseTime)
{
    assert(address == makeLineAddress(address));
    assert(m_writeRequestTable.count(makeLineAddress(address)));

    RequestTable::iterator i = m_writeRequestTable.find(address);
    assert(i != m_writeRequestTable.end());
    SequencerRequest* request = i->second;

    m_writeRequestTable.erase(i);
    markRemoved();

    // assert((request->m_type == RubyRequestType_ST) ||
    //        (request->m_type == RubyRequestType_ATOMIC) ||
    //        (request->m_type == RubyRequestType_ATOMIC_RETURN) ||
    //        (request->m_type == RubyRequestType_ATOMIC_NO_RETURN) ||
    //        (request->m_type == RubyRequestType_RMW_Read) ||
    //        (request->m_type == RubyRequestType_RMW_Write) ||
    //        (request->m_type == RubyRequestType_Load_Linked) ||
    //        (request->m_type == RubyRequestType_Store_Conditional) ||
    //        (request->m_type == RubyRequestType_Locked_RMW_Read) ||
    //        (request->m_type == RubyRequestType_Locked_RMW_Write) ||
    //        (request->m_type == RubyRequestType_FLUSH));

    assert((request->m_type == RubyRequestType_ST));

    bool success = true;

    hitCallback(request, data, success, mach, externalHit,
                initialRequestTime, forwardRequestTime, firstResponseTime);
}

void
SC3L2SequencerWT::atomicCallback(Addr address, DataBlock& data,
                                       bool sc_success,
                                       const MachineType mach,
                                       const Cycles initialRequestTime,
                                       const Cycles forwardRequestTime,
                                       const Cycles firstResponseTime)
{
    assert(address == makeLineAddress(address));
    assert(m_writeRequestTable.count(makeLineAddress(address)));

    RequestTable::iterator i = m_writeRequestTable.find(address);
    assert(i != m_writeRequestTable.end());
    SequencerRequest* request = i->second;

    m_writeRequestTable.erase(i);
    markRemoved();

    assert((request->m_type == RubyRequestType_ATOMIC) ||
           (request->m_type == RubyRequestType_ATOMIC_RETURN) ||
           (request->m_type == RubyRequestType_Load_Linked) ||
           (request->m_type == RubyRequestType_Store_Conditional));

    if (!sc_success) {
        assert(request->m_type == RubyRequestType_Store_Conditional);
    }

    if (request->m_type == RubyRequestType_Store_Conditional) {
        // Set flag indicating sc success/failure
        if (sc_success) {
            request->pkt->req->setExtraData(1);
        } else {
            request->pkt->req->setExtraData(0);
        }
    }

    bool externalHit = true;

    hitCallback(request, data, sc_success, mach, externalHit,
                initialRequestTime, forwardRequestTime, firstResponseTime);
}

void
SC3L2SequencerWT::hitCallback(SequencerRequest* srequest,
                            DataBlock& data,
                            bool llscSuccess,
                            const MachineType mach,
                            const bool externalHit,
                            const Cycles initialRequestTime,
                            const Cycles forwardRequestTime,
                            const Cycles firstResponseTime)
{
    warn_once("Replacement policy updates recently became the responsibility "
              "of SLICC state machines. Make sure to setMRU() near callbacks "
              "in .sm files!");

    PacketPtr pkt = srequest->pkt;
    Addr request_address(pkt->getAddr());
    RubyRequestType type = srequest->m_type;
    Cycles issued_time = srequest->issue_time;

    assert(curCycle() >= issued_time);
    Cycles total_latency = curCycle() - issued_time;

    // Profile the latency for all demand accesses.
    recordMissLatency(total_latency, type, mach, externalHit, issued_time,
                      initialRequestTime, forwardRequestTime,
                      firstResponseTime, curCycle());

    DPRINTFR(ProtocolTrace, "%15s %3s %10s%20s %6s>%-6s %#x %d cycles\n",
             curTick(), m_version, "Seq",
             llscSuccess ? "Done" : "SC_Failed", "", "",
             printAddress(request_address), total_latency);

    // update the data unless it is a non-data-carrying flush
    if (RubySystem::getWarmupEnabled()) {
        data.setData(pkt->getConstPtr<uint8_t>(),
                     getOffset(request_address), pkt->getSize());
    } else if (!pkt->isFlush()) {
        if ((type == RubyRequestType_LD) ||
            (type == RubyRequestType_IFETCH) ||
            (type == RubyRequestType_Load_Linked)) {
            memcpy(pkt->getPtr<uint8_t>(),
                   data.getData(getOffset(request_address), pkt->getSize()),
                   pkt->getSize());
            DPRINTF(RubySequencer, "read data %s\n", data);
        } else if (pkt->req->isSwap() || pkt->isAtomicOp()) {
            // AMO already handled in L2, simply return old value
            memcpy(pkt->getPtr<uint8_t>(),
                   data.getData(getOffset(request_address), pkt->getSize()),
                   pkt->getSize());

            DPRINTF(RubySequencer, "swap data %s\n", data);
        } else if (type != RubyRequestType_Store_Conditional || llscSuccess) {
            // Types of stores set the actual data here, apart from
            // failed Store Conditional requests
            data.setData(pkt->getConstPtr<uint8_t>(),
                         getOffset(request_address), pkt->getSize());
            DPRINTF(RubySequencer, "set data %s\n", data);
        }
    }

    // If using the RubyTester, update the RubyTester sender state's
    // subBlock with the recieved data.  The tester will later access
    // this state.
    if (m_usingRubyTester) {
        DPRINTF(RubySequencer, "hitCallback %s 0x%x using RubyTester\n",
                pkt->cmdString(), pkt->getAddr());
        RubyTester::SenderState* testerSenderState =
            pkt->findNextSenderState<RubyTester::SenderState>();
        assert(testerSenderState);
        testerSenderState->subBlock.mergeFrom(data);
    }

    delete srequest;

    RubySystem *rs = m_ruby_system;
    if (RubySystem::getWarmupEnabled()) {
        assert(pkt->req);
        delete pkt;
        rs->m_cache_recorder->enqueueNextFetchRequest();
    } else if (RubySystem::getCooldownEnabled()) {
        delete pkt;
        rs->m_cache_recorder->enqueueNextFlushRequest();
    } else {
        ruby_hit_callback(pkt);
        testDrainComplete();
    }
}

RequestStatus
SC3L2SequencerWT::makeRequest(PacketPtr pkt)
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

        if (pkt->req->isAcquire() && pkt->req->isRelease()) {
            // full (acquire and release) fence
            invWbDataCache();
        } else if (pkt->req->isAcquire()) {
            // acquire fence
            invalidateDataCache();
        } else if (pkt->req->isRelease()) {
            // release fence
            writebackDataCache();
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
        if (pkt->isWrite() && !pkt->isAtomicOp()) {
            //
            // Note: M5 packets do not differentiate ST from RMW_Write
            //
            DPRINTF(RubySequencer, "Issuing Store\n");
            primary_type = secondary_type = RubyRequestType_ST;
        } else if (pkt->isRead() && !pkt->isAtomicOp()) {
            if (pkt->req->isInstFetch()) {
                DPRINTF(RubySequencer, "Issuing IFetch\n");
                primary_type = secondary_type = RubyRequestType_IFETCH;
            } else {
                bool storeCheck = false;
                DPRINTF(RubySequencer, "Issuing Load\n");
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
            DPRINTF(RubySequencer, "Issuing Swap\n");
            primary_type = secondary_type = RubyRequestType_ATOMIC_RETURN;
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

void
SC3L2SequencerWT::issueRequest(PacketPtr pkt,
                             RubyRequestType secondary_type,
                             RubyRequestType primary_type)
{
    assert(pkt != NULL);
    assert(!pkt->isFlush());

    Addr line_addr = makeLineAddress(pkt->getAddr());
    uint32_t blockSize = RubySystem::getBlockSizeBytes();
    uint32_t offset = pkt->getAddr() - line_addr;

    assert(pkt->getSize() + offset <= blockSize);

    assert(pkt->req->hasContextId());

    ContextID proc_id = pkt->req->contextId();
    ContextID core_id = coreId();

    // If valid, copy the pc to the ruby request
    Addr pc = 0;
    if (pkt->req->hasPC()) {
        pc = pkt->req->getPC();
    }

    // create accessMask

    std::vector<bool> accessMask(blockSize, false);

    for (int j = 0; j < pkt->getSize(); j++) {
      accessMask[offset+j] = true;
    }

    // create dataBlock and atomicOps for AMO
    // AMOs are handled in L2, but normal reads and writes are handled in
    // callback functions in the sequencer.
    DataBlock dataBlock;
    dataBlock.clear();
    if (pkt->isWrite()) {
        dataBlock.setData(pkt->getPtr<uint8_t>(), offset, pkt->getSize());
    }

    std::vector< std::pair<int,AtomicOpFunctor*> > atomicOps;
    if (pkt->isAtomicOp()) {
        std::pair<int, AtomicOpFunctor*> tmpAtomicOp(offset,
                                                     pkt->getAtomicOp());
        atomicOps.push_back(tmpAtomicOp);
    }

    // check if the packet has data as for example prefetch and flush
    // requests do not

    std::shared_ptr<RubyRequest> msg;

    if (pkt->isAtomicOp()) {
        assert(pkt->cmd == MemCmd::SwapReq);
        msg = std::make_shared<RubyRequest>(clockEdge(), pkt->getAddr(),
                                            pkt->getPtr<uint8_t>(),
                                            pkt->getSize(), pc, secondary_type,
                                            RubyAccessMode_Supervisor, pkt,
                                            PrefetchBit_No, proc_id, core_id,
                                            blockSize, accessMask, dataBlock,
                                            atomicOps);
    } else {
        msg = std::make_shared<RubyRequest>(clockEdge(), pkt->getAddr(),
                                            pkt->getPtr<uint8_t>(),
                                            pkt->getSize(), pc, secondary_type,
                                            RubyAccessMode_Supervisor, pkt,
                                            PrefetchBit_No, proc_id, core_id,
                                            blockSize, accessMask, dataBlock);
    }

    msg->m_PrimaryType = primary_type;

    DPRINTFR(ProtocolTrace, "%15s %3s %10s%20s %6s>%-6s %#x %s\n",
            curTick(), m_version, "Seq", "Begin", "", "",
            printAddress(msg->getPhysicalAddress()),
            RubyRequestType_to_string(secondary_type));

    // The Sequencer currently assesses instruction and data cache hit latency
    // for the top-level caches at the beginning of a memory access.
    // TODO: Eventually, this latency should be moved to represent the actual
    // cache access latency portion of the memory access. This will require
    // changing cache controller protocol files to assess the latency on the
    // access response path.
    Cycles latency(0);  // Initialize to zero to catch misconfigured latency
    if (secondary_type == RubyRequestType_IFETCH)
        latency = m_inst_cache_hit_latency;
    else
        latency = m_data_cache_hit_latency;

    // Send the message to the cache controller
    assert(latency > 0);

    assert(m_mandatory_q_ptr != NULL);
    m_mandatory_q_ptr->enqueue(msg, clockEdge(), cyclesToTicks(latency));

    // For each write, we're gonna receive one writeCallback (i.e., happening
    // when the write is done at L1 cache) and a writebackCallback (i.e.,
    // happening when the write is performed at L2 cache).

    if (pkt->isWrite() && !pkt->isLLSC() && !pkt->isAtomicOp()) {
        m_outstanding_writeback++;
    }
}
