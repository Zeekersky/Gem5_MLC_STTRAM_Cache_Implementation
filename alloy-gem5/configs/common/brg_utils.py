#------------------------------------------------------------------------------
# brg_utils
#------------------------------------------------------------------------------
# Utility functions used by BRG
#
# Author: Tuan Ta
# Date  : 19/08/04

import optparse
import sys
import os

import m5
from m5.defines import buildEnv
from m5.objects import *
from m5.util import addToPath, fatal, warn

#------------------------------------------------------------------------------
# Get workload process
#------------------------------------------------------------------------------

def get_process(options):
  inputs = []
  outputs = []
  errouts = []
  pargs = []

  workloads = options.cmd.split(';')
  if options.input != "":
    inputs = options.input.split(';')
  if options.output != "":
    outputs = options.output.split(';')
  if options.errout != "":
    errouts = options.errout.split(';')
  if options.options != "":
    pargs = options.options.split(';')

  # we're not simulating multi-program workloads
  assert(len(workloads) == 1)

  wrkld = workloads[0]

  process = Process(pid = 100)
  process.executable = wrkld
  process.cwd = os.getcwd()

  if options.env:
    with open(options.env, 'r') as f:
      process.env = [line.rstrip() for line in f]

  if len(pargs) > 0:
    process.cmd = [wrkld] + pargs[0].split()
  else:
    process.cmd = [wrkld]

  if len(inputs) > 0:
    process.input = inputs[0]
  if len(outputs) > 0:
    process.output = outputs[0]
  if len(errouts) > 0:
    process.errout = errouts[0]

  return process

#------------------------------------------------------------------------------
# Copy CPU config parameters from an old_cpu to a new_cpu (for fast-forwarding)
#------------------------------------------------------------------------------

def copy_cpu_configs(old_cpu, new_cpu):
  new_cpu.system                = old_cpu.system
  new_cpu.socket_id             = old_cpu.socket_id
  new_cpu.numThreads            = old_cpu.numThreads
  new_cpu.syscallRetryLatency   = old_cpu.syscallRetryLatency
  new_cpu.clk_domain            = old_cpu.clk_domain
  new_cpu.workload              = old_cpu.workload
  new_cpu.interrupts            = old_cpu.interrupts
  new_cpu.isa                   = old_cpu.isa
  new_cpu.max_insts_all_threads = old_cpu.max_insts_all_threads
  new_cpu.activity_trace        = old_cpu.activity_trace

