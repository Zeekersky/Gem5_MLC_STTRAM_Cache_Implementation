//========================================================================
// Scratchpad
//========================================================================
// This models a scratchpad that supports Ruby network interface and remote
// read/write
//
// +----------------------------------------------------------------+
// |                          RubyNetwork                           |
// +----------------------------------------------------------------+
//     ^              |                     |                 ^
//     |              v                     V                 |
// mem_req_buf   mem_resp_buf        remote_req_buf    remote_resp_buf
//     ^              |                     |                 ^
//     |              v                     V                 |
// +----------------------------------------------------------------+
// |                          Scratchpad                            |
// +----------------------------------------------------------------+
//                                ^
//                                |
//                             cpu_port
//                                |
//                                v
// +----------------------------------------------------------------+
// |                             CPU                                |
// +----------------------------------------------------------------+
//
// Author: Tuan Ta
// Date  : 2019/07/01

#ifndef __MEM_RUBY_SCRATCHPAD_HH__
#define __MEM_RUBY_SCRATCHPAD_HH__

#include <deque>
#include <unordered_map>

#include "mem/packet.hh"
#include "mem/port.hh"
#include "mem/ruby/slicc_interface/AbstractController.hh"
#include "mem/ruby/system/RubySystem.hh"
#include "params/Scratchpad.hh"

//-----------------------------------------------------------------------------
// CpuPort
//-----------------------------------------------------------------------------
// Slave port connected to CPU to handle requests from/responses to CPU

class CpuPort : public SlavePort
{
  public:
    CpuPort(Scratchpad* _scratchpad_p, const std::string& _name);
    ~CpuPort() = default;

    /**
     * Mark that CPU will need to retry sending the last request
     */
    void setRetry() { m_need_retry = true; }

    /**
     * Clear retry flag
     */
    void clearRetry() { m_need_retry = false; }

    /**
     * Check if retry is needed
     */
    bool needRetry() const { return m_need_retry; }

    /**
     * Receive timing request from CPU
     */
    bool recvTimingReq(Packet* pkt) override;

    /**
     * Receive functional request from CPU
     */
    void recvFunctional(Packet* pkt) override;

    /**
     * Receive atomic request from CPU
     */
    Tick recvAtomic(Packet *pkt) override
    { panic("recvAtomic Not implemented\n"); }

    void recvRespRetry() override
    { panic("recvRespRetry Not implemented!\n"); }

    AddrRangeList getAddrRanges() const override
    { panic("getAddrRanges Not implemented!\n"); }

  private:
    Scratchpad* m_scratchpad_p;
    bool m_need_retry;
};

// We reserve the following fields for control flags. Since this is scratchpad,
// software should be fully aware of those flags and their locations in each
// scratchpad
//
// +-----------------------+-----------------------+-------------------------+
// | SPMBaseAddr (64 bits) | xcelgo flag (32 bits) | xceldone flag (32 bits) |
// +-----------------------+-----------------------+-------------------------+

#define SPM_BASE_ADDR_OFFSET  0
#define SPM_GO_FLAG_OFFSET    (SPM_BASE_ADDR_OFFSET + sizeof(uint64_t))
#define SPM_DONE_FLAG_OFFSET  (SPM_GO_FLAG_OFFSET   + sizeof(uint32_t))
#define SPM_ARGS_OFFSET       (SPM_DONE_FLAG_OFFSET + sizeof(uint32_t))

class Scratchpad : public AbstractController
{
  public:
    typedef ScratchpadParams Params;
    Scratchpad(const Params* p);
    ~Scratchpad();

    /**
     * Return slave port
     */
    BaseSlavePort& getSlavePort(const std::string& if_name,
                                PortID idx = InvalidPortID) override;

    /**
     * Initialize network queues from/to Ruby network
     */
    void initNetQueues() override;

    /**
     * Wakeup scratchpad when there're incoming messages from network
     */
    void wakeup() override;

    /**
     * Print out network port's name
     */
    void print(std::ostream& out) const override;

