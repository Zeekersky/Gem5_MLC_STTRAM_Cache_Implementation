//========================================================================
// Test Scratchpad Harness
//========================================================================
//
// Authors  : Tuan Ta
// Date     : July 2, 2019
//

#ifndef TEST_SCRATCHPAD_HARNESS_HH
#define TEST_SCRATCHPAD_HARNESS_HH

#include "brg-utst/test_harness.hh"
#include "params/TestScratchpadHarness.hh"

class TestScratchpadHarness : public TestHarness {

  public:

    typedef TestScratchpadHarnessParams Params;

    TestScratchpadHarness(const Params* params);
    ~TestScratchpadHarness() = default;

};

#endif // TEST_SCRATCHPAD_HARNESS_HH
