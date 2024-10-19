//========================================================================
// Test Scratchpad Harness
//========================================================================
//
// Authors  : Tuan Ta
// Date     : July 2, 2019
//

#include "test_scratchpad_harness.hh"
#include "test_scratchpad_suite.hh"

TestScratchpadHarness::TestScratchpadHarness(const Params* params)
    : TestHarness(params)
{
  test_suite_ptr = new TestScratchpadSuite(num_test_ports);

  // init directed tests
  test_suite_ptr->initDirectedTests();
}

TestScratchpadHarness*
TestScratchpadHarnessParams::create()
{
  return new TestScratchpadHarness(this);
}
