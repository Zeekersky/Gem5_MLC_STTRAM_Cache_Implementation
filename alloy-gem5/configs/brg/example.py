#==============================================================================
# example.py
#==============================================================================
# An example simulation system configuration
#
# Authors: Tuan Ta
# Date   : 2019/08/04

import optparse
import sys
import os

import m5
from m5.defines import buildEnv
from m5.objects import *
from m5.util import addToPath, fatal, warn

addToPath('../')

from ruby import Ruby

from common import Options
from common import Simulation
from common import CacheConfig
from common import CpuConfig
from common import MemConfig
from common.Caches import *

from common.brg_utils import get_process, copy_cpu_configs

#from smt_io_cpu import SMT_IO_CPU
#from vmt_io_cpu import VMT_IO_CPU

#------------------------------------------------------------------------------
# Adding options
#------------------------------------------------------------------------------

parser = optparse.OptionParser()
Options.addCommonOptions(parser)
Options.addSEOptions(parser)
Options.addBRGOptions(parser)
Options.addLaneOptions(parser)

if '--ruby' in sys.argv:
    Ruby.define_options(parser)

(options, args) = parser.parse_args()

if args:
    print("Error: script doesn't take any positional arguments")
    sys.exit(1)

if options.cmd:
    process = get_process(options)
else:
    print("No workload specified. Exiting!\n")
    sys.exit(1)

#------------------------------------------------------------------------------
# Create CPU instances
#------------------------------------------------------------------------------
#
# Warm-up CPUs are used before ROI
# Main CPUs are used inside ROI
# Cool-down CPUs are used after ROI
#

WarmupCPUClass   = NonCachingSimpleCPU
MainCPUClass, _  = Simulation.getCPUClass(options.cpu_type)
CooldownCPUClass = NonCachingSimpleCPU

WarmupCPUClass.numThreads   = options.nthreads_per_cpu
MainCPUClass.numThreads     = options.nthreads_per_cpu
CooldownCPUClass.numThreads = options.nthreads_per_cpu

# Number of CPUs
np = options.num_cpus

warmup_cpu_list = None
main_cpu_list = None
cooldown_cpu_list = None

if (options.brg_fast_forward):
  warmup_cpu_list   = [ WarmupCPUClass(cpu_id = i) \
                                        for i in xrange(np) ]
  main_cpu_list     = [ MainCPUClass(switched_out = True, cpu_id = i) \
                                        for i in xrange(np) ]
  cooldown_cpu_list = [ CooldownCPUClass(switched_out = True, cpu_id = i) \
                                        for i in xrange(np) ]
else:
  main_cpu_list     = [ MainCPUClass(cpu_id = i) \
                                        for i in xrange(np) ]

#------------------------------------------------------------------------------
# Create the top-level system
#------------------------------------------------------------------------------

# If fast_forward is enabled, the system will start with WarmupCPUClass.
# Otherwise, it will start with MainCPUClass

if (options.brg_fast_forward):
  system = System(cpu             = warmup_cpu_list,
                  mem_mode        = WarmupCPUClass.memory_mode(),
                  mem_ranges      = [AddrRange(options.mem_size)],
                  cache_line_size = options.cacheline_size)
else:
  system = System(cpu             = main_cpu_list,
                  mem_mode        = MainCPUClass.memory_mode(),
                  mem_ranges      = [AddrRange(options.mem_size)],
                  cache_line_size = options.cacheline_size)

## True if using SMT CPU
#system.multi_thread = True

# Create a top-level voltage domain
system.voltage_domain = VoltageDomain(voltage = options.sys_voltage)

# Create a source clock for the system and set the clock period
system.clk_domain = SrcClockDomain(clock =  options.sys_clock,
                                   voltage_domain = system.voltage_domain)

# Create a CPU voltage domain
system.cpu_voltage_domain = VoltageDomain()

# Create a separate clock domain for the CPUs
system.cpu_clk_domain = SrcClockDomain(clock = options.cpu_clock,
                                       voltage_domain =
                                       system.cpu_voltage_domain)

# Configure CPUs
for cpu in system.cpu:
  # All cpus belong to a common cpu_clk_domain, therefore running at a common
  # frequency.
  cpu.clk_domain = system.cpu_clk_domain
  # Assume single-workload simulation. All CPUs are mapped to the same process
  cpu.workload   = process
  cpu.createThreads()
  # Set activity trace flags for all CPUs in the system
  cpu.activity_trace = options.activity_trace

# Set brg fast-forward for the system
system.brg_fast_forward = options.brg_fast_forward

#------------------------------------------------------------------------------
# Create memory system
#------------------------------------------------------------------------------

