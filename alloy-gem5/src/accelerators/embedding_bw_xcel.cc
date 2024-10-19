//=============================================================================
// embedding_bw_xcel.cc
//=============================================================================

#include "accelerators/embedding_bw_xcel.hh"

#include "debug/Xcel.hh"
#include "mem/page_table.hh"
#include "mem/ruby/scratchpad/Scratchpad.hh"

EmbeddingBwXcel::EmbeddingBwXcel(const Params* p)
  : MemoryMappedXcel(p),
    m_cur_state(Idle),
    m_spm_base_vaddr(0),
    m_cpu_process_p(p->cpu_process),
    m_args{0, 0, 0, 0, 0, 0, 0, 0 },
    m_num_streams(p->stream_width),
    m_cur_stream_idx(0),
    m_streams(m_num_streams, Stream()),
    m_is_reading_idx(false)
{
  scheduleNextTick();
}

void
EmbeddingBwXcel::tick()
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

        bool done = true;
        for (auto& s : m_streams) {
          if (!s.isDone(m_args.numel)) {
            done = false;
            break;
          }
        }

        if (done) {
          m_cur_state = State::Done;
        } else if (!m_is_reading_idx){
          // check if all streams need to read the next idx val
          bool read_idx_val = true;
          for (auto& s : m_streams) {
            if (s.state != ReadIdxValNext) {
              read_idx_val = false;
              break;
            }
          }

          if (read_idx_val) {
            // sanity check: make sure all streams are on the same idx
            for (size_t i = 1; i < m_num_streams; ++i)
              assert(m_streams[0].cur_idx == m_streams[i].cur_idx);

            // first stream will fetch idx_val on behalf of all streams
            Addr offset = m_streams[0].cur_idx * sizeof(uint64_t);
            Addr vaddr = m_args.index_arr_addr + offset;
            Addr paddr = 0;

            assert(m_cpu_process_p->pTable->translate(vaddr, paddr));
            assert(paddr != 0);

            RequestPtr req = std::make_shared<Request>(paddr,
                                                       sizeof(uint64_t), 0, 0);
            Packet* pkt = new Packet(req, MemCmd::ReadReq);
            pkt->dataDynamic(new uint8_t[sizeof(uint64_t)]);
            pkt->pushSenderState(new EmbeddingBwXcel::SenderState(0,
                                                                  curCycle()));

            // send the request
            if (!m_mem_port_p->sendTimingReq(pkt)) {
              scheduleNextTick();
              delete pkt->popSenderState();
              delete pkt;
            } else {
              DPRINTF(Xcel, "Xcel-stream 0 is reading idx val at idx = %d\n",
                            m_streams[0].cur_idx);

              // change state to ReadingIdxVal
              for (auto& s : m_streams)
                s.state = StreamState::ReadingIdxVal;

              m_is_reading_idx = true;
            }
          } else {
            doWork();
          }
        }

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
EmbeddingBwXcel::processMemResp(Packet* pkt_p)
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
        m_args.grad_weight_tensor_addr = data_p->grad_weight_tensor_addr;
        m_args.grad_tensor_addr         = data_p->grad_tensor_addr;
        m_args.index_arr_addr           = data_p->index_arr_addr;
        m_args.dim_0                    = data_p->dim_0;
        m_args.dim_1                    = data_p->dim_1;
        m_args.numel                    = data_p->numel;
        m_args.lower_x_idx              = data_p->lower_x_idx;
        m_args.upper_x_idx              = data_p->upper_x_idx;

        DPRINTF(Xcel, "args lower_x_idx %d upper_x_idx %d\n",
                  m_args.lower_x_idx, m_args.upper_x_idx);
        DPRINTF(Xcel, "args dim_0 %d dim_1 %d\n",
                  m_args.dim_0, m_args.dim_1);

        // init all streams
        size_t y_chunk_size = m_args.dim_1 / m_num_streams;
        for (size_t i = 0; i < m_num_streams; ++i) {
          m_streams[i].state        = StreamState::ReadIdxValNext;
          m_streams[i].cur_idx      = 0;
          m_streams[i].lower_y_idx  = i * y_chunk_size;
          m_streams[i].upper_y_idx  = (i == m_num_streams - 1) ?
                                        m_args.dim_1 : (i + 1) * y_chunk_size;
          m_streams[i].y_idx        = m_streams[i].lower_y_idx;
        }

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
        EmbeddingBwXcel::SenderState* ss =
            safe_cast<EmbeddingBwXcel::SenderState*>(pkt_p->popSenderState());

        // sanity check
        assert(ss);
        assert(ss->stream_idx < m_num_streams);

        // retrieve the stream waiting for this response
        Stream& stream = m_streams[ss->stream_idx];

        // update stats
        if (pkt_p->cmd == MemCmd::ReadResp) {
          read_count++;
          read_latency += (curCycle() - ss->issue_cycle);
        } else if (pkt_p->cmd == MemCmd::WriteResp) {
          write_count++;
          write_latency += (curCycle() - ss->issue_cycle);
        }

        if (stream.state == StreamState::ReadingIdxVal) {
          assert(pkt_p->cmd == MemCmd::ReadResp);
          assert(m_is_reading_idx);
          assert(ss->stream_idx == 0);

          // broadcast idx_val to all streams
          for (auto& s : m_streams) {
            s.cur_idx_val = *(pkt_p->getPtr<uint64_t>());
            assert(s.cur_idx_val < m_args.dim_0);

            // check if idx_val belongs to this xcel
            if (m_args.lower_x_idx <= s.cur_idx_val &&
                s.cur_idx_val < m_args.upper_x_idx) {
              s.y_idx = s.lower_y_idx;
              s.state = StreamState::ReadGradNext;
            } else {
              // read next idx
              s.cur_idx++;
              s.state = StreamState::ReadIdxValNext;
            }
          }

          m_is_reading_idx = false;
          scheduleNextTick();
        } else if (stream.state == StreamState::ReadingGrad) {
          assert(pkt_p->cmd == MemCmd::ReadResp);

          // read grad
          stream.grad_val = *(pkt_p->getPtr<float>());

          // read grad_weight
          stream.state = StreamState::ReadGradWeightNext;
          scheduleNextTick();
        } else if (stream.state == StreamState::ReadingGradWeight) {
          assert(pkt_p->cmd == MemCmd::ReadResp);

          // read grad_weight
          stream.grad_weight = *(pkt_p->getPtr<float>());

          // add grad_val to grad_weight
          stream.grad_weight += stream.grad_val;

          // write back grad_weight next
          stream.state = StreamState::WriteGradWeightNext;
          scheduleNextTick();
        } else if (stream.state == StreamState::WritingGradWeight) {
          assert(pkt_p->cmd == MemCmd::WriteResp);

          // increment y_idx
          stream.y_idx++;

          // read grad next
          stream.state = StreamState::ReadGradNext;
          scheduleNextTick();
        } else {
          panic("Xcel received invalid response pkt\n");
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
EmbeddingBwXcel::retry()
{
  //panic( "Xcel is not supporting retry yet\n");
  warn( "Xcel received a retry\n");
}

void
EmbeddingBwXcel::doWork()
{
  // get the current stream
  Stream& cur_stream = m_streams[m_cur_stream_idx];

  // sanity check
  assert(cur_stream.cur_idx <= m_args.numel);
  assert(cur_stream.y_idx <= cur_stream.upper_y_idx);
  assert(cur_stream.y_idx >= cur_stream.lower_y_idx);

  /**
   * Out-of-bound check for cur_idx
   */
  if (cur_stream.cur_idx == m_args.numel) {
    // move to the next stream
    m_cur_stream_idx = (m_cur_stream_idx + 1) % m_num_streams;
    return;
  }

  if (cur_stream.state == StreamState::ReadingIdxVal ||
      cur_stream.state == StreamState::ReadingGrad ||
      cur_stream.state == StreamState::ReadingGradWeight ||
      cur_stream.state == StreamState::WritingGradWeight) {
    // move to the next stream
    m_cur_stream_idx = (m_cur_stream_idx + 1) % m_num_streams;
    return;
  }

  /**
   * Out-of-bound check for y_idx
   */
  if (cur_stream.y_idx == cur_stream.upper_y_idx) {
    cur_stream.y_idx = cur_stream.lower_y_idx;
    cur_stream.cur_idx++;
    cur_stream.state = StreamState::ReadIdxValNext;

    if (cur_stream.cur_idx == m_args.numel) {
      // move to the next stream
      m_cur_stream_idx = (m_cur_stream_idx + 1) % m_num_streams;
      return;
    }
  }

  /**
   * send a ReadReq to fetch cur_idx_val
   */
  if (cur_stream.state == StreamState::ReadIdxValNext) {
    // move to the next stream. Outer loop will fetch idx_val on behalf of all
    // streams
    m_cur_stream_idx = (m_cur_stream_idx + 1) % m_num_streams;
    return;
  }
  /**
   * send a ReadReq to fetch grad[cur_idx][y_idx]
   */
  else if (cur_stream.state == StreamState::ReadGradNext) {
    Addr offset = cur_stream.cur_idx * m_args.dim_1 + cur_stream.y_idx;
    Addr vaddr = m_args.grad_tensor_addr + offset * sizeof(float);
    Addr paddr = 0;

    assert(m_cpu_process_p->pTable->translate(vaddr, paddr));
    assert(paddr != 0);

    RequestPtr req = std::make_shared<Request>(paddr, sizeof(float), 0, 0);
    Packet* pkt = new Packet(req, MemCmd::ReadReq);
    pkt->dataDynamic(new uint8_t[sizeof(float)]);
    pkt->pushSenderState(new EmbeddingBwXcel::SenderState(m_cur_stream_idx,
                                                          curCycle()));

    // send the request
    if (!m_mem_port_p->sendTimingReq(pkt)) {
      scheduleNextTick();
      delete pkt->popSenderState();
      delete pkt;
    } else {
      DPRINTF(Xcel, "Xcel-stream %d is reading grad val at [%d, %d]\n",
                  m_cur_stream_idx, cur_stream.cur_idx, cur_stream.y_idx);

      // change state to ReadingIdxVal
      cur_stream.state = StreamState::ReadingGrad;

      // process the next stream in the next cycle
      m_cur_stream_idx = (m_cur_stream_idx + 1) % m_num_streams;
    }
  }
  /**
   * send a ReadReq to fetch grad_weight[cur_idx_val][y_idx]
   */
  else if (cur_stream.state == StreamState::ReadGradWeightNext) {
    Addr offset = cur_stream.cur_idx_val * m_args.dim_1 + cur_stream.y_idx;
    Addr vaddr = m_args.grad_weight_tensor_addr + offset * sizeof(float);
    Addr paddr = 0;

    assert(m_cpu_process_p->pTable->translate(vaddr, paddr));
    assert(paddr != 0);

    RequestPtr req = std::make_shared<Request>(paddr, sizeof(float), 0, 0);
    Packet* pkt = new Packet(req, MemCmd::ReadReq);
    pkt->dataDynamic(new uint8_t[sizeof(float)]);
    pkt->pushSenderState(new EmbeddingBwXcel::SenderState(m_cur_stream_idx,
                                                          curCycle()));

    // send the request
    if (!m_mem_port_p->sendTimingReq(pkt)) {
      scheduleNextTick();
      delete pkt->popSenderState();
      delete pkt;
    } else {
      DPRINTF(Xcel, "Xcel-stream %d is reading grad_weight at [%d, %d]\n",
                  m_cur_stream_idx, cur_stream.cur_idx_val, cur_stream.y_idx);

      // change state to ReadingIdxVal
      cur_stream.state = StreamState::ReadingGradWeight;

      // process the next stream in the next cycle
      m_cur_stream_idx = (m_cur_stream_idx + 1) % m_num_streams;
    }
  }
  /**
   * send a WriteReq to write back grad weight[cur_idx_val][y_idx]
   */
  else if (cur_stream.state == StreamState::WriteGradWeightNext) {
    Addr offset = cur_stream.cur_idx_val * m_args.dim_1 + cur_stream.y_idx;
    Addr vaddr = m_args.grad_weight_tensor_addr + offset * sizeof(float);
    Addr paddr = 0;

    assert(m_cpu_process_p->pTable->translate(vaddr, paddr));
    assert(paddr != 0);

    RequestPtr req = std::make_shared<Request>(paddr, sizeof(float), 0, 0);
    Packet* pkt = new Packet(req, MemCmd::WriteReq);
    pkt->dataDynamic(new uint8_t[sizeof(float)]);
    pkt->setData((const uint8_t*)(&(cur_stream.grad_weight)));
    pkt->pushSenderState(new EmbeddingBwXcel::SenderState(m_cur_stream_idx,
                                                          curCycle()));

    // send the request
    if (!m_mem_port_p->sendTimingReq(pkt)) {
      scheduleNextTick();
      delete pkt->popSenderState();
      delete pkt;
    } else {
      DPRINTF(Xcel, "Xcel-stream %d is writing grad_weight at [%d, %d]\n",
                  m_cur_stream_idx, cur_stream.cur_idx_val, cur_stream.y_idx);

      // change state to ReadingIdxVal
      cur_stream.state = StreamState::WritingGradWeight;

      // process the next stream in the next cycle
      m_cur_stream_idx = (m_cur_stream_idx + 1) % m_num_streams;
    }
  } else {
    panic("Wrong stream state. Stream = %d\n", m_cur_stream_idx);
  }
}

void
EmbeddingBwXcel::regStats()
{
  MemObject::regStats();

  read_latency.name(name() + ".read_latency")
              .desc("Total read latency in cycles");

  write_latency.name(name() + ".write_latency")
              .desc("Total write latency in cycles");

  read_count.name(name() + ".num_reads")
            .desc("Total number of reads");
  write_count.name(name() + ".num_writes")
              .desc("Total number of writes");

  avg_read_latency.name(name() + ".avg_read_latency")
                  .flags(Stats::oneline);
  avg_read_latency = read_latency / read_count;

  avg_write_latency.name(name() + ".avg_write_latency")
                  .flags(Stats::oneline);
  avg_write_latency = write_latency / write_count;
}

EmbeddingBwXcel*
EmbeddingBwXcelParams::create()
{
  return new EmbeddingBwXcel(this);
}
