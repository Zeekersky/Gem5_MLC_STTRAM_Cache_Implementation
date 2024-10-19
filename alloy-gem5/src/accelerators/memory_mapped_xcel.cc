//=============================================================================
// memory_mapped_xcel.cc
//=============================================================================
//
// This models an accelerator that communicates with host processors through a
// specific memory region mapped to the accelerator. This model is different
// from the BaseAccelerator that communicates with the host processor through
// ROCC interface.
//
// Author: Tuan Ta
// Date  : 19/07/09

#include "accelerators/memory_mapped_xcel.hh"

#include "debug/Xcel.hh"

//-----------------------------------------------------------------------------
// XcelMemPort
//-----------------------------------------------------------------------------

XcelMemPort::XcelMemPort(const std::string& _name, MemoryMappedXcel* _xcel_p)
  : MasterPort(_name, _xcel_p),
    m_xcel_p(_xcel_p)
{ }

bool
XcelMemPort::recvTimingResp(Packet* pkt_p) {
  return m_xcel_p->processMemResp(pkt_p);
}

void
XcelMemPort::recvReqRetry() {
  m_xcel_p->retry();
}

//-----------------------------------------------------------------------------
// MemoryMappedXcel
//-----------------------------------------------------------------------------

MemoryMappedXcel::MemoryMappedXcel(const Params* p)
  : MemObject(p),
    m_mem_port_p(new XcelMemPort(this->name() + ".mem_port", this)),
    m_tick_event([this]{ tick(); }, "Tick xcel", false)
{ }

void
MemoryMappedXcel::scheduleNextTick()
{
  if (!m_tick_event.scheduled())
    schedule(m_tick_event, clockEdge(Cycles(1)));
}

MemoryMappedXcel*
MemoryMappedXcelParams::create()
{
  return new MemoryMappedXcel(this);
}
