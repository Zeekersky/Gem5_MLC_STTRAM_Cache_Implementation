/*
 * Copyright (c) 2011-2012, 2014 ARM Limited
 * Copyright (c) 2013 Advanced Micro Devices, Inc.
 * All rights reserved.
 *
 * The license below extends only to copyright in the software and shall
 * not be construed as granting a license to any other intellectual
 * property including but not limited to intellectual property relating
 * to a hardware implementation of the functionality of the software
 * licensed hereunder.  You may use the software subject to the license
 * terms below provided that you ensure that this notice is replicated
 * unmodified and in its entirety in all distributions of the software,
 * modified or unmodified, in source code or in binary form.
 *
 * Copyright (c) 2004-2006 The Regents of The University of Michigan
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
 *
 * Authors: Kevin Lim
 */

#ifndef __CPU_O3_INST_QUEUE_HH__
#define __CPU_O3_INST_QUEUE_HH__

#include <list>
#include <map>
#include <queue>
#include <vector>

#include "base/statistics.hh"
#include "base/types.hh"
#include "cpu/o3/dep_graph.hh"
#include "cpu/inst_seq.hh"
#include "cpu/op_class.hh"
#include "cpu/timebuf.hh"
#include "enums/SMTQueuePolicy.hh"
#include "sim/eventq.hh"

struct DerivO3CPUParams;
class FUPool;
class MemInterface;

/**
 * A standard instruction queue class.  It holds ready instructions, in
 * order, in seperate priority queues to facilitate the scheduling of
 * instructions.  The IQ uses a separate linked list to track dependencies.
 * Similar to the rename map and the free list, it expects that
 * floating point registers have their indices start after the integer
 * registers (ie with 96 int and 96 fp registers, regs 0-95 are integer
 * and 96-191 are fp).  This remains true even for both logical and
 * physical register indices. The IQ depends on the memory dependence unit to
 * track when memory operations are ready in terms of ordering; register
 * dependencies are tracked normally. Right now the IQ also handles the
 * execution timing; this is mainly to allow back-to-back scheduling without
 * requiring IEW to be able to peek into the IQ. At the end of the execution
 * latency, the instruction is put into the queue to execute, where it will
 * have the execute() function called on it.
 * @todo: Make IQ able to handle multiple FU pools.
 */
template <class Impl>
class InstructionQueue
{
  public:
    //Typedefs from the Impl.
    typedef typename Impl::O3CPU O3CPU;
    typedef typename Impl::DynInstPtr DynInstPtr;

    typedef typename Impl::CPUPol::IEW IEW;
    typedef typename Impl::CPUPol::MemDepUnit MemDepUnit;
    typedef typename Impl::CPUPol::IssueStruct IssueStruct;
    typedef typename Impl::CPUPol::TimeStruct TimeStruct;

    // Typedef of iterator through the list of instructions.
    typedef typename std::list<DynInstPtr>::iterator ListIt;

    /** FU completion event class. */
    class FUCompletion : public Event {
      private:
        /** Executing instruction. */
        DynInstPtr inst;

        /** Index of the FU used for executing. */
        int fuIdx;

        /** Pointer back to the instruction queue. */
        InstructionQueue<Impl> *iqPtr;

        /** Should the FU be added to the list to be freed upon
         * completing this event.
         */
        bool freeFU;

      public:
        /** Construct a FU completion event. */
        FUCompletion(const DynInstPtr &_inst, int fu_idx,
                     InstructionQueue<Impl> *iq_ptr);

        virtual void process();
        virtual const char *description() const;
        void setFreeFU() { freeFU = true; }
    };

    /** Constructs an IQ. */
    InstructionQueue(O3CPU *cpu_ptr, IEW *iew_ptr, DerivO3CPUParams *params);

    /** Destructs the IQ. */
    ~InstructionQueue();

    /** Returns the name of the IQ. */
    std::string name() const;

    /** Registers statistics. */
    void regStats();

    /** Resets all instruction queue state. */
    void resetState();

    /** Sets active threads list. */
    void setActiveThreads(std::list<ThreadID> *at_ptr);

    /** Sets the timer buffer between issue and execute. */
    void setIssueToExecuteQueue(TimeBuffer<IssueStruct> *i2eQueue);

    /** Sets the global time buffer. */
    void setTimeBuffer(TimeBuffer<TimeStruct> *tb_ptr, ThreadID tid);

    /** Determine if we are drained. */
    bool isDrained() const;

    /** Perform sanity checks after a drain. */
    void drainSanityCheck() const;