    /**
     * handle CPU request
     */
    bool handleCpuReq(Packet* pkt_p);

    /**
     * handle remote request
     */
    bool handleRemoteReq(Packet* pkt_p, MachineID remote_sender);

    /**
     * handle functional request
     */
    void handleFunctionalCpuReq(Packet* pkt_p);

    /**
     * return number of scratchpad controllers
     */
    static int getNumControllers() { return m_num_scratchpads; }

    /**
     * unused inherited functions
     */

    void resetStats() override { }

    MessageBuffer* getMandatoryQueue() const override
    { return nullptr; }

    MessageBuffer* getMemoryQueue() const override
    { return nullptr; }

    AccessPermission getAccessPermission(const Addr &addr) override
    { return AccessPermission_Invalid; }

    void recordCacheTrace(int cntrl, CacheRecorder* tr) override
    { }

    Sequencer* getCPUSequencer() const override
    { return nullptr; }

    GPUCoalescer* getGPUCoalescer() const override
    { return nullptr; }

    bool functionalRead(const Addr &addr, PacketPtr pkt) override
    { warn("Scratchpad does not support functionalRead\n"); return false; }

    int functionalWriteBuffers(PacketPtr& pkt) override;

    int functionalWrite(const Addr &addr, PacketPtr pkt) override
    { warn("Scratchpad does not support functionalWrite\n"); return false; }

    void collateStats() override
    { warn("Scratchpad does not support collateStats()\n"); }

  private:
    /**
     * Return NodeID of scratchpad owning the given address
     */
    NodeID getScratchpadIdFromAddr(Addr addr) const;

    /**
     * Return local address from the given address
     */
    Addr getLocalAddr(Addr addr) const;

    bool isLocalAddr(Addr addr) const
    { return getScratchpadIdFromAddr(addr) < m_num_scratchpads; }

    /**
     * Access data array
     */
    void accessDataArray(Packet* pkt_p);

    /**
     * Send pending responses to CPU
     */
    void sendCPUResponse();

    /**
     * Get L2 bank ID from address
     */
    NodeID getL2BankFromAddr(Addr addr) const;

  private:
    /**
     * Pointer to Ruby system
     */
    RubySystem* m_ruby_system_p;

    /**
     * This scratchpad's size
     */
    const size_t m_size;

    /**
     * Base address of the SPM
     */
    const Addr m_base_spm_addr;

    /**
     * CPU port
     */
    CpuPort* m_cpu_port_p;

    /**
     * Ruby network buffers
     */
    MessageBuffer* m_mem_req_buffer_p;     // Mem req from this scratchpad
    MessageBuffer* m_mem_resp_buffer_p;    // Mem resp to this scratchpad
    MessageBuffer* m_remote_req_buffer_p;  // Remote req from other scratchpads
    MessageBuffer* m_remote_resp_buffer_p; // Remote resp to other scratchpads

    /**
     * Number of scratchpads
     */
    static int m_num_scratchpads;

    /**
     * Internal data array
     */
    uint8_t* m_data_array;

    /**
     * List of pending CPU response packets
     */
    std::deque<Packet*> m_cpu_resp_pkts;

    /**
     * Event used to respond CPU
     */
    EventFunctionWrapper m_cpu_resp_event;

    /**
     * List of all pending memory packets
     */
    std::unordered_map<uint64_t, Packet*> m_pending_pkt_map;
    uint64_t m_cur_seq_num;
    const uint64_t m_max_num_pending_pkts;

    /**
     * Queue of pending control requests
     */
    typedef std::pair<MachineID, Packet*> CtrlReq;
    CtrlReq m_pending_base_addr_req;
    CtrlReq m_pending_go_flag_req;
    CtrlReq m_pending_done_flag_req;

    /**
     * Pointers to control fields
     */
    uint64_t* const m_base_addr_p;
    uint32_t* const m_go_flag_p;
    uint32_t* const m_done_flag_p;

    // Number of L2 banks
    const int m_num_l2s;
};

#endif // MEM_RUBY_SCRATCHPAD_HH
