//=============================================================================
// tensor_sum_xcel.cc
//=============================================================================

#include "accelerators/tensor_sum_xcel.hh"

#include "debug/Xcel.hh"
#include "mem/page_table.hh"
#include "mem/ruby/scratchpad/Scratchpad.hh"

TensorSumXcel::TensorSumXcel(const Params* p)
  : MemoryMappedXcel(p),
    m_cur_state(Idle),
    m_spm_base_vaddr(0),
    m_cpu_process_p(p->cpu_process),
    m_args{0, 0, 0, 0, 0, 0, 0, 0, 0},
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
TensorSumXcel::tick()
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
TensorSumXcel::processMemResp(Packet* pkt_p)
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
        m_args.inp_tensor_addr = data_p->inp_tensor_addr;
        m_args.out_tensor_addr = data_p->out_tensor_addr;
        m_args.dim_0           = data_p->dim_0;
        m_args.dim_1           = data_p->dim_1;
        m_args.dim_2           = data_p->dim_2;
        m_args.lower_x_idx     = data_p->lower_x_idx;
        m_args.upper_x_idx     = data_p->upper_x_idx;
        m_args.lower_z_idx     = data_p->lower_z_idx;
        m_args.upper_z_idx     = data_p->upper_z_idx;

        assert(m_args.lower_x_idx < m_args.upper_x_idx);
        assert(m_args.lower_z_idx < m_args.upper_z_idx);

        // initializing streams
        for (size_t i = 0; i < m_num_streams; ++i) {
          m_streams[i].x_idx = m_args.lower_x_idx;

          if (m_args.lower_z_idx + i < m_args.upper_z_idx)
            m_streams[i].z_idx = m_args.lower_z_idx + i;
          else
            m_streams[i].z_idx = m_args.upper_z_idx;
        }

        // initialize the total number of additions to be done
        m_total_num_reads  = (m_args.upper_x_idx - m_args.lower_x_idx) *
                             m_args.dim_1 *
                             (m_args.upper_z_idx - m_args.lower_z_idx);
        m_total_num_writes = (m_args.upper_x_idx - m_args.lower_x_idx) *
                             (m_args.upper_z_idx - m_args.lower_z_idx);
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
        TensorSumXcel::SenderState* ss =
              safe_cast<TensorSumXcel::SenderState*>(pkt_p->popSenderState());

        // sanity check
        assert(ss);
        assert(ss->stream_idx < m_num_streams);

        // retrieve the stream waiting for this response
        Stream& stream = m_streams[ss->stream_idx];

        if (pkt_p->cmd == MemCmd::WriteResp) {
          assert(stream.is_writing && !stream.is_reading);
          // reset flags
          stream.partial_sum = 0.0;
          stream.is_writing = false;
          // one more write completed
          m_cur_num_writes++;
        } else if (pkt_p->cmd == MemCmd::ReadResp) {
          assert(!stream.is_writing && stream.is_reading);
          // extract data
          float* data_p = pkt_p->getPtr<float>();
          stream.partial_sum += *data_p;
          // reset flags
          stream.is_reading = false;
          // one more read completed
          m_cur_num_reads++;
        } else {
          panic( "Xcel is not expecting this packet %s\n", pkt_p->print());
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
TensorSumXcel::retry()
{
  //panic( "Xcel is not supporting retry yet\n");
  warn( "Xcel received a retry\n");
}

void
TensorSumXcel::doWork()
{
  Stream& cur_stream = m_streams[m_cur_stream_idx];

  // sanity check
  assert(cur_stream.x_idx <= m_args.upper_x_idx);
  assert(m_args.lower_x_idx <= cur_stream.x_idx);
  assert(cur_stream.y_idx <= m_args.dim_1);
  assert(cur_stream.z_idx <= m_args.upper_z_idx);
  assert(m_args.lower_z_idx <= cur_stream.z_idx);

  /**
   * out-of-bound check for z-dimension
   */
  if (cur_stream.z_idx == m_args.upper_z_idx) {
    m_cur_stream_idx = 0;
    return;
  }

  // check if the cur_stream is waiting for a memory response
  if (cur_stream.is_reading || cur_stream.is_writing) {
    // we'll come back this stream later. We decide not to move to the next
    // stream so that all streams can somewhat be in sync
    return;
  }

  /**
   * out-of-bound check for y-dimension
   */
  if (cur_stream.y_idx == m_args.dim_1) {
    // make a write request to write back the partial sum
    Addr offset = (cur_stream.x_idx * m_args.dim_2 + cur_stream.z_idx) *
                                                                sizeof(float);
    Addr vaddr = m_args.out_tensor_addr + offset;
    Addr paddr = 0;
    assert(m_cpu_process_p->pTable->translate(vaddr, paddr));
    assert(paddr != 0);

    RequestPtr req = std::make_shared<Request>(paddr, sizeof(float), 0, 0);
    Packet* pkt = new Packet(req, MemCmd::WriteReq);
    pkt->dataDynamic(new uint8_t[sizeof(float)]);
    pkt->setData((const uint8_t*)(&(cur_stream.partial_sum)));
    pkt->pushSenderState(new TensorSumXcel::SenderState(m_cur_stream_idx));

    // send the request
    if (!m_mem_port_p->sendTimingReq(pkt)) {
      scheduleNextTick();
      delete pkt->popSenderState();
      delete pkt;
    } else {
      DPRINTF(Xcel, "Xcel sent pkt %s x=%d y=%d z=%d\n", pkt->print(),
                cur_stream.x_idx, cur_stream.y_idx, cur_stream.z_idx);
      // marking this tream is writing
      cur_stream.is_writing = true;
      // reset y_idx and move to the next x_idx
      cur_stream.y_idx = 0;
      cur_stream.x_idx++;

      // process the next stream in the next cycle
      m_cur_stream_idx = (m_cur_stream_idx + 1) % m_num_streams;
    }

    return;
  }

  /**
   * out-of-bound check for x-dimension
   */
  if (cur_stream.x_idx == m_args.upper_x_idx) {
    // reset x_idx, y_idx and set z_idx
    cur_stream.x_idx = m_args.lower_x_idx;
    cur_stream.y_idx = 0;
    cur_stream.z_idx += m_num_streams;
    if (cur_stream.z_idx >= m_args.upper_z_idx)
      cur_stream.z_idx = m_args.upper_z_idx;

    // process the next stream in the next cycle
    m_cur_stream_idx = (m_cur_stream_idx + 1) % m_num_streams;
    return;
  }

  /**
   * All out-of-bound checks are done. Make a read request to fetch values
   */
  Addr offset = (cur_stream.x_idx * m_args.dim_1 * m_args.dim_2 +
                 cur_stream.y_idx * m_args.dim_2 +
                 cur_stream.z_idx) * sizeof(float);
  Addr vaddr = m_args.inp_tensor_addr + offset;
  Addr paddr = 0;
  assert(m_cpu_process_p->pTable->translate(vaddr, paddr));
  assert(paddr != 0);

  RequestPtr req = std::make_shared<Request>(paddr, sizeof(float), 0, 0);
  Packet* pkt = new Packet(req, MemCmd::ReadReq);
  pkt->dataDynamic(new uint8_t[sizeof(float)]);
  pkt->pushSenderState(new TensorSumXcel::SenderState(m_cur_stream_idx));

  // send the request
  if (!m_mem_port_p->sendTimingReq(pkt)) {
    scheduleNextTick();
    delete pkt->popSenderState();
    delete pkt;
  } else {
    DPRINTF(Xcel, "Xcel sent pkt %s x=%d y=%d z=%d\n", pkt->print(),
              cur_stream.x_idx, cur_stream.y_idx, cur_stream.z_idx);
    // marking this tream is reading
    cur_stream.is_reading = true;
    // move to the next y_idx
    cur_stream.y_idx++;
    // process the next stream in the next cycle
    m_cur_stream_idx = (m_cur_stream_idx + 1) % m_num_streams;
  }
}

TensorSumXcel*
TensorSumXcelParams::create()
{
  return new TensorSumXcel(this);
}
