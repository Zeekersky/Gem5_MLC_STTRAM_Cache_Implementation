//=============================================================================
// embedding_bw_xcel.hh
//=============================================================================
//
// Author: Tuan Ta
// Date  : 19/07/17

#ifndef __EMBEDDING_BW_XCEL_HH__
#define __EMBEDDING_BW_XCEL_HH__

#include "accelerators/memory_mapped_xcel.hh"
#include "params/EmbeddingBwXcel.hh"
#include "sim/process.hh"

class EmbeddingBwXcel : public MemoryMappedXcel {
  public:
    typedef EmbeddingBwXcelParams Params;
    EmbeddingBwXcel(const Params* p);
    ~EmbeddingBwXcel() = default;

    void tick() override;
    bool processMemResp(Packet* pkt_p) override;
    void retry() override;
    virtual void regStats();

  private:
    /**
     * FSM states
     */
    enum State {
      Idle,           // waiting to read base_spm_vaddr
      Ready,          // ready & waiting for go flag
      FetchingArgs,   // fetching arguments
      Running,        // running & doing the work
      Done            // writing to done flag & waiting to transit to Ready
    };

    struct Args {
      Addr grad_weight_tensor_addr;
      Addr grad_tensor_addr;
      Addr index_arr_addr;
      uint64_t dim_0;           // dim_0 of grad_weight
      uint64_t dim_1;           // dim_1 of grad_weight and grad
      uint64_t numel;           // size of index_arr
      uint64_t lower_x_idx;     // inclusive
      uint64_t upper_x_idx;     // exclusive
    };

    struct SenderState : public Packet::SenderState
    {
      int stream_idx;
      Cycles issue_cycle;
      SenderState(int _stream_idx, Cycles _cycle)
        : stream_idx(_stream_idx),
          issue_cycle(_cycle)
      { }
    };

    enum StreamState {
      ReadingIdxVal,
      ReadingGrad,
      ReadingGradWeight,
      WritingGradWeight,
      ReadIdxValNext,
      ReadGradNext,
      ReadGradWeightNext,
      WriteGradWeightNext
    };

    struct Stream {
      StreamState state;
      uint64_t    cur_idx;
      uint64_t    cur_idx_val;
      uint64_t    y_idx;
      float       grad_weight;
      float       grad_val;
      uint64_t    lower_y_idx;  // inclusive
      uint64_t    upper_y_idx;  // exclusive

      Stream()
        : state(ReadIdxValNext),
          cur_idx(0), cur_idx_val(0), y_idx(0),
          grad_weight(0.0), grad_val(0.0),
          lower_y_idx(0), upper_y_idx(0)
      { }

      bool isDone(size_t numel) const
      { return cur_idx == numel; }
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

    // True if the xcel is reading idx value
    bool m_is_reading_idx;

    // function doing the actual computation
    void doWork();

    Stats::Scalar read_latency;
    Stats::Scalar write_latency;
    Stats::Scalar read_count;
    Stats::Scalar write_count;
    Stats::Formula avg_read_latency;
    Stats::Formula avg_write_latency;
};

#endif // EMBEDDING_BW_XCEL_HH
