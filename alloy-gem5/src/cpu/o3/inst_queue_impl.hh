/*
 * Copyright (c) 2011-2014, 2017-2018 ARM Limited
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
 *          Korey Sewell
 */

#ifndef __CPU_O3_INST_QUEUE_IMPL_HH__
#define __CPU_O3_INST_QUEUE_IMPL_HH__

#include <limits>
#include <vector>

#include "base/logging.hh"
#include "cpu/o3/fu_pool.hh"
#include "cpu/o3/inst_queue.hh"
#include "debug/IQ.hh"
#include "enums/OpClass.hh"
#include "params/DerivO3CPU.hh"
#include "sim/core.hh"
#include "sim/line_trace.hh"

// clang complains about std::set being overloaded with Packet::set if
// we open up the entire namespace std
using std::list;

template <class Impl>
InstructionQueue<Impl>::FUCompletion::FUCompletion(const DynInstPtr &_inst,
    int fu_idx, InstructionQueue<Impl> *iq_ptr)
    : Event(Stat_Event_Pri, AutoDelete),
      inst(_inst), fuIdx(fu_idx), iqPtr(iq_ptr), freeFU(false)
{
}

template <class Impl>
void
InstructionQueue<Impl>::FUCompletion::process()
{
    iqPtr->processFUCompletion(inst, freeFU ? fuIdx : -1);
    inst = NULL;
}


template <class Impl>
const char *
InstructionQueue<Impl>::FUCompletion::description() const
{
    return "Functional unit completion";
}

template <class Impl>
InstructionQueue<Impl>::InstructionQueue(O3CPU *cpu_ptr, IEW *iew_ptr,
                                         DerivO3CPUParams *params)
    : cpu(cpu_ptr),
      iewStage(iew_ptr),
      fuPool(params->fuPool),
      iqPolicy(params->smtIQPolicy),
      numEntries(params->numIQEntries),
      totalWidth(params->issueWidth),
      commitToIEWDelay(params->commitToIEWDelay),
      isInOrderIssue(params->isInOrderIssue)
{
    assert(fuPool);

    numThreads = params->numThreads;

    // Init timeBuffer and backward wire
    timeBuffer.resize(numThreads);
    fromCommit.resize(numThreads);

    // Set the number of total physical registers
    // As the vector registers have two addressing modes, they are added twice
    numPhysRegs = params->numPhysIntRegs + params->numPhysFloatRegs +
                    params->numPhysVecRegs +
                    params->numPhysVecRegs * TheISA::NumVecElemPerVecReg +
                    params->numPhysVecPredRegs +
                    params->numPhysCCRegs;

    //Create an entry for each physical register within the
    //dependency graph.
    dependGraph.resize(numPhysRegs);

    // Resize the register scoreboard.
    regScoreboard.resize(numPhysRegs);

    //Initialize Mem Dependence Units
    for (ThreadID tid = 0; tid < Impl::MaxThreads; tid++) {
        memDepUnit[tid].init(params, tid);
        memDepUnit[tid].setIQ(this);
    }

    resetState();

    //Figure out resource sharing policy
    if (iqPolicy == SMTQueuePolicy::Dynamic) {
        //Set Max Entries to Total ROB Capacity
        for (ThreadID tid = 0; tid < numThreads; tid++) {
            maxEntries[tid] = numEntries;
        }
    } else if (iqPolicy == SMTQueuePolicy::Partitioned) {
        //@todo:make work if part_amt doesnt divide evenly.
        int part_amt = numEntries / numThreads;

        //Divide ROB up evenly
        for (ThreadID tid = 0; tid < numThreads; tid++) {
            maxEntries[tid] = part_amt;
        }

        DPRINTF(IQ, "IQ sharing policy set to Partitioned:"
                "%i entries per thread.\n",part_amt);
    } else if (iqPolicy == SMTQueuePolicy::Threshold) {
        double threshold =  (double)params->smtIQThreshold / 100;

        int thresholdIQ = (int)((double)threshold * numEntries);

        //Divide up by threshold amount
        for (ThreadID tid = 0; tid < numThreads; tid++) {
            maxEntries[tid] = thresholdIQ;
        }

        DPRINTF(IQ, "IQ sharing policy set to Threshold:"
                "%i entries per thread.\n",thresholdIQ);
   }

   for (ThreadID tid = numThreads; tid < Impl::MaxThreads; tid++) {
       maxEntries[tid] = 0;
   }
}

template <class Impl>
InstructionQueue<Impl>::~InstructionQueue()
{
    dependGraph.reset();
#ifdef DEBUG
    cprintf("Nodes traversed: %i, removed: %i\n",
            dependGraph.nodesTraversed, dependGraph.nodesRemoved);
#endif
}

template <class Impl>
std::string
InstructionQueue<Impl>::name() const
{
    return cpu->name() + ".iq";
}

