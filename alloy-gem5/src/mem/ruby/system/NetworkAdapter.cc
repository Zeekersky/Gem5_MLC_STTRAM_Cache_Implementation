//=============================================================================
// NetworkAdapter
//=============================================================================
// This adapter supports a direct 2-way communication channel between a CPU and
// a network. Both CPU and network can send requests and responses to each
// other through the adapter.

#include "mem/ruby/system/NetworkAdapter.hh"

#include "debug/NetworkAdapter.hh"
#include "mem/ruby/network/Network.hh"
#include "mem/ruby/slicc_interface/ActiveMessage.hh"

int NetworkAdapter::m_num_controllers = 0;

//-----------------------------------------------------------------------------
// CpuReqPort
//-----------------------------------------------------------------------------
// Slave port connected to CPU to handle requests from CPU

CpuReqPort::CpuReqPort(NetworkAdapter*    _network_adapter_p,
                       CpuReqHandler*     _cpu_req_handler_p,
                       const std::string& _name)
    : SlavePort(_name, _network_adapter_p),
      m_network_adapter_p(_network_adapter_p),
      m_cpu_req_handler_p(_cpu_req_handler_p),
      m_need_retry(false)
{ }

bool
CpuReqPort::recvTimingReq(Packet *pkt)
{
  ActiveMsgPacket* active_msg_pkt = dynamic_cast<ActiveMsgPacket*>(pkt);
  assert(active_msg_pkt);

  if (m_cpu_req_handler_p->handleRequest(active_msg_pkt)) {
    assert(!needRetry());
    return true;
  }

  setRetry();
  return false;
}

//-----------------------------------------------------------------------------
// NetworkReqPort
//-----------------------------------------------------------------------------
// Master port connected to the adapter to handle requests from Network

NetworkReqPort::NetworkReqPort(NetworkAdapter*    _network_adapter_p,
                               NetworkReqHandler* _network_req_handler_p,
                               const std::string& _name)
    : MasterPort(_name, _network_adapter_p),
      m_network_adapter_p(_network_adapter_p),
      m_network_req_handler_p(_network_req_handler_p),
      m_need_retry(false)
{ }

bool
NetworkReqPort::recvTimingResp(Packet* pkt)
{
  ActiveMsgPacket* active_msg_pkt = dynamic_cast<ActiveMsgPacket*>(pkt);
  assert(active_msg_pkt);

  if (m_network_req_handler_p->handleResponse(active_msg_pkt)) {
    assert(!needRetry());
    return true;
  }

  setRetry();
  return false;
}

//-----------------------------------------------------------------------------
// NetworkAdapter
//-----------------------------------------------------------------------------
// Main adapter connecting both CPU and network

NetworkAdapter::NetworkAdapter(const Params* p)
    : AbstractController(p),
      m_cpu_req_buffer_p(p->cpuReqBuffer),
      m_network_resp_buffer_p(p->networkRespBuffer),
      m_network_req_buffer_p(p->networkReqBuffer),
      m_cpu_resp_buffer_p(p->cpuRespBuffer)
{
  m_machineID.type = MachineType_NetworkAdapter;
  m_machineID.num = m_version;
  m_num_controllers++;

  // create req handlers
  m_cpu_req_handler_p = new CpuReqHandler(this,
                                          nullptr,
                                          m_cpu_req_buffer_p,
                                          m_network_resp_buffer_p);

  m_network_req_handler_p = new NetworkReqHandler(this,
                                                  nullptr,
                                                  m_network_req_buffer_p,
                                                  m_cpu_resp_buffer_p);
  // create req ports
  m_cpu_req_port_p =
             new CpuReqPort(this,
                            m_cpu_req_handler_p,
                            this->name() + ".cpu_req_port");
  m_network_req_port_p =
             new NetworkReqPort(this,
                                m_network_req_handler_p,
                                this->name() + ".network_req_port");

  m_cpu_req_handler_p->setCpuReqPort(m_cpu_req_port_p);
  m_network_req_handler_p->setNetworkReqPort(m_network_req_port_p);

  // set consumer for incoming buffers
  m_network_req_buffer_p->setConsumer(this);
  m_network_resp_buffer_p->setConsumer(this);
}

NetworkAdapter::~NetworkAdapter()
{
  delete m_cpu_req_port_p;
  delete m_network_req_port_p;
  delete m_cpu_req_handler_p;
  delete m_network_req_handler_p;
}