    /** Takes over execution from another CPU's thread. */
    void takeOverFrom();

    /** Resets max entries for all threads. */
    void resetEntries();

    /** Returns total number of free entries. */
    unsigned numFreeEntries();

    /** Returns number of free entries for a thread. */
    unsigned numFreeEntries(ThreadID tid);

    /** Returns whether or not the IQ is full. */
    bool isFull();

    /** Returns whether or not the IQ is full for a specific thread. */
    bool isFull(ThreadID tid);

    /** Returns if there are any ready instructions in the IQ. */
    bool hasReadyInsts();

    /** Inserts a new instruction into the IQ. */
    void insert(const DynInstPtr &new_inst);

    /** Inserts a new, non-speculative instruction into the IQ. */
    void insertNonSpec(const DynInstPtr &new_inst);

    /** Inserts a memory or write barrier into the IQ to make sure
     *  loads and stores are ordered properly.
     */
    void insertBarrier(const DynInstPtr &barr_inst);

    /** Returns the oldest scheduled instruction, and removes it from
     * the list of instructions waiting to execute.
     */
    DynInstPtr getInstToExecute();

    /** Gets a memory instruction that was referred due to a delayed DTB
     *  translation if it is now ready to execute.  NULL if none available.
     */
    DynInstPtr getDeferredMemInstToExecute();

    /** Gets a memory instruction that was blocked on the cache. NULL if none
     *  available.
     */
    DynInstPtr getBlockedMemInstToExecute();

    /**
     * Records the instruction as the producer of a register without
     * adding it to the rest of the IQ.
     */
    void recordProducer(const DynInstPtr &inst)
    { addToProducers(inst); }

    /** Process FU completion event. */
    void processFUCompletion(const DynInstPtr &inst, int fu_idx);

    /**
     * Schedules ready instructions, adding the ready ones (oldest first) to
     * the queue to execute.
     */
    void scheduleReadyInsts();

    /** Schedules a single specific non-speculative instruction. */
    void scheduleNonSpec(const InstSeqNum &inst);

    /**
     * Commits all instructions up to and including the given sequence number,
     * for a specific thread.
     */
    void commit(const InstSeqNum &inst, ThreadID tid = 0);

    /** Wakes all dependents of a completed instruction. */
    int wakeDependents(const DynInstPtr &completed_inst);

    /** Adds a ready memory instruction to the ready list. */
    void addReadyMemInst(const DynInstPtr &ready_inst);

    /**
     * Reschedules a memory instruction. It will be ready to issue once
     * replayMemInst() is called.
     */
    void rescheduleMemInst(const DynInstPtr &resched_inst);

    /** Replays a memory instruction. It must be rescheduled first. */
    void replayMemInst(const DynInstPtr &replay_inst);

    /** Completes a memory operation. */
    void completeMemInst(const DynInstPtr &completed_inst);

    /**
     * Defers a memory instruction when its DTB translation incurs a hw
     * page table walk.
     */
    void deferMemInst(const DynInstPtr &deferred_inst);

    /**  Defers a memory instruction when it is cache blocked. */
    void blockMemInst(const DynInstPtr &blocked_inst);

    /**  Notify instruction queue that a previous blockage has resolved */
    void cacheUnblocked();

    /** Indicates an ordering violation between a store and a load. */
    void violation(const DynInstPtr &store, const DynInstPtr &faulting_load);

    /**
     * Squashes instructions for a thread. Squashing information is obtained
     * from the time buffer.
     */
    void squash(ThreadID tid);

    /** Returns the number of used entries for a thread. */
    unsigned getCount(ThreadID tid) { return count[tid]; };

    /** Debug function to print all instructions. */
    void printInsts();

  private:
    /** Does the actual squashing. */
    void doSquash(ThreadID tid);

    /////////////////////////
    // Various pointers
    /////////////////////////

    /** Pointer to the CPU. */
    O3CPU *cpu;

    /** Cache interface. */
    MemInterface *dcacheInterface;

    /** Pointer to IEW stage. */
    IEW *iewStage;

    /** The memory dependence unit, which tracks/predicts memory dependences
     *  between instructions.
     */
    MemDepUnit memDepUnit[Impl::MaxThreads];

    /** The queue to the execute stage.  Issued instructions will be written
     *  into it.
     */
    TimeBuffer<IssueStruct> *issueToExecuteQueue;

    /** The backwards time buffer. */
    std::vector<TimeBuffer<TimeStruct>*> timeBuffer;

