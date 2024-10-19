//=============================================================================
// TestNWAdapterHarness
//=============================================================================

#ifndef __TEST_NW_ADAPTER_HARNESS__
#define __TEST_NW_ADAPTER_HARNESS__

#include "cpu/structures/ActiveMsgPacket.hh"
#include "mem/mem_object.hh"
#include "mem/port.hh"
#include "params/TestNWAdapterHarness.hh"

class TestCPU;
class TestNWAdapterHarness;

//-----------------------------------------------------------------------------
// OutReqPort
//-----------------------------------------------------------------------------
// Port that delivers requests from and responses to this test harness

class OutReqPort : public MasterPort
{
  public:
    OutReqPort(TestNWAdapterHarness* _harness,
               TestCPU* _cpu_p,
               const std::string& _name,
               int _port_id);
    ~OutReqPort() = default;

    void setCPU(TestCPU* _cpu_p) { m_test_cpu_p = _cpu_p; }

  protected:
    bool recvTimingResp(Packet *pkt) override;
    void recvReqRetry() override
    { panic("recvReqRetry not implemented\n"); }
    void recvTimingSnoopReq(Packet *pkt) override
    { panic("recvTimingSnoopReq Not implemented!\n"); }
    Tick recvAtomicSnoop(Packet *pkt) override
    { panic("recvAtomicSnoop Not implemented!\n"); }

  private:
    TestNWAdapterHarness* m_test_harness_p;
    TestCPU*              m_test_cpu_p;
    int                   m_port_id;
};

//-----------------------------------------------------------------------------
// InReqPort
//-----------------------------------------------------------------------------
// Port that delivers requests from and responses to the outside test object

class InReqPort : public SlavePort
{
  public:
    InReqPort(TestNWAdapterHarness* _harness,
              TestCPU* _cpu_p,
              const std::string& _name,
              int _port_id);
    ~InReqPort() = default;

    void setCPU(TestCPU* _cpu_p) { m_test_cpu_p = _cpu_p; }

  protected:
    bool recvTimingReq(Packet *pkt) override;
    void recvFunctional(Packet *pkt) override
    { panic("recvFunctional Not implemented\n"); }
    Tick recvAtomic(Packet *pkt) override
    { panic("recvAtomic Not implemented\n"); }
    void recvRespRetry() override;
    AddrRangeList getAddrRanges() const override
    { panic("getAddrRanges Not implemented!\n"); }

  private:
    TestNWAdapterHarness* m_test_harness_p;
    TestCPU*              m_test_cpu_p;
    int                   m_port_id;
};

//-----------------------------------------------------------------------------
// TestCPU
//-----------------------------------------------------------------------------

class TestCPU
{
  public:

    struct TestEvent {
      TestEvent(ActiveMsgPacket::ActiveMsgCmd _cmd,
                uint64_t _cpu_id,
                uint64_t _payload)
          : cmd(_cmd),
            cpu_id(_cpu_id),
            payload(_payload)
      { }

      bool operator==(const TestEvent& other) const
      {
        return cmd == other.cmd &&
               cpu_id == other.cpu_id &&
               payload == other.payload;
      }

      ActiveMsgPacket::ActiveMsgCmd cmd;      // Get/Ack/Nack
      uint64_t                      cpu_id;   // sender's ID
      uint64_t                      payload;  // payload
    };

    TestCPU(uint64_t num_cpus, uint64_t cpu_id, uint64_t num_tasks,
            TestNWAdapterHarness* harness_p,
            OutReqPort* out_req_port_p, InReqPort* in_req_port_p);
    ~TestCPU() = default;

    bool recvReq(ActiveMsgPacket* pkt_p);
    bool recvResp(ActiveMsgPacket* pkt_p);

    // send the m_pending_resp packet
    bool sendResp();

    void registerExpReq(TestEvent req_event);
    void registerExpResp(TestEvent resp_event);

    // check if this CPU needs to steal tasks
    // a CPU needs to steal only if it's not currently stealing and its task
    // queue is empty
    bool needToSteal() const
    { return m_curr_task_id == 0 && !m_is_stealing; }

    bool isStealing() const
    { return m_is_stealing; }

    // randomly select a victim and send a "Get" request to steal a task from
    // the victim
    void steal();

    void setNumTasks(uint64_t num_tasks) { m_curr_task_id = num_tasks; }
    uint64_t getNumTasks() const { return m_curr_task_id; }

    void printProgress();

    bool hasPendingResp() const { return m_pending_resp != nullptr; }

  private:
    const uint64_t          m_num_cpus;
    const uint64_t          m_cpu_id;
    uint64_t                m_curr_task_id;

    TestNWAdapterHarness*   m_test_harness_p;
    OutReqPort*             m_out_req_port_p;
    InReqPort*              m_in_req_port_p;

    std::vector<TestEvent>  m_exp_req_vec;
    std::vector<TestEvent>  m_exp_resp_vec;

    bool                    m_is_stealing;

    ActiveMsgPacket*        m_pending_resp;
};

//-----------------------------------------------------------------------------
// TestNWAdapterHarness
//-----------------------------------------------------------------------------

class TestNWAdapterHarness : public MemObject
{
  public:
    typedef TestNWAdapterHarnessParams Params;

    TestNWAdapterHarness(const Params* params);
    ~TestNWAdapterHarness();

    BaseMasterPort& getMasterPort(const std::string &if_name,
                                  PortID idx = InvalidPortID) override;

    BaseSlavePort& getSlavePort(const std::string &if_name,
                                PortID idx = InvalidPortID) override;

    void registerExpReq(uint64_t cpu_id, TestCPU::TestEvent event)
    { (m_cpus[cpu_id])->registerExpReq(event); }

    void registerExpResp(uint64_t cpu_id, TestCPU::TestEvent event)
    { (m_cpus[cpu_id])->registerExpResp(event); }

    void tick();
    void configTests();
    bool isDone() const;

    void progress();

    void consumeOneTask() { m_num_remaining_tasks--; }

  private:
    const int                 m_num_cpus;
    std::vector<OutReqPort*>  m_out_req_ports;
    std::vector<InReqPort*>   m_in_req_ports;
    std::vector<TestCPU*>     m_cpus;

    EventFunctionWrapper m_tick_event;
    EventFunctionWrapper m_deadlock_event;

    const int                 m_max_tasks_per_cpu;
    int                       m_num_remaining_tasks;
};

#endif // __TEST_NW_ADAPTER_HARNESS__
