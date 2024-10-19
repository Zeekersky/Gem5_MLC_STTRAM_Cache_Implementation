//=============================================================================
// TestNetworkAdapterHarness
//=============================================================================

#include "brg-utst/test-network-adapter/test_nw_adapter_harness.hh"

#include <iomanip>

#include "sim/sim_exit.hh"

//-----------------------------------------------------------------------------
// OutReqPort
//-----------------------------------------------------------------------------
// Port that delivers requests from and responses to this test harness

OutReqPort::OutReqPort(TestNWAdapterHarness* _harness,
                       TestCPU* _cpu_p,
                       const std::string& _name,
                       int _port_id)
    : MasterPort(_name, _harness),
      m_test_harness_p(_harness),
      m_test_cpu_p(_cpu_p),
      m_port_id(_port_id)
{ }

bool
OutReqPort::recvTimingResp(Packet *pkt)
{
  ActiveMsgPacket* active_msg_pkt = dynamic_cast<ActiveMsgPacket*>(pkt);
  assert(active_msg_pkt);
  return m_test_cpu_p->recvResp(active_msg_pkt);
}

//-----------------------------------------------------------------------------
// InReqPort
//-----------------------------------------------------------------------------
// Port that delivers requests from and responses to the outside test object

InReqPort::InReqPort(TestNWAdapterHarness* _harness,
                     TestCPU* _cpu_p,
                     const std::string& _name,
                     int _port_id)
    : SlavePort(_name, _harness),
      m_test_harness_p(_harness),
      m_test_cpu_p(_cpu_p),
      m_port_id(_port_id)
{ }

bool
InReqPort::recvTimingReq(Packet *pkt)
{
  ActiveMsgPacket* active_msg_pkt = dynamic_cast<ActiveMsgPacket*>(pkt);
  assert(active_msg_pkt);
  return m_test_cpu_p->recvReq(active_msg_pkt);
}

void
InReqPort::recvRespRetry()
{
  m_test_cpu_p->sendResp();
}

//-----------------------------------------------------------------------------
// TestCPU
//-----------------------------------------------------------------------------

TestCPU::TestCPU(uint64_t num_cpus, uint64_t cpu_id, uint64_t num_tasks,
                 TestNWAdapterHarness* harness_p,
                 OutReqPort* out_req_port_p,
                 InReqPort* in_req_port_p)
    : m_num_cpus(num_cpus),
      m_cpu_id(cpu_id),
      m_curr_task_id(num_tasks),
      m_test_harness_p(harness_p),
      m_out_req_port_p(out_req_port_p),
      m_in_req_port_p(in_req_port_p),
      m_is_stealing(false),
      m_pending_resp(nullptr)
{ }

bool
TestCPU::recvReq(ActiveMsgPacket* pkt_p)
{
  // adding some randomness here to emulate interrupt
  if (random() % 2) {
    // register a request event in the victim CPU
    m_test_harness_p->
            registerExpResp(pkt_p->getSenderId(),
                            TestEvent(ActiveMsgPacket::ActiveMsgCmd::Nack,
                            m_cpu_id,
                            0));
    return false;   // reject the request
  }

  assert(pkt_p->isRequest());

  if (m_pending_resp) {
    // there's already a pending response that is waiting
    // can't accept more request
    return false;
  }

  TestEvent incoming_event = TestEvent(pkt_p->getActiveMsgCmd(),
                                       pkt_p->getSenderId(),
                                       pkt_p->getPayload());

  std::cout << "cycle " << std::setw(10) << m_test_harness_p->curCycle()
            << ": cpu " << m_cpu_id
            << ": received Req  " << pkt_p->print() << "\n";

  auto pred = [&incoming_event](const TestEvent& event)
                                          { return incoming_event == event; };

  auto it = std::find_if(m_exp_req_vec.begin(), m_exp_req_vec.end(), pred);
  assert(it != m_exp_req_vec.end());

  // respond the request
  pkt_p->makeResponse();

  if (m_curr_task_id > 0) {
    pkt_p->setActiveMsgCmd(ActiveMsgPacket::ActiveMsgCmd::Ack);
    pkt_p->setPayload(m_curr_task_id);
    m_curr_task_id--;
  } else {
    pkt_p->setActiveMsgCmd(ActiveMsgPacket::ActiveMsgCmd::Nack);
    pkt_p->setPayload(0);
  }

  // erase the request event
  m_exp_req_vec.erase(it);

  // send the response
  m_pending_resp = pkt_p;

  return sendResp();
}