void
NetworkAdapter::initNetQueues()
{
  MachineType machine_type = string_to_MachineType("NetworkAdapter");
  int base M5_VAR_USED = MachineType_base_number(machine_type);

  assert(m_cpu_req_buffer_p);
  m_net_ptr->setToNetQueue(m_version + base,
                           m_cpu_req_buffer_p->getOrdered(),
                           1,
                           "request",
                           m_cpu_req_buffer_p);

  assert(m_network_resp_buffer_p);
  m_net_ptr->setFromNetQueue(m_version + base,
                             m_network_resp_buffer_p->getOrdered(),
                             0,
                             "response",
                             m_network_resp_buffer_p);

  assert(m_network_req_buffer_p);
  m_net_ptr->setFromNetQueue(m_version + base,
                             m_network_req_buffer_p->getOrdered(),
                             1,
                             "request",
                             m_network_req_buffer_p);

  assert(m_cpu_resp_buffer_p);
  m_net_ptr->setToNetQueue(m_version + base,
                           m_cpu_resp_buffer_p->getOrdered(),
                           0,
                           "response",
                           m_cpu_resp_buffer_p);
}

BaseMasterPort&
NetworkAdapter::getMasterPort(const std::string &if_name, PortID idx)
{
  return *m_network_req_port_p;
}

BaseSlavePort&
NetworkAdapter::getSlavePort(const std::string &if_name, PortID idx)
{
  return *m_cpu_req_port_p;
}

void
NetworkAdapter::wakeup()
{
  // Check if we have any response from the network
  if (m_network_resp_buffer_p->isReady(clockEdge())) {
    const ActiveMessage* msg_p =
        dynamic_cast<const ActiveMessage*>(m_network_resp_buffer_p->peek());
    assert(msg_p);

    ActiveMsgPacket* pkt_p = msg_p->getPacket();
    assert(pkt_p && pkt_p->isResponse());

    DPRINTF(NetworkAdapter, "adapter %d: handling pkt %s\n",
              m_version, pkt_p->print());

    if (m_cpu_req_handler_p->handleResponse(pkt_p)) {
      // successfully delivered the response
      m_network_resp_buffer_p->dequeue(clockEdge());
    } else {
      DPRINTF(NetworkAdapter, "adapter %d: pkt %s FAILED\n",
              m_version, pkt_p->print());

      // failed to deliver the response packet, so schedule a wakeup in the
      // next cycle to retry
      scheduleEvent(Cycles(1));
    }
  }

  // Check if we have any request from the network
  if (m_network_req_buffer_p->isReady(clockEdge())) {
    const ActiveMessage* msg_p =
        dynamic_cast<const ActiveMessage*>(m_network_req_buffer_p->peek());
    assert(msg_p);

    ActiveMsgPacket* pkt_p = msg_p->getPacket();
    assert(pkt_p && pkt_p->isRequest());

    DPRINTF(NetworkAdapter, "adapter %d: handling pkt %s\n",
              m_version, pkt_p->print());

    if (m_network_req_handler_p->handleRequest(pkt_p)) {
      // successfully delivered the request
      m_network_req_buffer_p->dequeue(clockEdge());
    } else {
      DPRINTF(NetworkAdapter, "adapter %d: pkt %s FAILED\n",
              m_version, pkt_p->print());

      // failed to deliver the response packet, so schedule a wakeup in the
      // next cycle to retry
      scheduleEvent(Cycles(1));
      DPRINTF(NetworkAdapter, "FAILED\n");
    }
  }

  // Wake up CPU to retry sending a request to this adapter
  if (m_cpu_req_port_p->needRetry()) {
    m_cpu_req_port_p->sendRetryReq();
    m_cpu_req_port_p->clearRetry();
  }

  // Wake up CPU to retry sending a response to this adapter
  if (m_network_req_port_p->needRetry()) {
    m_network_req_port_p->sendRetryResp();
    m_network_req_port_p->clearRetry();
  }

  if (!m_network_resp_buffer_p->isEmpty() ||
      !m_network_req_buffer_p->isEmpty()) {
    scheduleEvent(Cycles(1));
  }
}

void
NetworkAdapter::print(std::ostream& out) const
{
  out << "NetworkAdapter_" << m_version;
}

//-----------------------------------------------------------------------------
// CpuReqHandler
//-----------------------------------------------------------------------------
// Handle requests from CPU and responses to CPU

CpuReqHandler::CpuReqHandler(NetworkAdapter*  _network_adapter_p,
                             CpuReqPort*      _cpu_req_port_p,
                             MessageBuffer*   _cpu_req_buffer_p,
                             MessageBuffer*   _network_resp_buffer_p)
    : m_network_adapter_p(_network_adapter_p),
      m_cpu_req_port_p(_cpu_req_port_p),
      m_cpu_req_buffer_p(_cpu_req_buffer_p),
      m_network_resp_buffer_p(_network_resp_buffer_p)
{ }

