//=============================================================================
// tensor_sum_xcel.cc
//=============================================================================

#include "accelerators/embedding_xcel.hh"

#include "debug/Xcel.hh"
#include "mem/page_table.hh"
#include "mem/ruby/scratchpad/Scratchpad.hh"

EmbeddingXcel::EmbeddingXcel(const Params* p)
  : MemoryMappedXcel(p),
    m_cur_state(Idle),
    m_spm_base_vaddr(0),
    m_cpu_process_p(p->cpu_process),
    m_args{0, 0, 0, 0, 0, 0, 0, 0 },
    m_num_streams(p->stream_width),
    m_cur_stream_idx(0),
    m_streams(m_num_streams, Stream()),
    m_total_num_reads(0),
    m_total_num_writes(0),
    m_cur_num_reads(0),
    m_cur_num_writes(0)
{
  scheduleNextTick();
}

void
EmbeddingXcel::tick()
{
  switch (m_cur_state) {
    /**
     * Idle state
     */
    case State::Idle:
      {
        DPRINTF(Xcel, "Xcel is reading SPM base addr\n");

        // send a request to read spm_base_vaddr
        RequestPtr req = std::make_shared<Request>(SPM_BASE_ADDR_OFFSET,
                                                   sizeof(uint64_t), 0, 0);
        Packet* pkt = new Packet(req, MemCmd::SPMReadReq);
        pkt->dataDynamic(new uint8_t[sizeof(uint64_t)]);

        if (!m_mem_port_p->sendTimingReq(pkt)) {
          scheduleNextTick();
          delete pkt;
        }
      }
      break;

    /**
     * Ready state
     */
    case State::Ready:
      {
        assert(m_spm_base_vaddr != 0);

        DPRINTF(Xcel, "Xcel is reading go flag\n");

        // send a request to read go flag
        RequestPtr req = std::make_shared<Request>(SPM_GO_FLAG_OFFSET,
                                                   sizeof(uint32_t), 0, 0);
        Packet* pkt = new Packet(req, MemCmd::SPMReadReq);
        pkt->dataDynamic(new uint8_t[sizeof(uint32_t)]);

        if (!m_mem_port_p->sendTimingReq(pkt)) {
          scheduleNextTick();
          delete pkt;
        }
      }
      break;

    /**
     * Fetching arguments
     */
    case State::FetchingArgs:
      {
        assert(m_spm_base_vaddr != 0);

        // get paddr of this request
        Addr vaddr = m_spm_base_vaddr + SPM_ARGS_OFFSET;
        Addr paddr = 0;
        assert(m_cpu_process_p->pTable->translate(vaddr, paddr));
        assert(paddr != 0);

        DPRINTF(Xcel, "Xcel is fetching arguments at vaddr 0x%x paddr 0x%x\n",
                      vaddr, paddr);

        RequestPtr req = std::make_shared<Request>(paddr, sizeof(Args), 0, 0);
        Packet* pkt = new Packet(req, MemCmd::ReadReq);
        pkt->dataDynamic(new uint8_t[sizeof(Args)]);

        if (!m_mem_port_p->sendTimingReq(pkt)) {
          scheduleNextTick();
          delete pkt;
        }
      }
      break;

    /**
     * Running state
     */
    case State::Running:
      {
        assert(m_spm_base_vaddr != 0);

        DPRINTF(Xcel, "m_cur_num_reads = %d total %d\n",
                      m_cur_num_reads, m_total_num_reads);
        DPRINTF(Xcel, "m_cur_num_writes = %d total %d\n",
                      m_cur_num_writes, m_total_num_writes);

        if (m_cur_num_reads == m_total_num_reads &&
            m_cur_num_writes == m_total_num_writes)
          m_cur_state = State::Done;
        else
          doWork();

        // schedule the next tick to do work until the work is done
        scheduleNextTick();
      }
      break;

    /**
     * Done state
     */
    case State::Done:
      {
        DPRINTF(Xcel, "Xcel is done\n");

        assert(m_spm_base_vaddr != 0);

        // send a request to write done flag
        RequestPtr req = std::make_shared<Request>(SPM_DONE_FLAG_OFFSET,
                                                   sizeof(uint32_t), 0, 0);
        Packet* pkt = new Packet(req, MemCmd::SPMWriteReq);
        pkt->dataDynamic(new uint8_t[sizeof(uint32_t)]);
        *(pkt->getPtr<uint32_t>()) = 1;

        if (!m_mem_port_p->sendTimingReq(pkt)) {
          scheduleNextTick();
          delete pkt;
        }
      }
      break;

    /**
     * Default (invalid)
     */
    default:
      panic("Invalid xcel state\n");
  }
}