bool
TestCPU::recvResp(ActiveMsgPacket* pkt_p)
{
  assert(pkt_p->isResponse());

  TestEvent incoming_event = TestEvent(pkt_p->getActiveMsgCmd(),
                                       pkt_p->getSenderId(),
                                       pkt_p->getPayload());

  std::cout << "cycle " << std::setw(10) << m_test_harness_p->curCycle()
            << ": cpu " << m_cpu_id
            << ": received Resp " << pkt_p->print() << "\n";

  auto pred = [&incoming_event](const TestEvent& event)
                                          { return incoming_event == event; };

  if (pkt_p->getActiveMsgCmd() == ActiveMsgPacket::ActiveMsgCmd::Ack)
    m_test_harness_p->consumeOneTask();

  auto it = std::find_if(m_exp_resp_vec.begin(), m_exp_resp_vec.end(), pred);
  assert(it != m_exp_resp_vec.end());

  // erase the response event
  m_exp_resp_vec.erase(it);

  // delete pkt_p since this CPU created the packet
  delete pkt_p;

  assert(m_is_stealing);
  m_is_stealing = false;

  return true;
}

bool
TestCPU::sendResp()
{
  assert(m_pending_resp);

  if (m_in_req_port_p->sendTimingResp(m_pending_resp)) {
    std::cout << "cycle " << std::setw(10) << m_test_harness_p->curCycle()
              << ": cpu " << m_cpu_id
              << ": sent     Resp " << m_pending_resp->print() << "\n";

    // register a response event in the receiver's exp_resp_vec
    m_test_harness_p->
            registerExpResp(m_pending_resp->getReceiverId(),
                            TestEvent(m_pending_resp->getActiveMsgCmd(),
                                      m_pending_resp->getSenderId(),
                                      m_pending_resp->getPayload()));

    // clear the pending response
    m_pending_resp = nullptr;

    return true;
  }

  return false;
}

void
TestCPU::registerExpReq(TestEvent req_event)
{
  m_exp_req_vec.push_back(req_event);
}

void
TestCPU::registerExpResp(TestEvent resp_event)
{
  m_exp_resp_vec.push_back(resp_event);
}

void
TestCPU::steal()
{
  // select a victim
  uint64_t victim_cpu_id;
  do {
    victim_cpu_id = random() % m_num_cpus;
  } while (victim_cpu_id == m_cpu_id);

  // make a request packet
  ActiveMsgPacket* pkt_p = new ActiveMsgPacket(m_cpu_id, victim_cpu_id, 0);
  pkt_p->setActiveMsgCmd(ActiveMsgPacket::ActiveMsgCmd::Get);

  if (!m_out_req_port_p->sendTimingReq(pkt_p)) {
    delete pkt_p;
    return;
  }

  std::cout << "cycle " << std::setw(10) << m_test_harness_p->curCycle()
            << ": cpu " << m_cpu_id
            << ": sent     Req  " << pkt_p->print() << "\n";

  // register a request event in the victim CPU
  m_test_harness_p->registerExpReq(victim_cpu_id,
                                   TestEvent(pkt_p->getActiveMsgCmd(),
                                             m_cpu_id,
                                             0));

  assert(!m_is_stealing);
  m_is_stealing = true;
}

void
TestCPU::printProgress()
{
  std::cout << "-------------------------\n";
  std::cout << "cpu " << m_cpu_id << "\n";
  for ( auto event : m_exp_req_vec )
    std::cout << "Req  from " << event.cpu_id << "\n";
  for ( auto event : m_exp_resp_vec )
    std::cout << "Resp from " << event.cpu_id << "\n";
}