if options.ruby:
  Ruby.create_system(options, False, system)
  assert(options.num_cpus == len(system.ruby._cpu_ports))

  system.ruby.clk_domain = SrcClockDomain(clock = options.ruby_clock,
                                          voltage_domain = \
                                                        system.voltage_domain)
  for i in xrange(np):
    ruby_port = system.ruby._cpu_ports[i]

    # Create the interrupt controller and connect its ports to Ruby
    # Note that the interrupt controller is always present but only
    # in x86 does it have message ports that need to be connected
    system.cpu[i].createInterruptController()

    # Connect the cpu's cache ports to Ruby
    system.cpu[i].icache_port = ruby_port.slave
    system.cpu[i].dcache_port = ruby_port.slave
    if buildEnv['TARGET_ISA'] == 'x86':
      system.cpu[i].interrupts[0].pio = ruby_port.master
      system.cpu[i].interrupts[0].int_master = ruby_port.slave
      system.cpu[i].interrupts[0].int_slave = ruby_port.master
      system.cpu[i].itb.walker.port = ruby_port.slave
      system.cpu[i].dtb.walker.port = ruby_port.slave
else:
  MemClass = Simulation.setMemClass(options)
  system.membus = SystemXBar()
  system.system_port = system.membus.slave
  CacheConfig.config_cache(options, system)
  MemConfig.config_mem(options, system)

#------------------------------------------------------------------------------
# Create root object
#------------------------------------------------------------------------------

root = Root(full_system = False, system = system)

#------------------------------------------------------------------------------
# Set up for fast-forward mode
#------------------------------------------------------------------------------

if options.brg_fast_forward:
  for i in xrange(np):
    copy_cpu_configs(warmup_cpu_list[i], main_cpu_list[i])
    copy_cpu_configs(main_cpu_list[i],   cooldown_cpu_list[i])

  system.main_cpu     = main_cpu_list
  system.cooldown_cpu = cooldown_cpu_list

  switch_warmup_cpu_pairs   = [ ( warmup_cpu_list[i], main_cpu_list[i] ) \
                                        for i in xrange(np) ]
  switch_cooldown_cpu_pairs = [ ( main_cpu_list[i], cooldown_cpu_list[i] ) \
                                        for i in xrange(np) ]

#------------------------------------------------------------------------------
# Instantiate all m5 objects
#------------------------------------------------------------------------------

checkpoint_dir = None
m5.instantiate(checkpoint_dir)

maxtick = m5.MaxTick
if options.abs_max_tick:
    maxtick = options.abs_max_tick

#------------------------------------------------------------------------------
# Run simulation
#------------------------------------------------------------------------------

#
# check if we should stop the simulation or continue to the next phase
#
def checkExitEvent(exit_event):
  # If either there is no exit event (None event) or exit event is caused by
  # switch cpu, we continue the next simulation phase.
  if (exit_event is None) or (exit_event.getCause() == "switchcpu"):
    return

  # Otherwise, we stop here
  print('Exiting @ tick %i because %s. Exit code %i' % \
            (m5.curTick(), exit_event.getCause(), exit_event.getCode()))
  sys.exit(exit_event.getCode())

if options.brg_fast_forward:
  print("\n\n----- Entering warmup simulation -----\n")
  exit_event = m5.simulate(maxtick)
  print("\n\n----- Exiting warmup simulation @ tick %i because %s -----\n\n" %\
                                (m5.curTick(), exit_event.getCause()))
  checkExitEvent(exit_event)

  print("\n\n----- Switching to main CPUs ----\n")
  exit_event = m5.switchCpus(system, switch_warmup_cpu_pairs)
  checkExitEvent(exit_event)

  print("\n\n----- Entering main simulation -----\n")
  exit_event = m5.simulate(maxtick - m5.curTick())
  print("\n\n----- Exiting main simulation @ tick %i because %s -----\n\n" %\
                                (m5.curTick(), exit_event.getCause()))
  checkExitEvent(exit_event)

  if options.brg_do_cooldown:
    print("\n\n----- Switching to cooldown CPUs -----\n")
    exit_event = m5.switchCpus(system, switch_cooldown_cpu_pairs)
    checkExitEvent(exit_event)

    print("\n\n----- Entering cooldown simulation -----\n")
    exit_event = m5.simulate(maxtick - m5.curTick())
    print("\n\n----- Exiting cooldown simulation @ tick %i because %s \
                      -----\n\n" % (m5.curTick(), exit_event.getCause()))
    checkExitEvent(exit_event)
else:
  print("\n\n----- Entering main simulation -----\n")
  exit_event = m5.simulate(maxtick)
  print("\n\n----- Exiting main simulation @ tick %i because %s -----\n\n" % \
                                (m5.curTick(), exit_event.getCause()))

print('Exit code %i' % exit_event.getCode())

# Set exit code
sys.exit(exit_event.getCode())
