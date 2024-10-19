# Copyright (c) 2006-2007 The Regents of The University of Michigan
# Copyright (c) 2009 Advanced Micro Devices, Inc.
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
# Authors: Brad Beckmann

import math
import m5
from m5.objects import *
from m5.defines import buildEnv
from Ruby import create_topology, create_directories
from Ruby import send_evicts

#
# Declare caches used by the protocol
#
class L1Cache(RubyCache): pass
class L2Cache(RubyCache): pass

def define_options(parser):
  return

def create_system(options, full_system, system, dma_ports,
                  bootmem, ruby_system):

  if buildEnv['PROTOCOL'] != 'SC3_Two_Level_WT':
    panic("This script requires the SC3_Two_Level_WT protocol to be built.")

  cpu_sequencers = []

  #
  # The ruby network creation expects the list of nodes in the system to
  # be consistent with the NetDest list.  Therefore the l1 controller
  # nodes must be listed before the directory nodes and directory nodes
  # before dma nodes, etc.
  #
  sc3_cntrl_nodes = []
  l2_cntrl_nodes  = []

  #
  # Must create the individual controllers before the network to ensure
  # the controller constructors are called before the network constructor
  #
  l2_bits         = int(math.log(options.num_l2caches, 2))
  block_size_bits = int(math.log(options.cacheline_size, 2))

  for i in xrange(options.num_cpus):
    #
    # First create the Ruby objects associated with this cpu
    #
    l1i_cache = L1Cache(size = options.l1i_size,
                        assoc = options.l1i_assoc,
                        start_index_bit = block_size_bits,
                        is_icache = True)

    l1d_cache = L1Cache(size = options.l1d_size,
                        assoc = options.l1d_assoc,
                        start_index_bit = block_size_bits,
                        is_icache = False)

    # the ruby random tester reuses num_cpus to specify the number of cpu
    # ports connected to the tester object, which is stored in
    # system.cpu. because there is only ever one tester object, num_cpus
    # is not necessarily equal to the size of system.cpu; therefore if
    # len(system.cpu) == 1 we use system.cpu[0] to set the clk_domain,
    # thereby ensuring we don't index off the end of the cpu list.
    if len(system.cpu) == 1:
      clk_domain = system.cpu[0].clk_domain
    else:
      clk_domain = system.cpu[i].clk_domain

    sc3_cntrl = SC3_Controller(version = i, L1Icache = l1i_cache,
                               L1Dcache = l1d_cache,
                               l2_select_num_bits = l2_bits,
                               ruby_system = ruby_system,
                               clk_domain = clk_domain,
                               send_evictions=send_evicts(options),
                               transitions_per_cycle = \
                                   options.num_l1_cache_ports)

    cpu_seq = SC3L2SequencerWT(version = i, icache = l1i_cache,
                               dcache = l1d_cache, clk_domain = clk_domain,
                               ruby_system = ruby_system, coreid=i)

    sc3_cntrl.sequencer = cpu_seq
    exec("ruby_system.sc3_cntrl%d = sc3_cntrl" % i)

    # Add controllers and sequencers to the appropriate lists
    cpu_sequencers.append(cpu_seq)
    sc3_cntrl_nodes.append(sc3_cntrl)

    # Connect the L1 controllers and the network
    sc3_cntrl.mandatoryQueue = MessageBuffer()
    sc3_cntrl.requestFromCache = MessageBuffer(ordered = True)
    sc3_cntrl.requestFromCache.master = ruby_system.network.slave

    sc3_cntrl.responseToCache = MessageBuffer(ordered = True)
    sc3_cntrl.responseToCache.slave = ruby_system.network.master

  l2_index_start = block_size_bits + l2_bits

  for i in xrange(options.num_l2caches):
    #
    # First create the Ruby objects associated with this cpu
    #
    l2_cache = L2Cache(size = options.l2_size,
                       assoc = options.l2_assoc,
                       start_index_bit = l2_index_start)

    l2_cntrl = L2Cache_Controller(version = i,
                                  L2cache = l2_cache,
                                  transitions_per_cycle = options.ports,
                                  ruby_system = ruby_system)

    exec("ruby_system.l2_cntrl%d = l2_cntrl" % i)
    l2_cntrl_nodes.append(l2_cntrl)

    # Connect the L2 controllers and the network
    l2_cntrl.DirRequestFromL2Cache = MessageBuffer()
    l2_cntrl.DirRequestFromL2Cache.master = ruby_system.network.slave
    l2_cntrl.L1RequestFromL2Cache = MessageBuffer()
    l2_cntrl.L1RequestFromL2Cache.master = ruby_system.network.slave
    l2_cntrl.responseFromL2Cache = MessageBuffer()
    l2_cntrl.responseFromL2Cache.master = ruby_system.network.slave

    l2_cntrl.unblockToL2Cache = MessageBuffer()
    l2_cntrl.unblockToL2Cache.slave = ruby_system.network.master
    l2_cntrl.L1RequestToL2Cache = MessageBuffer(ordered = True)
    l2_cntrl.L1RequestToL2Cache.slave = ruby_system.network.master
    l2_cntrl.responseToL2Cache = MessageBuffer()
    l2_cntrl.responseToL2Cache.slave = ruby_system.network.master

    l2_cntrl.triggerQueue = MessageBuffer()

  phys_mem_size = sum(map(lambda r: r.size(), system.mem_ranges))
  assert(phys_mem_size % options.num_dirs == 0)
  mem_module_size = phys_mem_size / options.num_dirs

  # Run each of the ruby memory controllers at a ratio of the frequency of
  # the ruby system.
  # clk_divider value is a fix to pass regression.
  ruby_system.memctrl_clk_domain = DerivedClockDomain(
    clk_domain=ruby_system.clk_domain,
    clk_divider=3)

  mem_dir_cntrl_nodes, rom_dir_cntrl_node = create_directories(
    options, bootmem, ruby_system, system)
  dir_cntrl_nodes = mem_dir_cntrl_nodes[:]
  if rom_dir_cntrl_node is not None:
    dir_cntrl_nodes.append(rom_dir_cntrl_node)

  for dir_cntrl in dir_cntrl_nodes:
    # Connect the directory controllers and the network
    dir_cntrl.requestToDir = MessageBuffer()
    dir_cntrl.requestToDir.slave = ruby_system.network.master
    dir_cntrl.responseToDir = MessageBuffer()
    dir_cntrl.responseToDir.slave = ruby_system.network.master
    dir_cntrl.responseFromDir = MessageBuffer()
    dir_cntrl.responseFromDir.master = ruby_system.network.slave
    dir_cntrl.responseFromMemory = MessageBuffer()

  assert len(dma_ports) == 0

  all_cntrls = sc3_cntrl_nodes + l2_cntrl_nodes + dir_cntrl_nodes

  # Create the io controller and the sequencer
  if full_system:
    panic("This protocol does not support full system mode.")

  ruby_system.network.number_of_virtual_networks = 3
  topology = create_topology(all_cntrls, options)
  return (cpu_sequencers, dir_cntrl_nodes, topology)