template <class Impl>
void
InstructionQueue<Impl>::regStats()
{
    using namespace Stats;
    iqInstsAdded
        .name(name() + ".iqInstsAdded")
        .desc("Number of instructions added to the IQ (excludes non-spec)")
        .prereq(iqInstsAdded);

    iqNonSpecInstsAdded
        .name(name() + ".iqNonSpecInstsAdded")
        .desc("Number of non-speculative instructions added to the IQ")
        .prereq(iqNonSpecInstsAdded);

    iqInstsIssued
        .name(name() + ".iqInstsIssued")
        .desc("Number of instructions issued")
        .prereq(iqInstsIssued);

    iqIntInstsIssued
        .name(name() + ".iqIntInstsIssued")
        .desc("Number of integer instructions issued")
        .prereq(iqIntInstsIssued);

    iqFloatInstsIssued
        .name(name() + ".iqFloatInstsIssued")
        .desc("Number of float instructions issued")
        .prereq(iqFloatInstsIssued);

    iqBranchInstsIssued
        .name(name() + ".iqBranchInstsIssued")
        .desc("Number of branch instructions issued")
        .prereq(iqBranchInstsIssued);

    iqMemInstsIssued
        .name(name() + ".iqMemInstsIssued")
        .desc("Number of memory instructions issued")
        .prereq(iqMemInstsIssued);

    iqMiscInstsIssued
        .name(name() + ".iqMiscInstsIssued")
        .desc("Number of miscellaneous instructions issued")
        .prereq(iqMiscInstsIssued);

    iqSquashedInstsIssued
        .name(name() + ".iqSquashedInstsIssued")
        .desc("Number of squashed instructions issued")
        .prereq(iqSquashedInstsIssued);

    iqSquashedInstsExamined
        .name(name() + ".iqSquashedInstsExamined")
        .desc("Number of squashed instructions iterated over during squash;"
              " mainly for profiling")
        .prereq(iqSquashedInstsExamined);

    iqSquashedOperandsExamined
        .name(name() + ".iqSquashedOperandsExamined")
        .desc("Number of squashed operands that are examined and possibly "
              "removed from graph")
        .prereq(iqSquashedOperandsExamined);

    iqSquashedNonSpecRemoved
        .name(name() + ".iqSquashedNonSpecRemoved")
        .desc("Number of squashed non-spec instructions that were removed")
        .prereq(iqSquashedNonSpecRemoved);
/*
    queueResDist
        .init(Num_OpClasses, 0, 99, 2)
        .name(name() + ".IQ:residence:")
        .desc("cycles from dispatch to issue")
        .flags(total | pdf | cdf )
        ;
    for (int i = 0; i < Num_OpClasses; ++i) {
        queueResDist.subname(i, opClassStrings[i]);
    }
*/
    numIssuedDist
        .init(0,totalWidth,1)
        .name(name() + ".issued_per_cycle")
        .desc("Number of insts issued each cycle")
        .flags(pdf)
        ;
/*
    dist_unissued
        .init(Num_OpClasses+2)
        .name(name() + ".unissued_cause")
        .desc("Reason ready instruction not issued")
        .flags(pdf | dist)
        ;
    for (int i=0; i < (Num_OpClasses + 2); ++i) {
        dist_unissued.subname(i, unissued_names[i]);
    }
*/
    statIssuedInstType
        .init(numThreads,Enums::Num_OpClass)
        .name(name() + ".FU_type")
        .desc("Type of FU issued")
        .flags(total | pdf | dist)
        ;
    statIssuedInstType.ysubnames(Enums::OpClassStrings);

    //
    //  How long did instructions for a particular FU type wait prior to issue
    //
/*
    issueDelayDist
        .init(Num_OpClasses,0,99,2)
        .name(name() + ".")
        .desc("cycles from operands ready to issue")
        .flags(pdf | cdf)
        ;

    for (int i=0; i<Num_OpClasses; ++i) {
        std::stringstream subname;
        subname << opClassStrings[i] << "_delay";
        issueDelayDist.subname(i, subname.str());
    }
*/
    issueRate
        .name(name() + ".rate")
        .desc("Inst issue rate")
        .flags(total)
        ;
    issueRate = iqInstsIssued / cpu->numCycles;

    statFuBusy
        .init(Num_OpClasses)
        .name(name() + ".fu_full")
        .desc("attempts to use FU when none available")
        .flags(pdf | dist)
        ;
    for (int i=0; i < Num_OpClasses; ++i) {
        statFuBusy.subname(i, Enums::OpClassStrings[i]);
    }

    fuBusy
        .init(numThreads)
        .name(name() + ".fu_busy_cnt")
        .desc("FU busy when requested")
        .flags(total)
        ;

    fuBusyRate
        .name(name() + ".fu_busy_rate")
        .desc("FU busy rate (busy events/executed inst)")
        .flags(total)
        ;
    fuBusyRate = fuBusy / iqInstsIssued;

    for (ThreadID tid = 0; tid < numThreads; tid++) {
        // Tell mem dependence unit to reg stats as well.
        memDepUnit[tid].regStats();
    }

    intInstQueueReads
        .name(name() + ".int_inst_queue_reads")
        .desc("Number of integer instruction queue reads")
        .flags(total);

    intInstQueueWrites
        .name(name() + ".int_inst_queue_writes")
        .desc("Number of integer instruction queue writes")
        .flags(total);

    intInstQueueWakeupAccesses
        .name(name() + ".int_inst_queue_wakeup_accesses")
        .desc("Number of integer instruction queue wakeup accesses")
        .flags(total);

    fpInstQueueReads
        .name(name() + ".fp_inst_queue_reads")
        .desc("Number of floating instruction queue reads")
        .flags(total);

    fpInstQueueWrites
        .name(name() + ".fp_inst_queue_writes")
        .desc("Number of floating instruction queue writes")
        .flags(total);

    fpInstQueueWakeupAccesses
        .name(name() + ".fp_inst_queue_wakeup_accesses")
        .desc("Number of floating instruction queue wakeup accesses")
        .flags(total);

    vecInstQueueReads
        .name(name() + ".vec_inst_queue_reads")
        .desc("Number of vector instruction queue reads")
        .flags(total);

    vecInstQueueWrites
        .name(name() + ".vec_inst_queue_writes")
        .desc("Number of vector instruction queue writes")
        .flags(total);

    vecInstQueueWakeupAccesses
        .name(name() + ".vec_inst_queue_wakeup_accesses")
        .desc("Number of vector instruction queue wakeup accesses")
        .flags(total);

    intAluAccesses
        .name(name() + ".int_alu_accesses")
        .desc("Number of integer alu accesses")
        .flags(total);

    fpAluAccesses
        .name(name() + ".fp_alu_accesses")
        .desc("Number of floating point alu accesses")
        .flags(total);

    vecAluAccesses
        .name(name() + ".vec_alu_accesses")
        .desc("Number of vector alu accesses")
        .flags(total);

}

