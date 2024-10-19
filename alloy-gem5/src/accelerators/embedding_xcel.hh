//=============================================================================
// embedding_xcel.hh
//=============================================================================
//
// Author: Tuan Ta
// Date  : 19/07/17

#ifndef __EMBEDDING_XCEL_HH__
#define __EMBEDDING_XCEL_HH__

#include "accelerators/memory_mapped_xcel.hh"
#include "params/EmbeddingXcel.hh"
#include "sim/process.hh"

class EmbeddingXcel : public MemoryMappedXcel {
  public:
    typedef EmbeddingXcelParams Params;
    EmbeddingXcel(const Params* p);
    ~EmbeddingXcel() = default;

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
      Addr index_arr_addr;
      Addr weight_tensor_addr;
      Addr output_tensor_addr;
      uint64_t weight_dim_0;
      uint64_t weight_dim_1;
      uint64_t numel;
      uint64_t lower_idx;       // inclusive
      uint64_t upper_idx;       // exclusive
    };

    struct SenderState : public Packet::SenderState
    {
      int stream_idx;
      SenderState(int _stream_idx)
        : stream_idx(_stream_idx)
      { }
    };

    enum StreamState {
      ReadingIdxVal,    // reading index value
      Reading,          // reading weight value
      Writing,          // writing current weight value to output tensor
      ReadNext,         // to read next weight value
      WriteNext,        // to write current weight value to output tensor
      Invalid           // invalid
    };

    struct Stream {
      StreamState state;
      size_t      y_idx;
      size_t      cur_idx;
      size_t      cur_idx_val;
      float       weight_val;

      Stream()
        : state(Invalid), y_idx(0), cur_idx(0), cur_idx_val(0), weight_val(0.0)
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

#endif // EMBEDDING_XCEL_HH