bool
EmbeddingXcel::processMemResp(Packet* pkt_p)
{
  assert(pkt_p);

  DPRINTF(Xcel, "Xcel received pkt %s\n", pkt_p->print());

  switch (m_cur_state) {
    /**
     * Idle state
     */
    case State::Idle:
      {
        assert(pkt_p->cmd == MemCmd::SPMReadResp);
        m_spm_base_vaddr = (*pkt_p->getPtr<uint64_t>());
        assert(m_spm_base_vaddr != 0);
        m_cur_state = State::Ready;
        scheduleNextTick();
      }
      break;

    /**
     * Ready state
     */
    case State::Ready:
      {
        assert(pkt_p->cmd == MemCmd::SPMReadResp);
        uint32_t* go_p = pkt_p->getPtr<uint32_t>();
        assert(*go_p == 1);
        m_cur_state = State::FetchingArgs;
        scheduleNextTick();
      }
      break;

    /**
     * Fetching Args
     */
    case State::FetchingArgs:
      {
        assert(pkt_p->cmd == MemCmd::ReadResp);
        Args* data_p = pkt_p->getPtr<Args>();

        // extract data fields
        m_args.index_arr_addr     = data_p->index_arr_addr;
        m_args.weight_tensor_addr = data_p->weight_tensor_addr;
        m_args.output_tensor_addr = data_p->output_tensor_addr;
        m_args.weight_dim_0       = data_p->weight_dim_0;
        m_args.weight_dim_1       = data_p->weight_dim_1;
        m_args.numel              = data_p->numel;
        m_args.lower_idx          = data_p->lower_idx;
        m_args.upper_idx          = data_p->upper_idx;

        assert(m_args.lower_idx <= m_args.numel);
        assert(m_args.upper_idx <= m_args.numel);
        assert(m_args.weight_dim_1 >= m_num_streams);

        // initializing streams
        for (size_t i = 0; i < m_num_streams; ++i) {
          m_streams[i].state    = Invalid;
          m_streams[i].y_idx    = i;
          m_streams[i].cur_idx  = m_args.lower_idx;
        }

        // initialize the total number of additions to be done
        m_total_num_reads  = (m_args.upper_idx - m_args.lower_idx) *
                              m_args.weight_dim_1;
        m_total_num_writes = m_total_num_reads;
        m_cur_num_reads = 0;
        m_cur_num_writes = 0;

        // transit to Running state
        m_cur_state = State::Running;
        scheduleNextTick();
      }
      break;

    /**
     * Running state
     */
    case State::Running:
      {
        EmbeddingXcel::SenderState* ss =
              safe_cast<EmbeddingXcel::SenderState*>(pkt_p->popSenderState());

        // sanity check
        assert(ss);
        assert(ss->stream_idx < m_num_streams);

        // retrieve the stream waiting for this response
        Stream& stream = m_streams[ss->stream_idx];

        if (stream.state == StreamState::ReadingIdxVal) {
          assert(pkt_p->cmd == MemCmd::ReadResp);

          // read idx_val
          stream.cur_idx_val = *(pkt_p->getPtr<uint64_t>());
          assert(stream.cur_idx_val < m_args.weight_dim_0);

          // reset y_idx
          stream.y_idx = ss->stream_idx;

          // change to ReadNext state
          stream.state = StreamState::ReadNext;
          scheduleNextTick();
        } else if (stream.state == StreamState::Reading) {
          assert(pkt_p->cmd == MemCmd::ReadResp);

          // read weight_val
          stream.weight_val = *(pkt_p->getPtr<float>());

          // change to WriteNext state
          stream.state = StreamState::WriteNext;
          scheduleNextTick();

          // one more read completed
          m_cur_num_reads++;
        } else if (stream.state == StreamState::Writing) {
          assert(pkt_p->cmd == MemCmd::WriteResp);

          // increment y_idx
          stream.y_idx += m_num_streams;

          if (stream.y_idx > m_args.weight_dim_1)
            stream.y_idx = m_args.weight_dim_1;

          // change to ReadNext state
          stream.state = StreamState::ReadNext;
          scheduleNextTick();

          // one more write completed
          m_cur_num_writes++;
        } else {
          panic("Stream %d is not waiting for any response", ss->stream_idx);
        }

        // delete sender state
        delete ss;
      }
      break;

    /**
     * Done state
     */
    case State::Done:
      {
        // For now, just terminate the xcel
        assert(pkt_p->cmd == MemCmd::SPMWriteResp);
        m_cur_state = State::Idle;
      }
      break;

    default:
      panic("Invalid xcel state\n");
  }

  delete pkt_p;
  return true;
}

void
EmbeddingXcel::retry()
{
  //panic( "Xcel is not supporting retry yet\n");
  warn( "Xcel received a retry\n");
}