template <class Impl>
void
InstructionQueue<Impl>::resetState()
{
    //Initialize thread IQ counts
    for (ThreadID tid = 0; tid < Impl::MaxThreads; tid++) {
        count[tid] = 0;
        instsToIssue[tid].clear();
    }

    // Initialize the number of free IQ entries.
    freeEntries = numEntries;

    // Note that in actuality, the registers corresponding to the logical
    // registers start off as ready.  However this doesn't matter for the
    // IQ as the instruction should have been correctly told if those
    // registers are ready in rename.  Thus it can all be initialized as
    // unready.
    for (int i = 0; i < numPhysRegs; ++i) {
        regScoreboard[i] = false;
    }

    for (ThreadID tid = 0; tid < Impl::MaxThreads; ++tid) {
        squashedSeqNum[tid] = 0;
    }

    while (!instsReadyToIssue.empty())
        instsReadyToIssue.pop();

    nonSpecInsts.clear();
    deferredMemInsts.clear();
    blockedMemInsts.clear();
    retryMemInsts.clear();
    wbOutstanding = 0;
}

template <class Impl>
void
InstructionQueue<Impl>::setActiveThreads(list<ThreadID> *at_ptr)
{
    activeThreads = at_ptr;
}

template <class Impl>
void
InstructionQueue<Impl>::setIssueToExecuteQueue(TimeBuffer<IssueStruct> *i2e_ptr)
{
      issueToExecuteQueue = i2e_ptr;
}

template <class Impl>
void
InstructionQueue<Impl>::setTimeBuffer(TimeBuffer<TimeStruct> *tb_ptr,
                                      ThreadID tid)
{
    timeBuffer[tid] = tb_ptr;

    fromCommit[tid] = timeBuffer[tid]->getWire(-commitToIEWDelay);
}

template <class Impl>
bool
InstructionQueue<Impl>::isDrained() const
{
    bool drained = dependGraph.empty() &&
                   instsToExecute.empty() &&
                   wbOutstanding == 0;
    for (ThreadID tid = 0; tid < numThreads; ++tid)
        drained = drained && memDepUnit[tid].isDrained();

    return drained;
}

template <class Impl>
void
InstructionQueue<Impl>::drainSanityCheck() const
{
    assert(dependGraph.empty());
    assert(instsToExecute.empty());
    for (ThreadID tid = 0; tid < numThreads; ++tid)
        memDepUnit[tid].drainSanityCheck();
}

template <class Impl>
void
InstructionQueue<Impl>::takeOverFrom()
{
    resetState();
}

template <class Impl>
void
InstructionQueue<Impl>::resetEntries()
{
    if (iqPolicy != SMTQueuePolicy::Dynamic || numThreads > 1) {
        int active_threads = activeThreads->size();

        list<ThreadID>::iterator threads = activeThreads->begin();
        list<ThreadID>::iterator end = activeThreads->end();

        while (threads != end) {
            ThreadID tid = *threads++;

            if (iqPolicy == SMTQueuePolicy::Partitioned) {
                maxEntries[tid] = numEntries / active_threads;
            } else if (iqPolicy == SMTQueuePolicy::Threshold &&
                       active_threads == 1) {
                maxEntries[tid] = numEntries;
            }
        }
    }
}

template <class Impl>
unsigned
InstructionQueue<Impl>::numFreeEntries()
{
    return freeEntries;
}

template <class Impl>
unsigned
InstructionQueue<Impl>::numFreeEntries(ThreadID tid)
{
    if (iqPolicy == SMTQueuePolicy::Dynamic)
        return freeEntries;

    return maxEntries[tid] - count[tid];
}

// Might want to do something more complex if it knows how many instructions
// will be issued this cycle.
template <class Impl>
bool
InstructionQueue<Impl>::isFull()
{
    if (freeEntries == 0) {
        return(true);
    } else {
        return(false);
    }
}

template <class Impl>
bool
InstructionQueue<Impl>::isFull(ThreadID tid)
{
    if (numFreeEntries(tid) == 0) {
        return(true);
    } else {
        return(false);
    }
}

template <class Impl>
bool
InstructionQueue<Impl>::hasReadyInsts()
{
    if (!instsReadyToIssue.empty())
        return true;

    return false;
}

template <class Impl>
void
InstructionQueue<Impl>::insert(const DynInstPtr &new_inst)
{
    if (new_inst->isFloating()) {
        fpInstQueueWrites++;
    } else if (new_inst->isVector()) {
        vecInstQueueWrites++;
    } else {
        intInstQueueWrites++;
    }
    // Make sure the instruction is valid
    assert(new_inst);

    DPRINTF(IQ, "Adding instruction [sn:%lli] PC %s to the IQ.\n",
            new_inst->seqNum, new_inst->pcState());

    assert(freeEntries != 0);

    instsToIssue[new_inst->threadNumber].push_back(new_inst);

    --freeEntries;

    new_inst->setInIQ();

    // Look through its source registers (physical regs), and mark any
    // dependencies.
    addToDependents(new_inst);

    // Have this instruction set itself as the producer of its destination
    // register(s).
    addToProducers(new_inst);

    if (new_inst->isMemRef()) {
        memDepUnit[new_inst->threadNumber].insert(new_inst);
    } else {
        addIfReady(new_inst);
    }

    ++iqInstsAdded;

    count[new_inst->threadNumber]++;

    assert(freeEntries == (numEntries - countInsts()));
}

