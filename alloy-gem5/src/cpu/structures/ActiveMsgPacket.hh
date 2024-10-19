//=============================================================================
// ActiveMsgPacket
//=============================================================================

#ifndef __CPU_STRUCTURES_ACTIVE_MSG_PACKET_HH__
#define __CPU_STRUCTURES_ACTIVE_MSG_PACKET_HH__

#include "mem/packet.hh"
#include <vector>

class ActiveMsgPacket : public Packet
{
  public:

    enum ActiveMsgCmd {
      Get,      // Request to steal a task
      Ack,      // Ack to a Get request
      Nack,     // Nack to a Get request
      Invalid   // Invalid command
    };

    ActiveMsgPacket(unsigned int _sender_id,
                    unsigned int _receiver_id,
                    uint64_t _payload,
                    int _num_payload = 1);
    ~ActiveMsgPacket() = default;

    void makeResponse() override;

    std::string print() const override;

    void setPayload(uint64_t payload);
    void setPayload(int i, uint64_t payload);
    uint64_t getPayload() const;
    uint64_t getPayload(int i) const;

    ActiveMsgCmd getActiveMsgCmd() const;

    void setActiveMsgCmd(ActiveMsgCmd cmd);

    unsigned int getSenderId() const;
    unsigned int getReceiverId() const;

    bool isRequest() const override;
    bool isResponse() const override;

  private:

    ActiveMsgCmd m_cmd;
    std::vector<uint64_t> m_payloads;
    unsigned int m_sender_cpu_id;
    unsigned int m_receiver_cpu_id;
};

#endif // CPU_STRUCTURES_ACTIVE_MSG_PACKET_HH

