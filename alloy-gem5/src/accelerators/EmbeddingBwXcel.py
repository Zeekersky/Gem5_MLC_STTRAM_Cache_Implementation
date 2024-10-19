from m5.params import *
from m5.proxy import *

from m5.objects.Process import Process

from MemoryMappedXcel import MemoryMappedXcel

class EmbeddingBwXcel(MemoryMappedXcel):
  type = 'EmbeddingBwXcel'
  cxx_header = "accelerators/embedding_bw_xcel.hh"

  cpu_process = Param.Process("CPU process")
  stream_width = Param.Int(8, "number of parallel streams")