template <class Impl>
void
InstructionQueue<Impl>::insertNonSpec(const DynInstPtr &new_inst)
{
    // @todo: Clean up this code; can do it by setting inst as unable
    // to issue, then calling normal insert on the inst.
    if (new_inst->isFloating()) {
        fpInstQueueWrites++;
    } else if (new_inst->isVector()) {
        vecInstQueueWrites++;
    } else {
        intInstQueueWrites++;
    }

    assert(new_inst);

    nonSpecInsts[new_inst->seqNum] = new_inst;

    DPRINTF(IQ, "Adding non-speculative instruction [sn:%lli] PC %s "
            "to the IQ.\n",
            new_inst->seqNum, new_inst->pcState());

    assert(freeEntries != 0);

    instsToIssue[new_inst->threadNumber].push_back(new_inst);

    --freeEntries;

    new_inst->setInIQ();

    // Have this instruction set itself as the producer of its destination
    // register(s).
    addToProducers(new_inst);

    // If it's a memory instruction, add it to the memory dependency
    // unit.
    if (new_inst->isMemRef()) {
        memDepUnit[new_inst->threadNumber].insertNonSpec(new_inst);
    }

    ++iqNonSpecInstsAdded;

    count[new_inst->threadNumber]++;

    assert(freeEntries == (numEntries - countInsts()));
}

template <class Impl>
void
InstructionQueue<Impl>::insertBarrier(const DynInstPtr &barr_inst)
{
    memDepUnit[barr_inst->threadNumber].insertBarrier(barr_inst);
}

template <class Impl>
typename Impl::DynInstPtr
InstructionQueue<Impl>::getInstToExecute()
{
    assert(!instsToExecute.empty());
    DynInstPtr inst = std::move(instsToExecute.front());
    instsToExecute.pop_front();
    if (inst->isFloating()) {
        fpInstQueueReads++;
    } else if (inst->isVector()) {
        vecInstQueueReads++;
    } else {
        intInstQueueReads++;
    }
    return inst;
}

template <class Impl>
void
InstructionQueue<Impl>::processFUCompletion(const DynInstPtr &inst, int fu_idx)
{
    DPRINTF(IQ, "Processing FU completion [sn:%lli]\n", inst->seqNum);
    assert(!cpu->switchedOut());
    // The CPU could have been sleeping until this op completed (*extremely*
    // long latency op).  Wake it if it was.  This may be overkill.
   --wbOutstanding;
    iewStage->wakeCPU();

    if (fu_idx > -1)
        fuPool->freeUnitNextCycle(fu_idx);

    // @todo: Ensure that these FU Completions happen at the beginning
    // of a cycle, otherwise they could add too many instructions to
    // the queue.
    issueToExecuteQueue->access(-1)->size++;
    instsToExecute.push_back(inst);
}

