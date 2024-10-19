//=============================================================================
// NetworkAdapter
//=============================================================================
// This adapter supports a direct 2-way communication channel between a CPU and
// a network. Both CPU and network can send requests and responses to each
// other through the adapter.

#ifndef __MEM_RUBY_SYSTEM_NETWORK_ADAPTER_HH__
#define __MEM_RUBY_SYSTEM_NETWORK_ADAPTER_HH__

#include "cpu/structures/ActiveMsgPacket.hh"
#include "mem/port.hh"
#include "mem/ruby/slicc_interface/AbstractController.hh"
#include "params/NetworkAdapter.hh"

class NetworkAdapter;
class CpuReqPort;
class NetworkReqPort;

//-----------------------------------------------------------------------------
// CpuReqHandler
//-----------------------------------------------------------------------------
// Handle requests from CPU and responses to CPU

class CpuReqHandler
{
  public:
    CpuReqHandler(NetworkAdapter* _network_adapter_p,
                  CpuReqPort*     _cpu_req_port_p,
                  MessageBuffer*  _cpu_req_buffer_p,
                  MessageBuffer*  _network_resp_buffer_p);
    ~CpuReqHandler() = default;

    void setCpuReqPort(CpuReqPort* _cpu_req_port_p)
    { m_cpu_req_port_p = _cpu_req_port_p; }

    // try to send a packet to the network
    // return true if the packet is successfully sent out
    // otherwise return false
    bool handleRequest(ActiveMsgPacket* pkt_p);

    // deliver a response packet to the CPU
    // this function assumes no back pressure from the CPU, assuming the CPU
    // is blocking and waiting for the response. Therefore, the function
    // should always return true.
    bool handleResponse(ActiveMsgPacket* pkt_p);

  private:
    NetworkAdapter* m_network_adapter_p;
    CpuReqPort*     m_cpu_req_port_p;
    MessageBuffer*  m_cpu_req_buffer_p;       // CPU-initiated requests
    MessageBuffer*  m_network_resp_buffer_p;  // Network-initiated responses
};

//-----------------------------------------------------------------------------
// NetworkReqHandler
//-----------------------------------------------------------------------------
// Handle requests from network and responses to network

class NetworkReqHandler
{
  public:
    NetworkReqHandler(NetworkAdapter* _network_adapter_p,
                      NetworkReqPort* _network_req_port_p,
                      MessageBuffer*  _network_req_buffer_p,
                      MessageBuffer*  _cpu_resp_buffer_p);
    ~NetworkReqHandler() = default;

    void setNetworkReqPort(NetworkReqPort* _network_req_port_p)
    { m_network_req_port_p = _network_req_port_p; }

    // try to send a request packet to the CPU
    // return true if the packet is successfully handled
    bool handleRequest(ActiveMsgPacket* pkt_p);

    // try to send a response packet to the network
    // return true if the packet is successfully sent
    // otherwise return false
    bool handleResponse(ActiveMsgPacket* pkt_p);

  private:
    NetworkAdapter* m_network_adapter_p;
    NetworkReqPort* m_network_req_port_p;
    MessageBuffer*  m_network_req_buffer_p;   // Network-initiated requests
    MessageBuffer*  m_cpu_resp_buffer_p;      // CPU-initiated responses
};

//-----------------------------------------------------------------------------
// CpuReqPort
//-----------------------------------------------------------------------------
// Slave port connected to CPU to handle requests from CPU
// recvTimingReq: receive req from CPU
// sendTimingResp: send resp to CPU

class CpuReqPort : public SlavePort
{
  public:
    CpuReqPort(NetworkAdapter*    _network_adapter_p,
               CpuReqHandler*     _cpu_req_handler_p,
               const std::string& _name);
    ~CpuReqPort() = default;

    void setRetry() { m_need_retry = true; }
    void clearRetry() { m_need_retry = false; }
    bool needRetry() const { return m_need_retry; }

  protected:
    bool recvTimingReq(Packet *pkt) override;
    void recvFunctional(Packet *pkt) override
    { panic("recvFunctional Not implemented\n"); }
    Tick recvAtomic(Packet *pkt) override
    { panic("recvAtomic Not implemented\n"); }
    void recvRespRetry() override
    { panic("recvRespRetry Not implemented!\n"); }
    AddrRangeList getAddrRanges() const override
    { panic("getAddrRanges Not implemented!\n"); }

  private:
    NetworkAdapter* m_network_adapter_p;
    CpuReqHandler*  m_cpu_req_handler_p;
    bool            m_need_retry;             // Need to send a retry
};

//-----------------------------------------------------------------------------
// NetworkReqPort
//-----------------------------------------------------------------------------
// Master port connected to the adapter to handle requests from Network
// sendTimingReq: send req to CPU
// recvTimingResp: receive resp from CPU

class NetworkReqPort : public MasterPort
{
  public:
    NetworkReqPort(NetworkAdapter*    _network_adapter_p,
                   NetworkReqHandler* _network_req_hander_p,
                   const std::string& _name);
    ~NetworkReqPort() = default;

    void setRetry() { m_need_retry = true; }
    void clearRetry() { m_need_retry = false; }
    bool needRetry() const { return m_need_retry; }

  protected:
    bool recvTimingResp(Packet *pkt) override;
    void recvReqRetry() override
    { panic("recvReqRetry not implemented\n"); }
    void recvTimingSnoopReq(Packet *pkt) override
    { panic("recvTimingSnoopReq Not implemented!\n"); }
    Tick recvAtomicSnoop(Packet *pkt) override
    { panic("recvAtomicSnoop Not implemented!\n"); }

  private:
    NetworkAdapter*     m_network_adapter_p;
    NetworkReqHandler*  m_network_req_handler_p;
    bool                m_need_retry;             // Need to send a retry
};

//-----------------------------------------------------------------------------
// NetworkAdapter
//-----------------------------------------------------------------------------
// Main adapter connecting both CPU and network

class NetworkAdapter : public AbstractController
{
  public:

    typedef NetworkAdapterParams Params;
    NetworkAdapter(const Params* p);
    ~NetworkAdapter();

    void initNetQueues() override;

    BaseMasterPort& getMasterPort(const std::string &if_name,
                                  PortID idx = InvalidPortID) override;

    BaseSlavePort& getSlavePort(const std::string &if_name,
                                PortID idx = InvalidPortID) override;

    // this wakes up the adapter when there are incoming messages from network
    void wakeup() override;

    // print out the network port's name
    void print(std::ostream& out) const override;

    static int getNumControllers()
    { return m_num_controllers; }

  private:

    // CPU-side ports
    CpuReqPort*       m_cpu_req_port_p;
    NetworkReqPort*   m_network_req_port_p;

    // Network-side buffers
    MessageBuffer*    m_cpu_req_buffer_p;       // CPU-initiated requests
    MessageBuffer*    m_network_resp_buffer_p;  // Network-initiated responses

    MessageBuffer*    m_network_req_buffer_p;   // Network-initiated requests
    MessageBuffer*    m_cpu_resp_buffer_p;      // CPU-initiated responses

    // request handlers
    // m_cpu_req_handler:     handle from-CPU requests and to-CPU responses
    // m_network_req_handler: handle from-network requests and to-network
    //                        responses
    CpuReqHandler*     m_cpu_req_handler_p;
    NetworkReqHandler* m_network_req_handler_p;

    static int m_num_controllers;
};

#endif // MEM_RUBY_SYSTEM_NETWORK_ADAPTER_HH
