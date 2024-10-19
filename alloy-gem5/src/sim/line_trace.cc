//=============================================================================
// line_trace.cc
//=============================================================================
//
// Support printing per-cycle CPU's activities
//
// Author : Tuan Ta
// Date   : 03/11/2019
//

#include "sim/line_trace.hh"

#include <iomanip>
#include <sstream>

#include "debug/LineTrace.hh"

LineTracer* LineTracer::line_tracer = nullptr;

//-----------------------------------------------------------------------------
// LineTraceEvent
//-----------------------------------------------------------------------------

LineTraceEvent::LineTraceEvent(LineTracer* _tracer)
    : GlobalEvent(Stat_Event_Pri, 0),
      tracer(_tracer)
{
    schedule(curTick());
}

void
LineTraceEvent::process()
{
    tracer->dump();
    // schedule another event in the next cycle when CPUs tick
    schedule(curTick() + tracer->getCpuClockPeriod());
}

const char*
LineTraceEvent::description() const
{
    return "Line trace event";
}

//-----------------------------------------------------------------------------
// LineTracer
//-----------------------------------------------------------------------------

LineTracer::LineTracer()
    : num_cpus(0),
      num_threads(0),
      is_cpu_vmt(false),
      cpu_clock_period(0),
      dump_event(new LineTraceEvent(this))
{ }

LineTracer*
LineTracer::getLineTracer()
{
    if (!line_tracer)
        line_tracer = new LineTracer();
    return line_tracer;
}

void
LineTracer::addThreadContexts(unsigned int nthreads, bool is_vmt)
{
    num_cpus++;
    num_threads += nthreads;
    is_cpu_vmt = is_vmt;

    threads.resize(num_threads);
    insts.resize(num_threads);
    instSeqNums.resize(num_threads);
    for (auto& t : threads)
        t.resize(NumStages);
}

void
LineTracer::setCpuClockPeriod(Tick _period)
{
    cpu_clock_period = _period;
}

Tick
LineTracer::getCpuClockPeriod() const
{
    assert(cpu_clock_period != 0);
    return cpu_clock_period;
}

void
LineTracer::recordInst(ContextID ctid, CpuStage stage, Addr pc)
{
    if (DTRACE(LineTrace)) {
        assert(ctid < threads.size());
        threads[ctid][stage] = pc;
    }
}

void
LineTracer::recordInstAsm(ContextID ctid, const std::string& asm_str,
                          InstSeqNum seq_num)
{
    if (DTRACE(LineTrace)) {
        assert(ctid < threads.size());
        insts[ctid] = asm_str;
        instSeqNums[ctid] = seq_num;
    }
}

void
LineTracer::dump()
{
    assert(cpu_clock_period != 0);
    assert(threads.size() != 0);
    if (DTRACE(LineTrace)) {
        if (is_cpu_vmt)
            dump_vmt();
        else
            dump_smt();
    }
}

void
LineTracer::dump_smt()
{
    using namespace std;
    stringstream ss;
    ss << setw(10) << (curTick()/cpu_clock_period) << ": ";

    for (int tid = 0; tid < threads.size(); tid++) {
        ss << std::left << setw(25) << insts[tid]
           << " [sn:" << setw(10) << instSeqNums[tid] << "]"
           << std::right;

        for (int s = 0; s < NumStages; s++) {
//          for (int s = 0; s < Decode; s++) {
            if (threads[tid][s] == 0)
                ss << setw(10) << ".";
            else
                ss << hex << setw(10) << threads[tid][s] << dec;

            threads[tid][s] = 0;
        }

        ss << " ||";
        insts[tid] = "";
        instSeqNums[tid] = 0;
    }

    DPRINTF(LineTrace, "%s\n", ss.str());
}

void
LineTracer::dump_vmt()
{
    assert(num_threads % num_cpus == 0);
    int n_threads_per_cpu = num_threads / num_cpus;

    using namespace std;
    stringstream ss;
    ss << setw(10) << (curTick()/cpu_clock_period) << ": ";

    for (int cpu_id = 0; cpu_id < num_cpus; ++cpu_id) {
        for (int s = 0; s < NumStages; s++) {
            // for each stage, pick one value from a thread that had activity
            // in that stage
            int sel_tid = -1;

            for (int tid = cpu_id * n_threads_per_cpu;
                    tid < (cpu_id + 1) * n_threads_per_cpu; tid++) {
                if (threads[tid][s] != 0) {
                    assert(sel_tid == -1);
                    sel_tid = tid;
                }
            }

            // print trace
            if (s == 0) {
                if (sel_tid == -1)
                    ss << std::left << setw(25) << ""
                       << " [sn:" << setw(10) << 0 << "]"
                       << std::right;
                else
                    ss << std::left << setw(25) << insts[sel_tid]
                       << " [sn:" << setw(10) << instSeqNums[sel_tid] << "]"
                       << std::right;
            }

            string tid_str("(");
            tid_str.append(to_string(sel_tid));
            tid_str.append(")");

            if (sel_tid == -1)
                ss << setw(20) << ".";
            else
                ss << hex << setw(15) << threads[sel_tid][s]
                   << dec << setw(5)  << tid_str;
        }

        ss << " ||";
    }

    DPRINTF(LineTrace, "%s\n", ss.str());

    // reset all data fields
    for (int tid = 0; tid < threads.size(); tid++) {
        for (int s = 0; s < NumStages; s++)
            threads[tid][s] = 0;
        insts[tid] = "";
        instSeqNums[tid] = 0;
    }
}
