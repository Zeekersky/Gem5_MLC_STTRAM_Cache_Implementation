#==============================================================================
# vmt_io_cpu.py
#==============================================================================
#
# N-thread scalar in-order CPU (i.e., vertical-multithreading)
#
# Authors: Tuan Ta
# Date   : April 16, 2019
#

from m5.objects import *

# Int ALU
class BRG_ALU_Int(FUDesc):
    opList  = [ OpDesc(opClass='IntAlu',      opLat=1,  pipelined=True    ) ]
    count   = 1

# Int Mult and Div units
class BRG_MDU_Int(FUDesc):
    opList  = [ OpDesc(opClass='IntMult',     opLat=5,  pipelined=True    ),
                OpDesc(opClass='IntDiv',      opLat=12, pipelined=False   ),
                OpDesc(opClass='IprAccess',   opLat=3,  pipelined=True    ) ]
    count   = 1

# FPU
class BRG_FPU(FUDesc):
    opList  = [ OpDesc(opClass='FloatAdd',    opLat=5,  pipelined=True    ),
                OpDesc(opClass='FloatCmp',    opLat=5,  pipelined=True    ),
                OpDesc(opClass='FloatCvt',    opLat=5,  pipelined=True    ),
                OpDesc(opClass='FloatDiv',    opLat=9,  pipelined=False   ),
                OpDesc(opClass='FloatSqrt',   opLat=33, pipelined=False   ),
                OpDesc(opClass='FloatMult',   opLat=4),
                OpDesc(opClass='FloatMultAcc',opLat=5),
                OpDesc(opClass='FloatMisc',   opLat=3) ]
    count   = 1

# Load/Store Units
class BRG_Mem(FUDesc):
    opList = [ OpDesc(opClass='MemRead',      opLat=1, pipelined=True ),
               OpDesc(opClass='FloatMemRead', opLat=1, pipelined=True ),
               OpDesc(opClass='MemWrite',     opLat=1, pipelined=True ),
               OpDesc(opClass='FloatMemWrite',opLat=1, pipelined=True ) ]
    count = 1

# Functional Units for this CPU
class BRG_FUP(FUPool):
    @classmethod
    def init_resources(cls, num_threads):
        alu_int = BRG_ALU_Int()
        mdu_int = BRG_MDU_Int()
        fpu     = BRG_FPU()
        mem     = BRG_Mem()

        alu_int.count = 1
        mem.count     = 1
        mdu_int.count = 1
        fpu.count     = 1

        cls.FUList = [alu_int, mdu_int, fpu, mem]

class VMT_IO_CPU(DerivO3CPU):
    @classmethod
    def init_cpu(cls, num_threads,
                 use_min_pc = False,
                 min_pc_threshold = 0):
        cls.numThreads = num_threads

        # In-order issue
        cls.isInOrderIssue      = True

        # Store set parameters are not relavent b/c we do in-order issue
        #LFSTSize = 10                 # Last fetched store table size
        #SSITSize = 10                 # Store set ID table size

        cls.fetchWidth          = 1     # 1 inst per cycle
        cls.decodeWidth         = 1     # 1 inst per cycle
        cls.renameWidth         = 1     # 1 inst per cycle
        cls.dispatchWidth       = 1     # 1 inst per cycle
        cls.issueWidth          = 1     # 1 inst per cycle
        cls.wbWidth             = 1     # 1 inst per cycle
        cls.commitWidth         = 1     # 1 inst per cycle
        cls.squashWidth         = 16

        # Functional units
        BRG_FUP.init_resources(num_threads)
        cls.fuPool              = BRG_FUP()

        # 8 ROB entries for all thread
        cls.numROBEntries           = 8

        # 16 extra registers per thread make sure that pipeline does not stall
        # due to limited physical register file
        cls.numPhysIntRegs          = num_threads * (32 + 16)
        cls.numPhysFloatRegs        = num_threads * (32 + 16)

        # 1 issue slot for all threads
        cls.numIQEntries            = num_threads

        # 5 LQ & SQ entries per thread to ensure full throughput for
        # back-to-back loads hitting L1 cache
        #
        # In the best case in which load or store hits in L1, the instruction
        # is placed into LSQ when it is dispatched at cycle X. It can be issued
        # in the same cycle X. Address calculation happens at cycle X+1. Cache
        # request is sent at the end of cycle X+1. Cache response is returned
        # early at cycle X+2. If WB bandwidth is available, the instruction can
        # write back at the end of cycle X+2. It finally can commit at cycle
        # X+3 and be removed from LSQ.
        #
        cls.LQEntries               = 8 #5
        cls.SQEntries               = 8 #5

        cls.smtNumFetchingThreads   = 1 # num_threads

        cls.useMinPCScheme          = use_min_pc
        cls.minPCStallThreshold     = min_pc_threshold

        cls.smtIQPolicy             = "Partitioned"
        cls.smtLSQPolicy            = "Dynamic"
        cls.smtROBPolicy            = "Dynamic"

    fetchToDecodeDelay  = 1
    decodeToRenameDelay = 1
    renameToIEWDelay    = 1
    renameToROBDelay    = 1 # delay to add an instruction from Rename to ROB
    issueToExecuteDelay = 1
    iewToCommitDelay    = 1

    # backward communication delays need to be at least 1 cycle
    # since the CPU ticks forward, so no way to tick previous stages twice
    decodeToFetchDelay  = 1
    renameToFetchDelay  = 1
    iewToFetchDelay     = 1
    commitToFetchDelay  = 1

    renameToDecodeDelay = 1
    iewToDecodeDelay    = 1
    commitToDecodeDelay = 1

    iewToRenameDelay    = 1
    commitToRenameDelay = 1

    commitToIEWDelay    = 1

    backComSize         = 20
    forwardComSize      = 20

    fetchBufferSize     = 64  # cache line size worth of instructions
    fetchQueueSize      = 1   # number of fetched instructions per thread

    # average latency to finish a trap/syscall
    trapLatency         = 20

    loadLinkedThreshold = 64