//-----------------------------------------------------------------------------
// TestNWAdapterHarness
//-----------------------------------------------------------------------------

TestNWAdapterHarness::TestNWAdapterHarness(const Params* p)
    : MemObject(p),
      m_num_cpus(p->num_cpus),
      m_tick_event([this]{ tick(); },
                   "test harness tick event",
                   false,
                   Event::Progress_Event_Pri),
      m_deadlock_event([this]{ progress(); },
                       "test harness progress event",
                        false),
      m_max_tasks_per_cpu(p->max_tasks_per_cpu),
      m_num_remaining_tasks(0)
{
  for (int i = 0; i < m_num_cpus; i++) {
    std::string out_port_name = csprintf(".out_req_ports[%d]", i);
    std::string in_port_name  = csprintf(".in_req_ports[%d]",  i);

    OutReqPort* out_port_p = new OutReqPort(this, nullptr, out_port_name, i);
    InReqPort*  in_port_p  = new InReqPort(this, nullptr, in_port_name, i);

    TestCPU* cpu_p = new TestCPU(m_num_cpus, i, 0,
                                 this, out_port_p, in_port_p);

    out_port_p->setCPU(cpu_p);
    in_port_p->setCPU(cpu_p);

    m_out_req_ports.push_back(out_port_p);
    m_in_req_ports.push_back(in_port_p);
    m_cpus.push_back(cpu_p);
  }

  configTests();

  schedule(m_tick_event, curTick());
  schedule(m_deadlock_event, Cycles(1000000000));
}

TestNWAdapterHarness::~TestNWAdapterHarness()
{
  for (auto port : m_out_req_ports) delete port;
  for (auto port : m_in_req_ports) delete port;
  for (auto cpu : m_cpus) delete cpu;
}

BaseMasterPort&
TestNWAdapterHarness::getMasterPort(const std::string &if_name, PortID idx)
{
  return *(m_out_req_ports[idx]);
}

BaseSlavePort&
TestNWAdapterHarness::getSlavePort(const std::string &if_name, PortID idx)
{
  return *(m_in_req_ports[idx]);
}

void
TestNWAdapterHarness::configTests()
{
  for (auto cpu : m_cpus) {
    int num_tasks = random() % m_max_tasks_per_cpu;
    m_num_remaining_tasks += num_tasks;
    cpu->setNumTasks(num_tasks);
  }

  // make some CPU tasks empty
  for (int i = 0; i < m_num_cpus/2; i++) {
    m_num_remaining_tasks -= m_cpus[i]->getNumTasks();
    m_cpus[i]->setNumTasks(0);
  }
}

void
TestNWAdapterHarness::tick()
{
  uint64_t num_remaining_tasks = 0;
  bool is_someone_stealing = false;
  for (auto cpu_p : m_cpus) {
    num_remaining_tasks += cpu_p->getNumTasks();
    if (cpu_p->isStealing())
      is_someone_stealing = true;
  }

  if (num_remaining_tasks == 0 && !is_someone_stealing) {
    // check if all tasks have been consumed
    assert(m_num_remaining_tasks == 0);

    // we can exit now
    exitSimLoop("Test completed!");
    return;
  }

  if (num_remaining_tasks > 0) {
    for (auto cpu_p : m_cpus) {
      if (cpu_p->needToSteal()) {
        cpu_p->steal();
      }
    }
  }

  schedule(m_tick_event, clockEdge(Cycles(1)));
}

void
TestNWAdapterHarness::progress()
{
  for (auto cpu_p : m_cpus) {
    cpu_p->printProgress();
  }
  //schedule(m_deadlock_event, Cycles(10000000));
  panic("no forward progress\n");
}

TestNWAdapterHarness*
TestNWAdapterHarnessParams::create()
{
  return new TestNWAdapterHarness(this);
}