    /** Wire to read information from timebuffer. */
    std::vector<typename TimeBuffer<TimeStruct>::wire> fromCommit;

    /** Function unit pool. */
    FUPool *fuPool;

    //////////////////////////////////////
    // Instruction lists, ready queues, and ordering
    //////////////////////////////////////

    /** List of instructions that are waiting to issue (some may not be ready
     *  to issue yet). Instructions are pushed here when they are dispatched.
     *  Instructions are popped from here when they are issued.
     */
    std::list<DynInstPtr> instsToIssue[Impl::MaxThreads];

    /**
     * Struct for comparing entries to be added to the priority queue.
     * This gives reverse ordering to the instructions in terms of
     * sequence numbers: the instructions with smaller sequence
     * numbers (and hence are older) will be at the top of the
     * priority queue.
     */
    struct pqCompare {
        bool operator() (const DynInstPtr &lhs, const DynInstPtr &rhs) const
        {
            return lhs->seqNum > rhs->seqNum;
        }
    };

    /** List of instructions that are ready to issue (i.e., register and memory
     *  dependencies are all cleared) and waiting to be scheduled to issue.
     *  Instructions are pushed here when they are ready to issue, when they
     *  are rescheduled (e.g., blocked by cache, deferred by address
     *  translation, or stalled by a previous ST/AMO instruction). Instructions
     *  are popped from here when they are issued.
     *
     *  Note that instsReadyToIssue and instsToIssue may overlap. For example,
     *  ready-to-issue instructions stay in both lists until they are issued.
     *
     *  Also note that instsReadyToIssue may contain instructions that are not
     *  in instsToIssue. Examples of such instructions are rescheduled,
     *  replayed, and deferred memory instructions.
     */
    typedef std::priority_queue<DynInstPtr, std::vector<DynInstPtr>, pqCompare>
    ReadyInstQueue;

    ReadyInstQueue instsReadyToIssue;

    /** List of instructions that are ready to be executed. Instructions in
     *  this list have already gone through their execution pipeline (i.e.,
     *  execution timing has been already accounted for) and are waiting to
     *  execute functionally. Instructions are pushed here in
     *  processFUCompletion (i.e., instructions are going out of an FU pipe).
     *  Instructions are popped from here when they are selected to execute
     *  in execute stage.
     */
    std::list<DynInstPtr> instsToExecute;

    /** List of instructions waiting for their DTB translation to
     *  complete (hw page table walk in progress). Instructions here will
     *  eventually be pushed back to instsReadyToIssue list to re-execute.
     */
    std::list<DynInstPtr> deferredMemInsts;

    /** List of instructions that have been blocked by cache. Instructions here
     *  will be eventually be waken up by a cache's retry request
     */
    std::list<DynInstPtr> blockedMemInsts;

    /** List of instructions that were cache blocked, but a retry has been seen
     * since, so they can now be retried. May fail again go on the blocked
     * list.
     */
    std::list<DynInstPtr> retryMemInsts;

    /** List of non-speculative instructions that will be scheduled
     *  once the IQ gets a signal from commit.  While it's redundant to
     *  have the key be a part of the value (the sequence number is stored
     *  inside of DynInst), when these instructions are woken up only
     *  the sequence number will be available.  Thus it is most efficient to be
     *  able to search by the sequence number alone.
     *
     *  Note that instructions in this map are also in instsToIssue list
     */
    std::map<InstSeqNum, DynInstPtr> nonSpecInsts;

    typedef typename std::map<InstSeqNum, DynInstPtr>::iterator NonSpecMapIt;

    /** Register-dependency instruction graph */
    DependencyGraph<DynInstPtr> dependGraph;

    //////////////////////////////////////
    // Various parameters
    //////////////////////////////////////

    /** IQ sharing policy for SMT. */
    SMTQueuePolicy iqPolicy;

    /** Number of Total Threads*/
    ThreadID numThreads;

    /** Pointer to list of active threads. */
    std::list<ThreadID> *activeThreads;

    /** Per Thread IQ count */
    unsigned count[Impl::MaxThreads];

    /** Max IQ Entries Per Thread */
    unsigned maxEntries[Impl::MaxThreads];

    /** Number of free IQ entries left. */
    unsigned freeEntries;

    /** The number of entries in the instruction queue. */
    unsigned numEntries;

    /** The total number of instructions that can be issued in one cycle. */
    unsigned totalWidth;

    /** The number of physical registers in the CPU. */
    unsigned numPhysRegs;

    /** Number of instructions currently in flight to FUs */
    int wbOutstanding;

