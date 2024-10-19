//=============================================================================
// memory_mapped_xcel.hh
//=============================================================================
//
// This models an accelerator that communicates with host processors through a
// specific memory region mapped to the accelerator. This model is different
// from the BaseAccelerator that communicates with the host processor through
// ROCC interface.
//
// Author: Tuan Ta
// Date  : 19/07/09

#ifndef __MEMORY_MAPPED_XCEL_HH__
#define __MEMORY_MAPPED_XCEL_HH__

#include "mem/mem_object.hh"
#include "mem/packet.hh"
#include "mem/port.hh"
#include "mem/request.hh"
#include "params/MemoryMappedXcel.hh"

class XcelMemPort : public MasterPort {
  public:
    XcelMemPort(const std::string& _name, MemoryMappedXcel* _xcel_p);
    ~XcelMemPort() = default;

    virtual bool recvTimingResp(Packet* pkt_p) override;
    virtual void recvReqRetry() override;
  private:
    MemoryMappedXcel* m_xcel_p;
};

class MemoryMappedXcel : public MemObject {
  public:
    typedef MemoryMappedXcelParams Params;
    MemoryMappedXcel(const Params* p);
    ~MemoryMappedXcel() = default;

    /**
     * Process memory response packet from memory
     */
    virtual bool processMemResp(Packet* pkt_p)
    { panic("processMemResp() not implemented\n"); }

    /**
     * Retry the last failed request
     */
    virtual void retry()
    { panic("retry() not implemented\n"); }

  protected:
    /**
     * Port connecting to memory
     */
    XcelMemPort* m_mem_port_p;

    /**
     * Tick event object
     */
    EventFunctionWrapper m_tick_event;

    /**
     * Get master memory port
     */
    BaseMasterPort& getMasterPort(const std::string& if_name,
                                  PortID idx = InvalidPortID) override
    { return *m_mem_port_p; }

    /**
     * Tick every cycle
     */
    virtual void tick()
    { panic("tick() not implemented\n"); }

    void scheduleNextTick();
};

#endif // __MEMORY_MAPPED_XCEL_HH__