// @todo: Figure out a better way to remove the squashed items from the
// lists.  Checking the top item of each list to see if it's squashed
// wastes time and forces jumps.
template <class Impl>
void
InstructionQueue<Impl>::scheduleReadyInsts()
{
    DPRINTF(IQ, "Attempting to schedule ready instructions from "
            "the IQ.\n");

    IssueStruct *i2e_info = issueToExecuteQueue->access(0);

    DynInstPtr mem_inst;
    while (mem_inst = std::move(getDeferredMemInstToExecute())) {
        addReadyMemInst(mem_inst);
    }

    // See if any cache blocked instructions are able to be executed
    while (mem_inst = std::move(getBlockedMemInstToExecute())) {
        addReadyMemInst(mem_inst);
    }

    int total_issued = 0;
    std::vector<DynInstPtr> unissuedInsts;

    while (total_issued < totalWidth && !instsReadyToIssue.empty()) {
        DynInstPtr issuing_inst = instsReadyToIssue.top();
        OpClass op_class = issuing_inst->opClass();

        if (issuing_inst->isFloating()) {
            fpInstQueueReads++;
        } else if (issuing_inst->isVector()) {
            vecInstQueueReads++;
        } else {
            intInstQueueReads++;
        }

        // check if issuing_inst has been squashed
        if (issuing_inst->isSquashed()) {
            instsReadyToIssue.pop();
            ++iqSquashedInstsIssued;
            continue;
        }

        ThreadID tid = issuing_inst->threadNumber;

        // If we're in the in-order issue mode, we need to check if
        // issuing_inst is the oldest instruction from its thread. If not, it
        // can't be issued now.
        if (isInOrderIssue && !instsToIssue[tid].empty() &&
            issuing_inst->seqNum > instsToIssue[tid].front()->seqNum) {
            DPRINTF(IQ, "Thread %i: Can't issue instruction PC %s "
                    "[sn:%lli] - blocked by older instruction [sn:%lli]\n",
                    tid, issuing_inst->pcState(),
                    issuing_inst->seqNum, instsToIssue[tid].front()->seqNum);

            // Temporarily place issuing_inst into unissuedInsts list
            unissuedInsts.push_back(issuing_inst);
            instsReadyToIssue.pop();
            continue;
        }

        // Look for an available FU to execute issuing_inst

        int idx = FUPool::NoCapableFU;
        Cycles op_latency = Cycles(1);

        if (op_class != No_OpClass) {
            idx = fuPool->getUnit(op_class);
            if (issuing_inst->isFloating()) {
                fpAluAccesses++;
            } else if (issuing_inst->isVector()) {
                vecAluAccesses++;
            } else {
                intAluAccesses++;
            }
            if (idx > FUPool::NoFreeFU) {
                op_latency = fuPool->getOpLatency(op_class);
            }
        }

        // If we have an instruction that doesn't require a FU, or a
        // valid FU, then schedule for execution.
        if (idx != FUPool::NoFreeFU) {
            if (op_latency == Cycles(1)) {
                i2e_info->size++;
                instsToExecute.push_back(issuing_inst);

                // Add the FU onto the list of FU's to be freed next
                // cycle if we used one.
                if (idx >= 0)
                    fuPool->freeUnitNextCycle(idx);
            } else {
                bool pipelined = fuPool->isPipelined(op_class);
                // Generate completion event for the FU
                ++wbOutstanding;
                FUCompletion *execution = new FUCompletion(issuing_inst,
                                                           idx, this);

                cpu->schedule(execution,
                              cpu->clockEdge(Cycles(op_latency - 1)));

                if (!pipelined) {
                    // If FU isn't pipelined, then it must be freed
                    // upon the execution completing.
                    execution->setFreeFU();
                } else {
                    // Add the FU onto the list of FU's to be freed next cycle.
                    fuPool->freeUnitNextCycle(idx);
                }
            }

            DPRINTF(IQ, "Thread %i: Issuing instruction PC %s "
                    "[sn:%lli]\n",
                    tid, issuing_inst->pcState(),
                    issuing_inst->seqNum);

            instsReadyToIssue.pop();

            issuing_inst->setIssued();
            ++total_issued;

            // Search for the issued instruction from instsToIssue list
            // If the instruction is not in the list, it is a
            // replayed/rescheduled instruction.
            auto it = std::find_if(instsToIssue[tid].begin(),
                                   instsToIssue[tid].end(),
                                   [&issuing_inst](const DynInstPtr &inst)
                        { return issuing_inst->seqNum == inst->seqNum; } );

            if (it != instsToIssue[tid].end()) {
                // Remove the issued instruction from instsToIssue list
                // Reclaim free slots in instruction queue
                instsToIssue[tid].erase(it);
                ++freeEntries;
                count[tid]--;
#if TRACING_ON
                // We only count the first time an instruction is issued, not
                // when it is rescheduled.
                issuing_inst->issueTick = curTick() - issuing_inst->fetchTick;
#endif
                LineTracer::getLineTracer()->
                            recordInst(issuing_inst->contextId(),
                                       LineTracer::Issue,
                                       issuing_inst->instAddr());
            }

            issuing_inst->clearInIQ();

            if (issuing_inst->isMemRef())
                memDepUnit[tid].issue(issuing_inst);

            statIssuedInstType[tid][op_class]++;
        } else {
            DPRINTF(IQ, "Thread %i: Can't issue instruction PC %s "
                    "[sn:%lli] - no FU available\n",
                    tid, issuing_inst->pcState(),
                    issuing_inst->seqNum);

            statFuBusy[op_class]++;
            fuBusy[tid]++;

            // Temporarily place issuing_inst into unissuedInsts list
            unissuedInsts.push_back(issuing_inst);
            instsReadyToIssue.pop();
        }
    }

    // For unissued instructions, push them back to the instsReadyToIssue so
    // that they can be scheduled in the future
    while (!unissuedInsts.empty()) {
        instsReadyToIssue.push(unissuedInsts.back());
        unissuedInsts.pop_back();
    }

    numIssuedDist.sample(total_issued);
    iqInstsIssued+= total_issued;

    // If we issued any instructions, tell the CPU we had activity.
    // @todo If the way deferred memory instructions are handeled due to
    // translation changes then the deferredMemInsts condition should be removed
    // from the code below.
    if (total_issued || !retryMemInsts.empty() || !deferredMemInsts.empty()) {
        cpu->activityThisCycle();
    } else {
        DPRINTF(IQ, "Not able to schedule any instructions.\n");
    }
}

template <class Impl>
void
InstructionQueue<Impl>::scheduleNonSpec(const InstSeqNum &inst)
{
    DPRINTF(IQ, "Marking nonspeculative instruction [sn:%lli] as ready "
            "to execute.\n", inst);

    NonSpecMapIt inst_it = nonSpecInsts.find(inst);

    assert(inst_it != nonSpecInsts.end());

    ThreadID tid = (*inst_it).second->threadNumber;

    (*inst_it).second->setAtCommit();

    (*inst_it).second->setCanIssue();

    if (!(*inst_it).second->isMemRef()) {
        addIfReady((*inst_it).second);
    } else {
        memDepUnit[tid].nonSpecInstReady((*inst_it).second);
    }

    (*inst_it).second = NULL;

    nonSpecInsts.erase(inst_it);
}

template <class Impl>
void
InstructionQueue<Impl>::commit(const InstSeqNum &inst, ThreadID tid)
{
    DPRINTF(IQ, "[tid:%i]: Committing instructions older than [sn:%i]\n",
            tid,inst);

    ListIt iq_it = instsToIssue[tid].begin();

    while (iq_it != instsToIssue[tid].end() &&
           (*iq_it)->seqNum <= inst) {
        ++iq_it;
        instsToIssue[tid].pop_front();
    }

    assert(freeEntries == (numEntries - countInsts()));
}