void
EmbeddingXcel::doWork()
{
  // get the current stream
  Stream& cur_stream = m_streams[m_cur_stream_idx];

  // sanity check
  assert(cur_stream.y_idx <= m_args.weight_dim_1);
  assert(cur_stream.cur_idx <= m_args.upper_idx);
  assert(cur_stream.cur_idx >= m_args.lower_idx);

  /**
   * Out of bound check for cur_idx
   */
  if (cur_stream.cur_idx == m_args.upper_idx) {
    // move to next stream that may still have work to do
    m_cur_stream_idx = (m_cur_stream_idx + 1) % m_num_streams;
    return;
  }

  if (cur_stream.state == StreamState::ReadingIdxVal ||
      cur_stream.state == StreamState::Reading ||
      cur_stream.state == StreamState::Writing) {
    // we'll come back this stream later. We decide not to move to the next
    // stream so that all streams can somewhat be in sync
    return;
  }

  /**
   * Out of bound check for y_idx
   */
  if (cur_stream.state == Invalid ||
      cur_stream.y_idx == m_args.weight_dim_1) {
    // increment cur_idx
    if (cur_stream.state != Invalid)
      cur_stream.cur_idx++;

    if (cur_stream.cur_idx == m_args.upper_idx) {
      // move to next stream that may still have work to do
      m_cur_stream_idx = (m_cur_stream_idx + 1) % m_num_streams;
      return;
    }

    // issue a read request to get idx_val
    Addr offset = cur_stream.cur_idx * sizeof(uint64_t);
    Addr vaddr = m_args.index_arr_addr + offset;
    Addr paddr = 0;
    assert(m_cpu_process_p->pTable->translate(vaddr, paddr));
    assert(paddr != 0);

    RequestPtr req = std::make_shared<Request>(paddr, sizeof(uint64_t), 0, 0);
    Packet* pkt = new Packet(req, MemCmd::ReadReq);
    pkt->dataDynamic(new uint8_t[sizeof(uint64_t)]);
    pkt->pushSenderState(new EmbeddingXcel::SenderState(m_cur_stream_idx));

    // send the request
    if (!m_mem_port_p->sendTimingReq(pkt)) {
      scheduleNextTick();
      delete pkt->popSenderState();
      delete pkt;
    } else {
      DPRINTF(Xcel, "Xcel-stream %d is reading idx val at idx = %d\n",
                  m_cur_stream_idx, cur_stream.cur_idx);

      // change state to ReadingIdxVal
      cur_stream.state = StreamState::ReadingIdxVal;

      // process the next stream in the next cycle
      m_cur_stream_idx = (m_cur_stream_idx + 1) % m_num_streams;
    }
  }
  /**
   * Issue a request to read weight value
   */
  else if (cur_stream.state == StreamState::ReadNext) {
    Addr offset = cur_stream.cur_idx_val * m_args.weight_dim_1 +
                        cur_stream.y_idx;
    Addr vaddr = m_args.weight_tensor_addr + offset * sizeof(float);
    Addr paddr = 0;
    assert(m_cpu_process_p->pTable->translate(vaddr, paddr));
    assert(paddr != 0);

    RequestPtr req = std::make_shared<Request>(paddr, sizeof(float), 0, 0);
    Packet* pkt = new Packet(req, MemCmd::ReadReq);
    pkt->dataDynamic(new uint8_t[sizeof(float)]);
    pkt->pushSenderState(new EmbeddingXcel::SenderState(m_cur_stream_idx));

    // send the request
    if (!m_mem_port_p->sendTimingReq(pkt)) {
      scheduleNextTick();
      delete pkt->popSenderState();
      delete pkt;
    } else {
      DPRINTF(Xcel, "Xcel-stream %d is reading weight [%d, %d]\n",
                  m_cur_stream_idx, cur_stream.cur_idx_val, cur_stream.y_idx);

      // change state to Reading
      cur_stream.state = StreamState::Reading;

      // process the next stream in the next cycle
      m_cur_stream_idx = (m_cur_stream_idx + 1) % m_num_streams;
    }
  }
  /**
   * Issue a request to write back weight value
   */
  else if (cur_stream.state == StreamState::WriteNext) {
    Addr offset = cur_stream.cur_idx * m_args.weight_dim_1 + cur_stream.y_idx;
    Addr vaddr = m_args.output_tensor_addr + offset * sizeof(float);
    Addr paddr = 0;
    assert(m_cpu_process_p->pTable->translate(vaddr, paddr));
    assert(paddr != 0);

    RequestPtr req = std::make_shared<Request>(paddr, sizeof(float), 0, 0);
    Packet* pkt = new Packet(req, MemCmd::WriteReq);
    pkt->dataDynamic(new uint8_t[sizeof(float)]);
    pkt->setData((const uint8_t*)(&(cur_stream.weight_val)));
    pkt->pushSenderState(new EmbeddingXcel::SenderState(m_cur_stream_idx));

    // send the request
    if (!m_mem_port_p->sendTimingReq(pkt)) {
      scheduleNextTick();
      delete pkt->popSenderState();
      delete pkt;
    } else {
      DPRINTF(Xcel, "Xcel-stream %d is writing to output[%d, %d]\n",
                  m_cur_stream_idx, cur_stream.cur_idx, cur_stream.y_idx);

      // change state to Writing
      cur_stream.state = StreamState::Writing;

      // process the next stream in the next cycle
      m_cur_stream_idx = (m_cur_stream_idx + 1) % m_num_streams;
    }
  } else {
    panic("Invalid xcel state. Stream = %d\n", m_cur_stream_idx);
  }
}

EmbeddingXcel*
EmbeddingXcelParams::create()
{
  return new EmbeddingXcel(this);
}
