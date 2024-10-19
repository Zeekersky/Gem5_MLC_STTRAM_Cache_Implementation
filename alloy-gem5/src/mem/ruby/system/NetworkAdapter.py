from m5.params import *
from m5.proxy import *
from Controller import RubyController

class NetworkAdapter(RubyController):
  type = 'NetworkAdapter'
  cxx_class = "NetworkAdapter"
  cxx_header = "mem/ruby/system/NetworkAdapter.hh"

  node_id           = Param.Int(0, "Node ID")
  cpuReqBuffer      = Param.MessageBuffer("")
  networkRespBuffer = Param.MessageBuffer("")
  networkReqBuffer  = Param.MessageBuffer("")
  cpuRespBuffer     = Param.MessageBuffer("")

  cpu_req_port      = SlavePort("cpu_req_port")
  network_req_port  = MasterPort("network_req_port")
