from MemObject import MemObject
from m5.params import *
from m5.proxy import *

class TestNWAdapterHarness(MemObject):
  type = 'TestNWAdapterHarness'
  cxx_header = "brg-utst/test-network-adapter/test_nw_adapter_harness.hh"
  num_cpus = Param.Unsigned(2, "Number of CPUs")

  out_req_ports = VectorMasterPort("Outgoing request ports")
  in_req_ports  = VectorSlavePort("Incoming request ports")
  max_tasks_per_cpu = Param.Unsigned(100, "max number of tasks per CPU");
