//========================================================================
// Test Scratchpad Suite
//========================================================================
//
// A collection of all tests cases for memory controller
//
// Authors  : Tuan Ta
// Date     : Sep 26, 2018
//

#include <iostream>
#include <sstream>

#include "test_scratchpad_suite.hh"

TestScratchpadSuite::TestScratchpadSuite(int _num_test_ports)
    : TestSuite(_num_test_ports)
{ }

void
TestScratchpadSuite::initDirectedTests()
{
  //                                              id, cmd              , addr, ref_val, store_val
  test_queues[0].emplace( new TestScratchpadCase(  0, MemCmd::WriteReq , 0x00,       0,        10 ) );
  test_queues[0].emplace( new TestScratchpadCase(  1, MemCmd::WriteReq , 0x04,       0,         1 ) );
  test_queues[0].emplace( new TestScratchpadCase(  2, MemCmd::ReadReq  , 0x04,       1,         0 ) );

  test_queues[1].emplace( new TestScratchpadCase(  3, MemCmd::ReadReq  , 0x00,      10,         0 ) );
  test_queues[1].emplace( new TestScratchpadCase(  4, MemCmd::WriteReq , 0x00,       0,        30 ) );
  test_queues[1].emplace( new TestScratchpadCase(  5, MemCmd::ReadReq  , 0x00,      30,         0 ) );

  test_queues[1].emplace( new TestScratchpadCase(  5, MemCmd::ReadReq  , 0x08,       0,         0 ) );
  test_queues[1].emplace( new TestScratchpadCase(  5, MemCmd::ReadReq  , 0x0c,       0,         0 ) );

  // fill the second way
  test_queues[1].emplace( new TestScratchpadCase(  5, MemCmd::ReadReq  , 0x80,       0,         0 ) );
  test_queues[1].emplace( new TestScratchpadCase(  5, MemCmd::WriteReq , 0x80,       0,        50 ) );

  // evict
  test_queues[1].emplace( new TestScratchpadCase(  5, MemCmd::WriteReq , 0x100,      0,        60 ) );

  test_queues[1].emplace( new TestScratchpadCase(  5, MemCmd::ReadReq  , 0x80,      50,         0 ) );
  test_queues[1].emplace( new TestScratchpadCase(  5, MemCmd::ReadReq  , 0x100,     60,         0 ) );

//  test_queues[1].emplace( new TestScratchpadCase(  5, MemCmd::WriteReq , 0x0c,       0,        20 ) );
//  test_queues[1].emplace( new TestScratchpadCase(  5, MemCmd::ReadReq  , 0x0c,      20,         0 ) );
//
//  test_queues[1].emplace( new TestScratchpadCase(  5, MemCmd::WriteReq , 0x08,       0,        40 ) );
//  test_queues[1].emplace( new TestScratchpadCase(  5, MemCmd::ReadReq  , 0x08,      40,         0 ) );
//
//  test_queues[1].emplace( new TestScratchpadCase(  5, MemCmd::ReadReq  , 0x0c,      20,         0 ) );
//
//  test_queues[1].emplace( new TestScratchpadCase(  7, MemCmd::WriteReq , 0x08,       0,        30 ) );
//  test_queues[1].emplace( new TestScratchpadCase(  8, MemCmd::ReadReq  , 0x08,      30,         0 ) );
}

void
TestScratchpadSuite::initRandomTests()
{
  // TODO
}

PacketPtr
TestScratchpadSuite::getNextReqPkt(int port_id)
{
  assert(!test_queues[port_id].empty());

  std::shared_ptr<TestScratchpadCase> test_case =
        std::dynamic_pointer_cast<TestScratchpadCase>
            (test_queues[port_id].front());

  assert(!test_case->issued);

  RequestPtr req = std::make_shared<Request>(0,                // asid
                                             test_case->addr,  // virtual addr
                                             sizeof(int),      // size in bytes
                                             0,                // flags
                                             port_id,          // port id
                                             0,                // pc
                                             0                 // context ID
                                            );

  // Virtual addr and physical addr are the same
  req->setPaddr(test_case->addr);
  req->setReqInstSeqNum(test_case->id);

  // Create a new packet
  PacketPtr pkt = new Packet(req, test_case->cmd);
  uint8_t* data = new uint8_t[sizeof(int)];

  if (test_case->cmd == MemCmd::WriteReq) {
    for (int i = 0; i < sizeof(int); i++)
      data[i] = ((uint8_t*)&(test_case->store_val))[i];
  }

  pkt->dataDynamic(data);

  return pkt;
}

bool
TestScratchpadSuite::verifyRespPkt(int port_id, PacketPtr resp_pkt)
{
  // some sanity checks
  assert(resp_pkt && resp_pkt->req);

  assert(!test_queues[port_id].empty() &&
          test_queues[port_id].front()->issued);

  std::shared_ptr<TestScratchpadCase> test_case =
        std::dynamic_pointer_cast<TestScratchpadCase>
            (test_queues[port_id].front());

  int recv_test_id = resp_pkt->req->getReqInstSeqNum();
  Addr recv_addr = resp_pkt->getAddr();
  int recv_val = *(resp_pkt->getPtr<int>());

  if (test_case->cmd == MemCmd::ReadReq &&
      resp_pkt->cmd  != MemCmd::ReadResp) {
    std::cout << "ERROR: mismatched request type -"
              << " received = " << (resp_pkt->cmd).toString()
              << " expected = MemCmd::ReadResp"
              << std::endl;
    return false;
  }

  if (test_case->cmd == MemCmd::WriteReq &&
      resp_pkt->cmd  != MemCmd::WriteResp) {
    std::cout << "ERROR: mismatched request type -"
              << " received = " << (resp_pkt->cmd).toString()
              << " expected = MemCmd::WriteResp"
              << std::endl;
    return false;
  }

  if (test_case->id != recv_test_id) {
    std::cout << "ERROR: mismatched test case ID -"
              << " received = " << recv_test_id
              << " expected = " << test_case->id
              << std::endl;
    return false;
  }

  if (test_case->addr != recv_addr) {
    std::cout << "ERROR: mismatched address -"
              << " received = " << recv_addr
              << " expected = " << test_case->addr
              << std::endl;
    return false;
  }

  if (test_case->cmd == MemCmd::ReadReq &&
      test_case->ref_val != recv_val) {
    std::cout << "ERROR: mismatched return value -"
              << " received = " << recv_val
              << " expected = " << test_case->ref_val
              << std::endl;
    return false;
  }

  return true;
}

std::string
TestScratchpadSuite::printHeadTestCase(int port_id) const
{
  assert(!test_queues[port_id].empty());

  std::shared_ptr<TestScratchpadCase> test_case =
        std::dynamic_pointer_cast<TestScratchpadCase>
            (test_queues[port_id].front());

  std::stringstream ret_str;
  ret_str << "[ port = " << port_id
          << ", id = " << test_case->id
          << ", cmd = " << (test_case->cmd).toString()
          << ", addr = " << test_case->addr
          << ", ref_val = " << test_case->ref_val
          << ", store_val = " << test_case->store_val
          << " ]";

  return ret_str.str();
}