template <class Impl>
int
InstructionQueue<Impl>::wakeDependents(const DynInstPtr &completed_inst)
{
    int dependents = 0;

    // The instruction queue here takes care of both floating and int ops
    if (completed_inst->isFloating()) {
        fpInstQueueWakeupAccesses++;
    } else if (completed_inst->isVector()) {
        vecInstQueueWakeupAccesses++;
    } else {
        intInstQueueWakeupAccesses++;
    }

    DPRINTF(IQ, "Waking dependents of completed instruction.\n");

    assert(!completed_inst->isSquashed());

    // Tell the memory dependence unit to wake any dependents on this
    // instruction if it is a memory instruction.  Also complete the memory
    // instruction at this point since we know it executed without issues.
    // @todo: Might want to rename "completeMemInst" to something that
    // indicates that it won't need to be replayed, and call this
    // earlier.  Might not be a big deal.
    if (completed_inst->isMemRef()) {
        memDepUnit[completed_inst->threadNumber].wakeDependents(completed_inst);
        completeMemInst(completed_inst);
    } else if (completed_inst->isMemBarrier() ||
               completed_inst->isWriteBarrier()) {
        memDepUnit[completed_inst->threadNumber].completeBarrier(completed_inst);
    }

    for (int dest_reg_idx = 0;
         dest_reg_idx < completed_inst->numDestRegs();
         dest_reg_idx++)
    {
        PhysRegIdPtr dest_reg =
            completed_inst->renamedDestRegIdx(dest_reg_idx);

        // Special case of uniq or control registers.  They are not
        // handled by the IQ and thus have no dependency graph entry.
        if (dest_reg->isFixedMapping()) {
            DPRINTF(IQ, "Reg %d [%s] is part of a fix mapping, skipping\n",
                    dest_reg->index(), dest_reg->className());
            continue;
        }

        DPRINTF(IQ, "Waking any dependents on register %i (%s).\n",
                dest_reg->index(),
                dest_reg->className());

        //Go through the dependency chain, marking the registers as
        //ready within the waiting instructions.
        DynInstPtr dep_inst = dependGraph.pop(dest_reg->flatIndex());

        while (dep_inst) {
            if (!dep_inst->isSquashed()) {
                DPRINTF(IQ, "Waking up a dependent instruction, [sn:%lli] "
                        "PC %s.\n", dep_inst->seqNum, dep_inst->pcState());

                // Might want to give more information to the instruction
                // so that it knows which of its source registers is
                // ready.  However that would mean that the dependency
                // graph entries would need to hold the src_reg_idx.
                dep_inst->markSrcRegReady();

                addIfReady(dep_inst);

                ++dependents;
            }

            dep_inst = dependGraph.pop(dest_reg->flatIndex());
        }

        // Reset the head node now that all of its dependents have
        // been woken up.
        assert(dependGraph.empty(dest_reg->flatIndex()));
        dependGraph.clearInst(dest_reg->flatIndex());

        // Mark the scoreboard as having that register ready.
        regScoreboard[dest_reg->flatIndex()] = true;
    }
    return dependents;
}

template <class Impl>
void
InstructionQueue<Impl>::addReadyMemInst(const DynInstPtr &ready_inst)
{
    OpClass op_class = ready_inst->opClass();

    instsReadyToIssue.push(ready_inst);

    DPRINTF(IQ, "Instruction is ready to issue, putting it onto "
            "the ready list, PC %s opclass:%i [sn:%lli].\n",
            ready_inst->pcState(), op_class, ready_inst->seqNum);
}

template <class Impl>
void
InstructionQueue<Impl>::rescheduleMemInst(const DynInstPtr &resched_inst)
{
    DPRINTF(IQ, "Rescheduling mem inst [sn:%lli]\n", resched_inst->seqNum);

    // Reset DTB translation state
    resched_inst->translationStarted(false);
    resched_inst->translationCompleted(false);

    resched_inst->clearCanIssue();
    memDepUnit[resched_inst->threadNumber].reschedule(resched_inst);
}

template <class Impl>
void
InstructionQueue<Impl>::replayMemInst(const DynInstPtr &replay_inst)
{
    memDepUnit[replay_inst->threadNumber].replay();
}

template <class Impl>
void
InstructionQueue<Impl>::completeMemInst(const DynInstPtr &completed_inst)
{
    ThreadID tid = completed_inst->threadNumber;

    DPRINTF(IQ, "Completing mem instruction PC: %s [sn:%lli]\n",
            completed_inst->pcState(), completed_inst->seqNum);

    completed_inst->memOpDone(true);

    // Only need to inform memDepUnit that this mem instruction is completed.
    // The instruction has been popped from instsToIssue list when it was
    // scheduled to execute earlier, so there is no need to free it or reclaim
    // free slot in instruction queue here.
    memDepUnit[tid].completed(completed_inst);
}

template <class Impl>
void
InstructionQueue<Impl>::deferMemInst(const DynInstPtr &deferred_inst)
{
    deferredMemInsts.push_back(deferred_inst);
}

template <class Impl>
void
InstructionQueue<Impl>::blockMemInst(const DynInstPtr &blocked_inst)
{
    blocked_inst->clearIssued();
    blocked_inst->clearCanIssue();
    blockedMemInsts.push_back(blocked_inst);
}

template <class Impl>
void
InstructionQueue<Impl>::cacheUnblocked()
{
    retryMemInsts.splice(retryMemInsts.end(), blockedMemInsts);
    // Get the CPU ticking again
    cpu->wakeCPU();
}

template <class Impl>
typename Impl::DynInstPtr
InstructionQueue<Impl>::getDeferredMemInstToExecute()
{
    for (ListIt it = deferredMemInsts.begin(); it != deferredMemInsts.end();
         ++it) {
        if ((*it)->translationCompleted() || (*it)->isSquashed()) {
            DynInstPtr mem_inst = std::move(*it);
            deferredMemInsts.erase(it);
            return mem_inst;
        }
    }
    return nullptr;
}

