//=============================================================================
// ActiveMessage
//=============================================================================

#ifndef __MEM_RUBY_SLICC_INTERFACE_ACTIVEMESSAGE_HH__
#define __MEM_RUBY_SLICC_INTERFACE_ACTIVEMESSAGE_HH__

#include "cpu/structures/ActiveMsgPacket.hh"
#include "mem/ruby/slicc_interface/Message.hh"

class ActiveMessage : public Message
{
  public:
    ActiveMessage(Tick _cur_time,
                  MachineID _src,
                  MachineID _dest,
                  ActiveMsgPacket* _packet_p);
    ActiveMessage(const ActiveMessage& other);

    MsgPtr clone() const override;

    void print(std::ostream& out) const override;

    const MessageSizeType& getMessageSize() const override;

    MessageSizeType& getMessageSize() override;

    bool functionalRead(Packet* pkt) override
    { panic("Active message does not support functionalRead\n"); }

    bool functionalWrite(Packet* pkt) override
    { panic("Active message does not support functionalWrite\n"); }

    const NetDest& getDestination() const override;
    NetDest& getDestination() override;

    ActiveMsgPacket* getPacket() const;

  private:
    MachineID m_sender;
    NetDest m_destinations;
    MessageSizeType m_message_size;
    ActiveMsgPacket* m_packet_p;
};

#endif // MEM_RUBY_SLICC_INTERFACE_ACTIVEMESSAGE_HH

