from TestHarness import TestHarness
from m5.params import *
from m5.proxy import *

class TestScratchpadHarness(TestHarness):
  type = 'TestScratchpadHarness'
  cxx_header = "brg-utst/test-scratchpad/test_scratchpad_harness.hh"
