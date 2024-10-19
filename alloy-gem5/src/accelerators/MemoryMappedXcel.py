from m5.params import *
from m5.proxy import *

from m5.objects.MemObject import MemObject

class MemoryMappedXcel(MemObject):
  type = 'MemoryMappedXcel'
  cxx_header = "accelerators/memory_mapped_xcel.hh"

  mem_port = MasterPort("Xcel memory port")