    /** Delay between commit stage and the IQ.
     *  @todo: Make there be a distinction between the delays within IEW.
     */
    Cycles commitToIEWDelay;

    /** Issue instructions in order?
     */
    bool isInOrderIssue;

    /** The sequence number of the squashed instruction. */
    InstSeqNum squashedSeqNum[Impl::MaxThreads];

    /** A cache of the recently woken registers.  It is 1 if the register
     *  has been woken up recently, and 0 if the register has been added
     *  to the dependency graph and has not yet received its value.  It
     *  is basically a secondary scoreboard, and should pretty much mirror
     *  the scoreboard that exists in the rename map.
     */
    std::vector<bool> regScoreboard;

    /** Adds an instruction to the dependency graph, as a consumer. */
    bool addToDependents(const DynInstPtr &new_inst);

    /** Adds an instruction to the dependency graph, as a producer. */
    void addToProducers(const DynInstPtr &new_inst);

    /** Moves an instruction to the ready queue if it is ready. */
    void addIfReady(const DynInstPtr &inst);

    /** Debugging function to count how many entries are in the IQ.  It does
     *  a linear walk through the instructions, so do not call this function
     *  during normal execution.
     */
    int countInsts();

    /** Debugging function to dump all the list sizes, as well as print
     *  out the list of nonspeculative instructions.  Should not be used
     *  in any other capacity, but it has no harmful sideaffects.
     */
    void dumpLists();

    /** Debugging function to dump out all instructions that are in the
     *  IQ.
     */
    void dumpInsts();

    /** Stat for number of instructions added. */
    Stats::Scalar iqInstsAdded;
    /** Stat for number of non-speculative instructions added. */
    Stats::Scalar iqNonSpecInstsAdded;

    Stats::Scalar iqInstsIssued;
    /** Stat for number of integer instructions issued. */
    Stats::Scalar iqIntInstsIssued;
    /** Stat for number of floating point instructions issued. */
    Stats::Scalar iqFloatInstsIssued;
    /** Stat for number of branch instructions issued. */
    Stats::Scalar iqBranchInstsIssued;
    /** Stat for number of memory instructions issued. */
    Stats::Scalar iqMemInstsIssued;
    /** Stat for number of miscellaneous instructions issued. */
    Stats::Scalar iqMiscInstsIssued;
    /** Stat for number of squashed instructions that were ready to issue. */
    Stats::Scalar iqSquashedInstsIssued;
    /** Stat for number of squashed instructions examined when squashing. */
    Stats::Scalar iqSquashedInstsExamined;
    /** Stat for number of squashed instruction operands examined when
     * squashing.
     */
    Stats::Scalar iqSquashedOperandsExamined;
    /** Stat for number of non-speculative instructions removed due to a squash.
     */
    Stats::Scalar iqSquashedNonSpecRemoved;
    // Also include number of instructions rescheduled and replayed.

    /** Distribution of number of instructions in the queue.
     * @todo: Need to create struct to track the entry time for each
     * instruction. */
//    Stats::VectorDistribution queueResDist;
    /** Distribution of the number of instructions issued. */
    Stats::Distribution numIssuedDist;
    /** Distribution of the cycles it takes to issue an instruction.
     * @todo: Need to create struct to track the ready time for each
     * instruction. */
//    Stats::VectorDistribution issueDelayDist;

    /** Number of times an instruction could not be issued because a
     * FU was busy.
     */
    Stats::Vector statFuBusy;
//    Stats::Vector dist_unissued;
    /** Stat for total number issued for each instruction type. */
    Stats::Vector2d statIssuedInstType;

    /** Number of instructions issued per cycle. */
    Stats::Formula issueRate;

    /** Number of times the FU was busy. */
    Stats::Vector fuBusy;
    /** Number of times the FU was busy per instruction issued. */
    Stats::Formula fuBusyRate;
   public:
    Stats::Scalar intInstQueueReads;
    Stats::Scalar intInstQueueWrites;
    Stats::Scalar intInstQueueWakeupAccesses;
    Stats::Scalar fpInstQueueReads;
    Stats::Scalar fpInstQueueWrites;
    Stats::Scalar fpInstQueueWakeupAccesses;
    Stats::Scalar vecInstQueueReads;
    Stats::Scalar vecInstQueueWrites;
    Stats::Scalar vecInstQueueWakeupAccesses;

    Stats::Scalar intAluAccesses;
    Stats::Scalar fpAluAccesses;
    Stats::Scalar vecAluAccesses;
};

#endif //__CPU_O3_INST_QUEUE_HH__
