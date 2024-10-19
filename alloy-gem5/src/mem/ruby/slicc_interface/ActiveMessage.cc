//=============================================================================
// ActiveMessage
//=============================================================================

#include "mem/ruby/slicc_interface/ActiveMessage.hh"

#include "mem/ruby/system/NetworkAdapter.hh"

ActiveMessage::ActiveMessage(Tick _cur_time,
                             MachineID _src,
                             MachineID _dest,
                             ActiveMsgPacket* _packet_p)
  : Message(_cur_time),
    m_sender(_src),
    m_destinations(true),
    m_message_size(MessageSizeType_Control),
    m_packet_p(_packet_p)
{
  m_destinations.add(_dest);
}

ActiveMessage::ActiveMessage(const ActiveMessage& other)
  : Message(other),
    m_sender(other.m_sender),
    m_destinations(other.m_destinations),
    m_message_size(other.m_message_size),
    m_packet_p(other.m_packet_p)
{ }

MsgPtr
ActiveMessage::clone() const
{
  return std::shared_ptr<Message>(new ActiveMessage(*this));
}

void
ActiveMessage::print(std::ostream& out) const
{
  out << "[ActiveMessage: ";
  out << "sender = " << m_sender << " ";
  out << "destinations = " << m_destinations << " ";
  out << "size = " << m_message_size << " ";
  out << "]";
}

const MessageSizeType&
ActiveMessage::getMessageSize() const
{
  return m_message_size;
}

MessageSizeType&
ActiveMessage::getMessageSize()
{
  return m_message_size;
}

const NetDest&
ActiveMessage::getDestination() const
{
  return m_destinations;
}

NetDest&
ActiveMessage::getDestination()
{
  return m_destinations;
}

ActiveMsgPacket*
ActiveMessage::getPacket() const
{
  return m_packet_p;
}