bool
CpuReqHandler::handleRequest(ActiveMsgPacket* pkt_p)
{
  assert(pkt_p->isRequest());
  if (m_cpu_req_buffer_p->
                    areNSlotsAvailable(1, m_network_adapter_p->clockEdge())) {
    // Make a message
    MachineID src_port  = { MachineType_NetworkAdapter,
                            pkt_p->getSenderId() };
    MachineID dest_port = { MachineType_NetworkAdapter,
                            pkt_p->getReceiverId() };

    std::shared_ptr<ActiveMessage> msg_p =
            std::make_shared<ActiveMessage>(m_network_adapter_p->clockEdge(),
                                            src_port,
                                            dest_port,
                                            pkt_p);

    // push the message into the m_cpu_req_buffer
    m_cpu_req_buffer_p->enqueue(msg_p,
                                m_network_adapter_p->clockEdge(),
                                m_network_adapter_p->cyclesToTicks(Cycles(1)));

    return true;
  }

  return false;
}

bool
CpuReqHandler::handleResponse(ActiveMsgPacket* pkt_p)
{
  if (!m_cpu_req_port_p->sendTimingResp(pkt_p)) {
    panic("Failed to send a response m_cpu_req_port!\n");
  }

  return true;
}

//-----------------------------------------------------------------------------
// NetworkReqHandler
//-----------------------------------------------------------------------------
// Handle requests from network and responses to network

NetworkReqHandler::NetworkReqHandler(NetworkAdapter* _network_adapter_p,
                                     NetworkReqPort* _network_req_port_p,
                                     MessageBuffer*  _network_req_buffer_p,
                                     MessageBuffer*  _cpu_resp_buffer_p)
    : m_network_adapter_p(_network_adapter_p),
      m_network_req_port_p(_network_req_port_p),
      m_network_req_buffer_p(_network_req_buffer_p),
      m_cpu_resp_buffer_p(_cpu_resp_buffer_p)
{ }

bool
NetworkReqHandler::handleRequest(ActiveMsgPacket* pkt_p)
{
  if (m_network_req_port_p->sendTimingReq(pkt_p)) {
    return true;
  } else if (!m_cpu_resp_buffer_p->
                    areNSlotsAvailable(1, m_network_adapter_p->clockEdge())) {
    // the request was rejected, and we DO NOT have space in the
    // m_cpu_resp_buffer to send a Nack message.
    return false;
  }

  // the request was rejected, and we have space in the m_cpu_resp_buffer
  // to send a Nack message

  // make a NACK response message to inform that the request was rejected
  pkt_p->makeResponse();
  pkt_p->setActiveMsgCmd(ActiveMsgPacket::ActiveMsgCmd::Nack);

  MachineID src_port  = { MachineType_NetworkAdapter,
                          pkt_p->getSenderId() };
  MachineID dest_port = { MachineType_NetworkAdapter,
                          pkt_p->getReceiverId() };
  std::shared_ptr<ActiveMessage> out_msg_p =
              std::make_shared<ActiveMessage>(m_network_adapter_p->clockEdge(),
                                              src_port,
                                              dest_port,
                                              pkt_p);
  m_cpu_resp_buffer_p->enqueue(out_msg_p,
                               m_network_adapter_p->clockEdge(),
                               m_network_adapter_p->cyclesToTicks(Cycles(1)));

  return true;
}

bool
NetworkReqHandler::handleResponse(ActiveMsgPacket* pkt_p)
{
  assert(pkt_p->isResponse());
  if (m_cpu_resp_buffer_p->
                    areNSlotsAvailable(1, m_network_adapter_p->clockEdge())) {
    // Make a message
    MachineID src_port  = { MachineType_NetworkAdapter,
                            pkt_p->getSenderId() };
    MachineID dest_port = { MachineType_NetworkAdapter,
                            pkt_p->getReceiverId() };

    std::shared_ptr<ActiveMessage> msg_p =
            std::make_shared<ActiveMessage>(m_network_adapter_p->clockEdge(),
                                            src_port,
                                            dest_port,
                                            pkt_p);

    // push the message into the m_cpu_resp_buffer
    m_cpu_resp_buffer_p->
                   enqueue(msg_p,
                           m_network_adapter_p->clockEdge(),
                           m_network_adapter_p->cyclesToTicks(Cycles(1)));

    return true;
  }

  return false;
}

NetworkAdapter*
NetworkAdapterParams::create()
{
  return new NetworkAdapter(this);
}