template <class Impl>
typename Impl::DynInstPtr
InstructionQueue<Impl>::getBlockedMemInstToExecute()
{
    if (retryMemInsts.empty()) {
        return nullptr;
    } else {
        DynInstPtr mem_inst = std::move(retryMemInsts.front());
        retryMemInsts.pop_front();
        return mem_inst;
    }
}

template <class Impl>
void
InstructionQueue<Impl>::violation(const DynInstPtr &store,
                                  const DynInstPtr &faulting_load)
{
    intInstQueueWrites++;
    memDepUnit[store->threadNumber].violation(store, faulting_load);
}

template <class Impl>
void
InstructionQueue<Impl>::squash(ThreadID tid)
{
    DPRINTF(IQ, "[tid:%i]: Starting to squash instructions in "
            "the IQ.\n", tid);

    // Read instruction sequence number of last instruction out of the time
    // buffer.
    squashedSeqNum[tid] = fromCommit[tid]->commitInfo.doneSeqNum;

    // Squash any instruction younger than the squashed sequence number given
    // from Commit stage in instsToIssue list. This will free up space in the
    // instruction queue.

    // Start at the tail.
    ListIt squash_it = instsToIssue[tid].end();
    --squash_it;

    DPRINTF(IQ, "[tid:%i]: Squashing until sequence number %i!\n",
            tid, squashedSeqNum[tid]);

    while ( squash_it != instsToIssue[tid].end() &&
           (*squash_it)->seqNum > squashedSeqNum[tid]) {

        DynInstPtr squashed_inst = (*squash_it);

        assert(squashed_inst->threadNumber == tid);
        // assert that the squashed_inst has not been squashed yet
        assert(!squashed_inst->isSquashedInIQ());

        DPRINTF(IQ, "[tid:%u]: Squashing instruction [sn:%i], "
                "%s squashed in ROB\n",
                squashed_inst->threadNumber,
                squashed_inst->seqNum,
                squashed_inst->isSquashed() ? "already" : "not yet");
        // Mark it as squashed within the IQ.
        squashed_inst->setSquashedInIQ();

        // @todo: Remove this hack where several statuses are set so the
        // inst will flow through the rest of the pipeline.
        squashed_inst->setIssued();
        squashed_inst->setCanCommit();
        squashed_inst->clearInIQ();

        // remove squashed_inst from instsToIssue
        instsToIssue[tid].erase(squash_it--);

        // search for squashed_inst in nonSpecInsts map
        auto it = nonSpecInsts.find(squashed_inst->seqNum);
        if (it != nonSpecInsts.end()) {
            assert(squashed_inst->isNonSpeculative() ||
                   squashed_inst->isStoreConditional() ||
                   squashed_inst->isAtomic() ||
                   squashed_inst->isMemBarrier() ||
                   squashed_inst->isWriteBarrier());
            (*it).second = nullptr;
            nonSpecInsts.erase(it);
            ++iqSquashedNonSpecRemoved;
        }

        // Update Thread IQ Count and reclaim free slot
        count[tid]--;
        ++freeEntries;

        ++iqSquashedInstsExamined;

        // No need to inspect other lists including instsReadyToIssue and
        // instsToExecute because when instructions popped from those lists,
        // they're checked whether they have been already squashed. Also no
        // free slot in instruction queue is occupied when they move out of
        // instsToIssue list.
    }

    // We need to squash all instructions younger than the squashedSeqNum
    // in the dependency graph as well
    dependGraph.squash(tid, squashedSeqNum[tid]);

    // Also tell the memory dependence unit to squash.
    memDepUnit[tid].squash(squashedSeqNum[tid], tid);
}

template <class Impl>
bool
InstructionQueue<Impl>::addToDependents(const DynInstPtr &new_inst)
{
    // Loop through the instruction's source registers, adding
    // them to the dependency list if they are not ready.
    int8_t total_src_regs = new_inst->numSrcRegs();
    bool return_val = false;

    for (int src_reg_idx = 0;
         src_reg_idx < total_src_regs;
         src_reg_idx++)
    {
        // Only add it to the dependency graph if it's not ready.
        if (!new_inst->isReadySrcRegIdx(src_reg_idx)) {
            PhysRegIdPtr src_reg = new_inst->renamedSrcRegIdx(src_reg_idx);

            // Check the IQ's scoreboard to make sure the register
            // hasn't become ready while the instruction was in flight
            // between stages.  Only if it really isn't ready should
            // it be added to the dependency graph.
            if (src_reg->isFixedMapping()) {
                continue;
            } else if (!regScoreboard[src_reg->flatIndex()]) {
                DPRINTF(IQ, "Instruction PC %s has src reg %i (%s) that "
                        "is being added to the dependency chain.\n",
                        new_inst->pcState(), src_reg->index(),
                        src_reg->className());

                dependGraph.insert(src_reg->flatIndex(), new_inst);

                // Change the return value to indicate that something
                // was added to the dependency graph.
                return_val = true;
            } else {
                DPRINTF(IQ, "Instruction PC %s has src reg %i (%s) that "
                        "became ready before it reached the IQ.\n",
                        new_inst->pcState(), src_reg->index(),
                        src_reg->className());
                // Mark a register ready within the instruction.
                new_inst->markSrcRegReady(src_reg_idx);
            }
        }
    }

    return return_val;
}

