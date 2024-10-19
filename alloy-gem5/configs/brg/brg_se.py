# Copyright (c) 2012-2013 ARM Limited
# All rights reserved.
#
# The license below extends only to copyright in the software and shall
# not be construed as granting a license to any other intellectual
# property including but not limited to intellectual property relating
# to a hardware implementation of the functionality of the software
# licensed hereunder.  You may use the software subject to the license
# terms below provided that you ensure that this notice is replicated
# unmodified and in its entirety in all distributions of the software,
# modified or unmodified, in source code or in binary form.
#
# Copyright (c) 2006-2008 The Regents of The University of Michigan
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Authors: Steve Reinhardt

# Simple test script
#
# "m5 test.py"

#----------------------------------------------------------------------------
# @tuan: a BRG version of configs/example/se.py configuration file
# This is for now mainly used to support --brg-fast-forward option
#----------------------------------------------------------------------------

import optparse
import sys
import os
import math

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
from common.cpu2000 import *

# Check if KVM support has been enabled, we might need to do VM
# configuration if that's the case.
have_kvm_support = 'BaseKvmCPU' in globals()
def is_kvm_cpu(cpu_class):
    return have_kvm_support and cpu_class != None and \
        issubclass(cpu_class, BaseKvmCPU)

def get_processes(options):
    """Interprets provided options and returns a list of processes"""

    multiprocesses = []
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

    idx = 0
    for wrkld in workloads:
        process = Process(pid = 100 + idx)
        process.executable = wrkld
        process.cwd = os.getcwd()

        if options.env:
            with open(options.env, 'r') as f:
                process.env = [line.rstrip() for line in f]

        if len(pargs) > idx:
            process.cmd = [wrkld] + pargs[idx].split()
        else:
            process.cmd = [wrkld]

        if len(inputs) > idx:
            process.input = inputs[idx]
        if len(outputs) > idx:
            process.output = outputs[idx]
        if len(errouts) > idx:
            process.errout = errouts[idx]

        multiprocesses.append(process)
        idx += 1

    if options.smt:
        assert(options.cpu_type == "DerivO3CPU")
        return multiprocesses, idx
    else:
        return multiprocesses, 1

#------------------------------------------------------------------------------
# make network topology
#------------------------------------------------------------------------------

def makeActiveMsgNetworkTopology(adapters, network, IntLink, ExtLink, Router):
    nodes = adapters

    num_routers = len(nodes)
    num_rows = int( math.sqrt(num_routers) )

    if num_rows == 0:
      num_rows = 1

    link_latency = 1
    router_latency = 1 # only used by garnet

    # There must be an evenly divisible number of cntrls to routers
    # Also, obviously the number or rows must be <= the number of routers
    cntrls_per_router, remainder = divmod(len(nodes), num_routers)
    assert(remainder == 0)
    assert(num_rows > 0 and num_rows <= num_routers)
    num_columns = int(num_routers / num_rows)
    assert(num_columns * num_rows == num_routers)

    # Create the routers in the mesh
    routers = [Router(router_id=i, latency = router_latency) \
        for i in range(num_routers)]
    network.routers = routers

    # link counter to set unique link ids
    link_count = 0

    # Add all but the remainder nodes to the list of nodes to be uniformly
    # distributed across the network.
    network_nodes = []
    remainder_nodes = []
    for node_index in xrange(len(nodes)):
        if node_index < (len(nodes) - remainder):
            network_nodes.append(nodes[node_index])
        else:
            remainder_nodes.append(nodes[node_index])

    # Connect each node to the appropriate router
    ext_links = []
    for (i, n) in enumerate(network_nodes):
        cntrl_level, router_id = divmod(i, num_routers)
        assert(cntrl_level < cntrls_per_router)
        ext_links.append(ExtLink(link_id=link_count, ext_node=n,
                                int_node=routers[router_id],
                                latency = link_latency))
        link_count += 1

    network.ext_links = ext_links

    # Create the mesh links.
    int_links = []

    # East output to West input links (weight = 1)
    for row in xrange(num_rows):
        for col in xrange(num_columns):
            if (col + 1 < num_columns):
                east_out = col + (row * num_columns)
                west_in = (col + 1) + (row * num_columns)
                int_links.append(IntLink(link_id=link_count,
                                         src_node=routers[east_out],
                                         dst_node=routers[west_in],
                                         src_outport="East",
                                         dst_inport="West",
                                         latency = link_latency,
                                         weight=1))
                link_count += 1

    # West output to East input links (weight = 1)
    for row in xrange(num_rows):
        for col in xrange(num_columns):
            if (col + 1 < num_columns):
                east_in = col + (row * num_columns)
                west_out = (col + 1) + (row * num_columns)
                int_links.append(IntLink(link_id=link_count,
                                         src_node=routers[west_out],
                                         dst_node=routers[east_in],
                                         src_outport="West",
                                         dst_inport="East",
                                         latency = link_latency,
                                         weight=1))
                link_count += 1

    # North output to South input links (weight = 2)
    for col in xrange(num_columns):
        for row in xrange(num_rows):
            if (row + 1 < num_rows):
                north_out = col + (row * num_columns)
                south_in = col + ((row + 1) * num_columns)
                int_links.append(IntLink(link_id=link_count,
                                         src_node=routers[north_out],
                                         dst_node=routers[south_in],
                                         src_outport="North",
                                         dst_inport="South",
                                         latency = link_latency,
                                         weight=2))
                link_count += 1

    # South output to North input links (weight = 2)
    for col in xrange(num_columns):
        for row in xrange(num_rows):
            if (row + 1 < num_rows):
                north_in = col + (row * num_columns)
                south_out = col + ((row + 1) * num_columns)
                int_links.append(IntLink(link_id=link_count,
                                         src_node=routers[south_out],
                                         dst_node=routers[north_in],
                                         src_outport="South",
                                         dst_inport="North",
                                         latency = link_latency,
                                         weight=2))
                link_count += 1


    network.int_links = int_links

