//=============================================================================
// ActiveMsgPacket
//=============================================================================

#include "cpu/structures/ActiveMsgPacket.hh"

ActiveMsgPacket::ActiveMsgPacket(unsigned int _sender_id,
                                 unsigned int _receiver_id,
                                 uint64_t _payload,
                                 int _num_payload)
    : Packet(std::make_shared<Request>(), MemCmd::GenericRequest),
      m_cmd(ActiveMsgCmd::Invalid),
      m_payloads(_num_payload),
      m_sender_cpu_id(_sender_id),
      m_receiver_cpu_id(_receiver_id)
{
    assert(_num_payload >= 1);
    m_payloads[0] = _payload;
}

void
ActiveMsgPacket::makeResponse()
{
  Packet::makeResponse();

  // flip sender and receiver
  int temp = m_sender_cpu_id;
  m_sender_cpu_id = m_receiver_cpu_id;
  m_receiver_cpu_id = temp;
}

std::string
ActiveMsgPacket::print() const
{
  std::ostringstream ss;

  ss << "[sender_id = " << m_sender_cpu_id;
  ss << ", receiver_id = " << m_receiver_cpu_id;
  ss << ", cmd = ";

  switch (m_cmd) {
    case ActiveMsgCmd::Get:
      ss << "GET";
      break;
    case ActiveMsgCmd::Ack:
      ss << "ACK";
      break;
    case ActiveMsgCmd::Nack:
      ss << "NACK";
      break;
    case ActiveMsgCmd::Invalid:
      ss << "INVALID";
      break;
    default:
      panic("Invalid active msg command\n");
  }

  ss << ", payload = (";
  for (size_t i = 0; i < m_payloads.size(); i++) {
      if (i > 0) {
          ss << ",";
      }
      ss << m_payloads[i];
  }
  ss << ")]";

  return ss.str();
}

void
ActiveMsgPacket::setPayload(uint64_t payload)
{
  m_payloads[0] = payload;
}

void
ActiveMsgPacket::setPayload(int i, uint64_t payload)
{
  assert(i >= 0);
  assert(i < m_payloads.size());
  m_payloads[i] = payload;
}

uint64_t
ActiveMsgPacket::getPayload() const
{
  return m_payloads[0];
}

uint64_t
ActiveMsgPacket::getPayload(int i) const
{
  assert(i >= 0);
  assert(i < m_payloads.size());
  return m_payloads[i];
}

ActiveMsgPacket::ActiveMsgCmd
ActiveMsgPacket::getActiveMsgCmd() const
{
  return m_cmd;
}

void
ActiveMsgPacket::setActiveMsgCmd(ActiveMsgCmd cmd)
{
  m_cmd = cmd;
}

unsigned int
ActiveMsgPacket::getSenderId() const
{
  return m_sender_cpu_id;
}

unsigned int
ActiveMsgPacket::getReceiverId() const
{
  return m_receiver_cpu_id;
}

bool
ActiveMsgPacket::isRequest() const
{
  return Packet::isRequest() && m_cmd == ActiveMsgCmd::Get;
}

bool
ActiveMsgPacket::isResponse() const
{
  return Packet::isResponse() &&
         (m_cmd == ActiveMsgCmd::Ack || m_cmd == ActiveMsgCmd::Nack);
}
