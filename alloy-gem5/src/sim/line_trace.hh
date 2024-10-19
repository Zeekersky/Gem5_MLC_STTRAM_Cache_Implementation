//=============================================================================
// line_trace.hh
//=============================================================================
//
// Support printing per-cycle CPU's activities
//
// Author : Tuan Ta
// Date   : 03/11/2019
//

#ifndef __LINE_TRACE_HH__
#define __LINE_TRACE_HH__

#include "cpu/inst_seq.hh"
#include "sim/global_event.hh"

class LineTracer;

class LineTraceEvent : public GlobalEvent
{
  public:
    LineTraceEvent(LineTracer* _tracer);

    void process() override;

    const char *description() const override;

  private:
    LineTracer* tracer;
};

class LineTracer
{
  public:
    enum CpuStage {
        Fetch,
        Decode,
        Rename,
        Issue,
        Writeback,
        Commit,
        StoreRetire,
        NumStages
    };

    // return the unique global line tracer. Create one if it doesn't exist yet
    static LineTracer* getLineTracer();

    // add new CPU thread contexts.
    // This function is called when a new CPU is created.
    // n_threads: number of new contexts
    // is_vmt: do threads work in vertical multithreading mode?
    void addThreadContexts(unsigned int n_threads, bool is_vmt);

    // set CPU clock period. Assuming all CPUs have the same frequency
    void setCpuClockPeriod(Tick _period);

    // return the CPU's clock period
    Tick getCpuClockPeriod() const;

    // record an instruction's event in a given stage of a CPU
    void recordInst(int ctid, CpuStage stage, Addr pc);

    // record assembly format of a given instruction
    void recordInstAsm(int ctid, const std::string& asm_str,
                       InstSeqNum seq_num);

    // dump line traces to std::cout
    void dump();

  private:
    LineTracer();

    // Unique global tracer
    static LineTracer* line_tracer;

    // Total number of CPUs
    unsigned int num_cpus;

    // Total number of thread contexts
    unsigned int num_threads;

    // Are CPUs VMT?
    bool is_cpu_vmt;

    // Clock period of CPUs, assuming all CPUs have the same frequency
    Tick cpu_clock_period;

    // Event to dump line traces every CPU cycle
    LineTraceEvent* dump_event;

    // Vector of PCs in all stages
    typedef std::vector<Addr> PCVector;
    std::vector<PCVector> threads;

    // Vector of all instructions in assembly format across all threads
    std::vector<std::string> insts;

    // Vector of instruction's seq numbers across all threads
    std::vector<InstSeqNum> instSeqNums;

    void dump_smt();
    void dump_vmt();
};

#endif // LINE_TRACE_HH
