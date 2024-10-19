#==============================================================================
# single_issue_io_core
#==============================================================================
#
# single-issue in-order CPU
#
# Authors: Tuan Ta
# Date   : Feb 22, 2019
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
    FUList = [ BRG_ALU_Int(),
               BRG_MDU_Int(),
               BRG_FPU(),
               BRG_Mem() ]

class SingleIssueInOrderCPU(DerivO3CPU):
    LSQDepCheckShift = 0

    # In-order issue
    isInOrderIssue      = True

    # No SMT
    numThreads          = 1

    # Store set parameters are not relavent b/c we do in-order issue
    #LFSTSize = 10                 # Last fetched store table size
    #SSITSize = 10                 # Store set ID table size

    fetchWidth          = 1
    decodeWidth         = 1
    renameWidth         = 1
    dispatchWidth       = 1
    issueWidth          = 1
    wbWidth             = 1
    commitWidth         = 1
    squashWidth         = 1

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

    fetchBufferSize     = 64
    fuPool              = BRG_FUP()
    trapLatency         = 13
    backComSize         = 5
    forwardComSize      = 5

    numPhysIntRegs   = 40 # 32 logical regs + extra 8 for 8 in-flight insts
    numPhysFloatRegs = 40 # 32 logical regs + extra 8 for 8 in-flight insts
    #numPhysVecRegs = 48
    numIQEntries     = 1
    numROBEntries    = 8

    # 2-stage mem pipeline
    LQEntries       = 2
    SQEntries       = 2
