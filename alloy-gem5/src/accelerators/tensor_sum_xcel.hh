//=============================================================================
// tensor_sum_xcel.hh
//=============================================================================
//
// Author: Tuan Ta
// Date  : 19/07/17

#ifndef __TENSOR_SUM_XCEL_HH__
#define __TENSOR_SUM_XCEL_HH__

#include "accelerators/memory_mapped_xcel.hh"
#include "params/TensorSumXcel.hh"
#include "sim/process.hh"

class TensorSumXcel : public MemoryMappedXcel {
  public:
    typedef TensorSumXcelParams Params;
    TensorSumXcel(const Params* p);
    ~TensorSumXcel() = default;

    void tick() override;
    bool processMemResp(Packet* pkt_p) override;
    void retry() override;

  private:
    /**
     * FSM states
     */
    enum State {
      Idle,         // waiting to read base_spm_vaddr
      Ready,        // ready & waiting for go flag
      FetchingArgs, // fetching arguments
      Running,      // running & doing the work
      Done          // writing to done flag & waiting to transit to Ready
    };

    struct Args {
      Addr inp_tensor_addr;
      Addr out_tensor_addr;
      uint64_t dim_0;
      uint64_t dim_1;
      uint64_t dim_2;
      uint64_t lower_x_idx; // inclusive
      uint64_t upper_x_idx; // exclusive
      uint64_t lower_z_idx; // inclusive
      uint64_t upper_z_idx; // exclusive
    };

    struct SenderState : public Packet::SenderState
    {
      int stream_idx;
      SenderState(int _stream_idx)
        : stream_idx(_stream_idx)
      { }
    };

    struct Stream {
      bool     is_reading;
      bool     is_writing;
      float    partial_sum;
      uint64_t x_idx;
      uint64_t y_idx;
      uint64_t z_idx;

      Stream()
        : is_reading(false),
          is_writing(false),
          partial_sum(0.0),
          x_idx(0),
          y_idx(0),
          z_idx(0)
      { }
    };

    // current FSM state
    State m_cur_state;

    // Base vaddr of SP for this xcel
    Addr m_spm_base_vaddr;

    // Pointer to CPU process so that we can do address translation
    Process* m_cpu_process_p;

    // Xcel input/output arguments
    Args m_args;

    // Number of streaming lanes
    const int m_num_streams;

    // Current streaming ID
    int m_cur_stream_idx;

    // List of all streams
    std::vector<Stream> m_streams;

    // Total number of reads/writes (total of amount of work to be done).
    // This will tell when the xcel finishes
    size_t m_total_num_reads;
    size_t m_total_num_writes;

    // Number of ops that have finished
    size_t m_cur_num_reads;
    size_t m_cur_num_writes;

    // function doing the actual computation
    void doWork();
};

#endif // TENSOR_SUM_XCEL_HH