template <class Impl>
void
InstructionQueue<Impl>::addToProducers(const DynInstPtr &new_inst)
{
    // Nothing really needs to be marked when an instruction becomes
    // the producer of a register's value, but for convenience a ptr
    // to the producing instruction will be placed in the head node of
    // the dependency links.
    int8_t total_dest_regs = new_inst->numDestRegs();

    for (int dest_reg_idx = 0;
         dest_reg_idx < total_dest_regs;
         dest_reg_idx++)
    {
        PhysRegIdPtr dest_reg = new_inst->renamedDestRegIdx(dest_reg_idx);

        // Some registers have fixed mapping, and there is no need to track
        // dependencies as these instructions must be executed at commit.
        if (dest_reg->isFixedMapping()) {
            continue;
        }

        if (!dependGraph.empty(dest_reg->flatIndex())) {
            dependGraph.dump();
            panic("Dependency graph %i (%s) (flat: %i) not empty!",
                  dest_reg->index(), dest_reg->className(),
                  dest_reg->flatIndex());
        }

        dependGraph.setInst(dest_reg->flatIndex(), new_inst);

        // Mark the scoreboard to say it's not yet ready.
        regScoreboard[dest_reg->flatIndex()] = false;
    }
}

template <class Impl>
void
InstructionQueue<Impl>::addIfReady(const DynInstPtr &inst)
{
    // If the instruction now has all of its source registers
    // available, then add it to the list of ready instructions.
    if (inst->readyToIssue()) {

        //Add the instruction to the proper ready list.
        if (inst->isMemRef()) {

            DPRINTF(IQ, "Checking if memory instruction can issue.\n");

            // Message to the mem dependence unit that this instruction has
            // its registers ready.
            memDepUnit[inst->threadNumber].regsReady(inst);

            return;
        }

        OpClass op_class = inst->opClass();

        DPRINTF(IQ, "Instruction is ready to issue, putting it onto "
                "the ready list, PC %s opclass:%i [sn:%lli].\n",
                inst->pcState(), op_class, inst->seqNum);

        instsReadyToIssue.push(inst);
    }
}

template <class Impl>
int
InstructionQueue<Impl>::countInsts()
{
    return numEntries - freeEntries;
}

template <class Impl>
void
InstructionQueue<Impl>::dumpLists()
{
    cprintf("Ready list size: %i\n", instsReadyToIssue.size());

    cprintf("Non speculative list size: %i\n", nonSpecInsts.size());

    NonSpecMapIt non_spec_it = nonSpecInsts.begin();
    NonSpecMapIt non_spec_end_it = nonSpecInsts.end();

    cprintf("Non speculative list: ");

    while (non_spec_it != non_spec_end_it) {
        cprintf("%s [sn:%lli]", (*non_spec_it).second->pcState(),
                (*non_spec_it).second->seqNum);
        ++non_spec_it;
    }

    cprintf("\n");
}


template <class Impl>
void
InstructionQueue<Impl>::dumpInsts()
{
    for (ThreadID tid = 0; tid < numThreads; ++tid) {
        int num = 0;
        int valid_num = 0;
        ListIt inst_list_it = instsToIssue[tid].begin();

        while (inst_list_it != instsToIssue[tid].end()) {
            cprintf("Instruction:%i\n", num);
            if (!(*inst_list_it)->isSquashed()) {
                if (!(*inst_list_it)->isIssued()) {
                    ++valid_num;
                    cprintf("Count:%i\n", valid_num);
                } else if ((*inst_list_it)->isMemRef() &&
                           !(*inst_list_it)->memOpDone()) {
                    // Loads that have not been marked as executed
                    // still count towards the total instructions.
                    ++valid_num;
                    cprintf("Count:%i\n", valid_num);
                }
            }

            cprintf("PC: %s\n[sn:%lli]\n[tid:%i]\n"
                    "Issued:%i\nSquashed:%i\n",
                    (*inst_list_it)->pcState(),
                    (*inst_list_it)->seqNum,
                    (*inst_list_it)->threadNumber,
                    (*inst_list_it)->isIssued(),
                    (*inst_list_it)->isSquashed());

            if ((*inst_list_it)->isMemRef()) {
                cprintf("MemOpDone:%i\n", (*inst_list_it)->memOpDone());
            }

            cprintf("\n");

            inst_list_it++;
            ++num;
        }
    }

    cprintf("Insts to Execute list:\n");

    int num = 0;
    int valid_num = 0;
    ListIt inst_list_it = instsToExecute.begin();

    while (inst_list_it != instsToExecute.end())
    {
        cprintf("Instruction:%i\n",
                num);
        if (!(*inst_list_it)->isSquashed()) {
            if (!(*inst_list_it)->isIssued()) {
                ++valid_num;
                cprintf("Count:%i\n", valid_num);
            } else if ((*inst_list_it)->isMemRef() &&
                       !(*inst_list_it)->memOpDone()) {
                // Loads that have not been marked as executed
                // still count towards the total instructions.
                ++valid_num;
                cprintf("Count:%i\n", valid_num);
            }
        }

        cprintf("PC: %s\n[sn:%lli]\n[tid:%i]\n"
                "Issued:%i\nSquashed:%i\n",
                (*inst_list_it)->pcState(),
                (*inst_list_it)->seqNum,
                (*inst_list_it)->threadNumber,
                (*inst_list_it)->isIssued(),
                (*inst_list_it)->isSquashed());

        if ((*inst_list_it)->isMemRef()) {
            cprintf("MemOpDone:%i\n", (*inst_list_it)->memOpDone());
        }

        cprintf("\n");

        inst_list_it++;
        ++num;
    }
}

#endif//__CPU_O3_INST_QUEUE_IMPL_HH__
