from m5.params import *
from m5.proxy import *

from m5.objects.Process import Process

from MemoryMappedXcel import MemoryMappedXcel

class EmbeddingXcel(MemoryMappedXcel):
  type = 'EmbeddingXcel'
  cxx_header = "accelerators/embedding_xcel.hh"

  cpu_process = Param.Process("CPU process")
  stream_width = Param.Int(8, "number of parallel streams")