#------------------------------------------------------------------------------
# main configuration
#------------------------------------------------------------------------------

parser = optparse.OptionParser()
Options.addCommonOptions(parser)
Options.addSEOptions(parser)
Options.addBRGOptions(parser)
Options.addLaneOptions(parser)
Options.addBRGSC3Options(parser)

if '--ruby' in sys.argv:
    Ruby.define_options(parser)

(options, args) = parser.parse_args()

if args:
    print("Error: script doesn't take any positional arguments")
    sys.exit(1)

multiprocesses = []
numThreads = 1

if options.bench:
    apps = options.bench.split("-")
    if len(apps) != options.num_cpus:
        print("number of benchmarks not equal to set num_cpus!")
        sys.exit(1)

    for app in apps:
        try:
            if buildEnv['TARGET_ISA'] == 'alpha':
                exec("workload = %s('alpha', 'tru64', '%s')" % (
                        app, options.spec_input))
            elif buildEnv['TARGET_ISA'] == 'arm':
                exec("workload = %s('arm_%s', 'linux', '%s')" % (
                        app, options.arm_iset, options.spec_input))
            else:
                exec("workload = %s(buildEnv['TARGET_ISA', 'linux', '%s')" % (
                        app, options.spec_input))
            multiprocesses.append(workload.makeProcess())
        except:
            print("Unable to find workload for %s: %s" % (
                    buildEnv['TARGET_ISA'], appi))
            sys.exit(1)
elif options.cmd:
    multiprocesses, numThreads = get_processes(options)
else:
    print("No workload specified. Exiting!\n")
    sys.exit(1)

#----------------------------------------------------------------------------
# @tuan: set up CPUs for --brg-fast-forward option
#
#   If --brg-fast-forward is used, WarmupCPUClass CPUs are used before the
#   main timing region starts. CPUClass CPUs are used within the timing region
#   while CooldownCPUClass CPUs are used after the timing region for
#   verification and cleanup purpose.
#
#----------------------------------------------------------------------------

WarmupCPUClass = None
CPUClass = None
CooldownCPUClass = None
TinyCPUClass = None

if options.brg_fast_forward:
    WarmupCPUClass = AtomicSimpleCPU
    CooldownCPUClass = TimingSimpleCPU

CPUClass, main_mem_mode = Simulation.getCPUClass(options.cpu_type)
TinyCPUClass, tiny_mem_mode = Simulation.getCPUClass(options.tiny_cpu_type)

if options.brg_fast_forward:
    WarmupCPUClass.numThreads = numThreads
    CooldownCPUClass.numThreads = numThreads

CPUClass.numThreads = numThreads

# Check -- do not allow SMT with multiple CPUs
if options.smt and options.num_cpus > 1:
    fatal("You cannot use SMT with multiple CPUs!")

np = options.num_cpus

# select a CPU class used to start the simulation
FirstCPUClass = WarmupCPUClass if options.brg_fast_forward else CPUClass

if options.num_main_cpus == -1:
  options.num_main_cpus = np

assert(np == options.num_main_cpus + options.num_tiny_cpus)

cpu_classes = []
for i in xrange(options.num_main_cpus):
  cpu_classes.append(FirstCPUClass)
for i in xrange(options.num_tiny_cpus):
  cpu_classes.append(TinyCPUClass)

system = System(cpu = [cpu_classes[i](cpu_id=i) for i in xrange(np)],
                mem_mode = FirstCPUClass.memory_mode(),
                mem_ranges = [AddrRange(options.mem_size)],
                cache_line_size = options.cacheline_size)

if numThreads > 1:
    system.multi_thread = True

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

# All cpus belong to a common cpu_clk_domain, therefore running at a common
# frequency.
for cpu in system.cpu:
    cpu.clk_domain = system.cpu_clk_domain

for i in xrange(np):
    if options.smt:
        system.cpu[i].workload = multiprocesses
    elif len(multiprocesses) == 1:
        system.cpu[i].workload = multiprocesses[0]
    else:
        system.cpu[i].workload = multiprocesses[i]

    if options.simpoint_profile:
        system.cpu[i].addSimPointProbe(options.simpoint_interval)

    if options.checker:
        system.cpu[i].addCheckerCpu()

    system.cpu[i].createThreads()

if options.ruby:
    Ruby.create_system(options, False, system)
    assert(options.num_cpus == len(system.ruby._cpu_ports))

    system.ruby.clk_domain = SrcClockDomain(clock = options.ruby_clock,
                                        voltage_domain = system.voltage_domain)
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

for cpu in system.cpu:
  cpu.activity_trace = options.activity_trace

# Set brg fast-forward for the system
if options.brg_fast_forward:
    system.brg_fast_forward = True

if options.active_message_network and np >= 2:
  #----------------------------------------------------------------------------
  # construct active message network
  #----------------------------------------------------------------------------

  ruby = RubySystem()
  ruby.num_of_sequencers = 0
  ruby.number_of_virtual_networks = 2

  system.ruby_am = ruby

  am_network = SimpleNetwork( ruby_system = ruby,
                              routers = [],
                              ext_links = [],
                              int_links = [],
                              netifs = [],
                              number_of_virtual_networks = 2,
                              is_active_msg_network = True)

  #
  # construct adapters
  #

  adapters = []
  for i in xrange(np):
    adapter = NetworkAdapter(version = i, ruby_system = ruby)

    # connect adapter and the network
    adapter.cpuReqBuffer            = MessageBuffer(ordered = True)
    adapter.cpuReqBuffer.master     = am_network.slave

    adapter.networkRespBuffer       = MessageBuffer(ordered = True)
    adapter.networkRespBuffer.slave = am_network.master

    adapter.networkReqBuffer        = MessageBuffer(ordered = True)
    adapter.networkReqBuffer.slave  = am_network.master

    adapter.cpuRespBuffer           = MessageBuffer(ordered = True)
    adapter.cpuRespBuffer.master    = am_network.slave

    adapters.append(adapter)

  system.adapters = adapters

  #
  # construct Mesh_XY topology
  #

  makeActiveMsgNetworkTopology(adapters, am_network, SimpleIntLink, \
                                SimpleExtLink, Switch)

  #
  # init network
  #

  am_network.buffer_size = 0  # infinite size
  am_network.setup_buffers()

  system.am_network = am_network

  #
  # connect CPUs to adapters
  #

  for i in xrange(np):
    system.cpu[i].out_nw_req_port = adapters[i].cpu_req_port
    adapters[i].network_req_port  = system.cpu[i].in_nw_req_port

#------------------------------------------------------------------------------
# instantiate system
#------------------------------------------------------------------------------

root = Root(full_system = False, system = system)

# Run simulation

if options.brg_fast_forward:
    Simulation.run_brg(options, root, system, CPUClass, CooldownCPUClass)
else:
    Simulation.run_brg(options, root, system, None)
