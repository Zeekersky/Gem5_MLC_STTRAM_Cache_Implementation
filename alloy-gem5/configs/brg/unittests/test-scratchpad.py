#------------------------------------------------------------------------------
# test-scratchpad.py
#------------------------------------------------------------------------------
#
# Configuration for scratchpad unit test
#
# Author: Tuan Ta
# Date  : 19/07/02

import optparse
import sys
import os
import math

import m5
from m5.defines import buildEnv
from m5.objects import *
from m5.util import addToPath, fatal, warn

addToPath('../..')

from ruby import Ruby
from common import Options

#------------------------------------------------------------------------------
# make network topology
#------------------------------------------------------------------------------

def makeNetworkTopology(nodes, network, IntLink, ExtLink, Router):
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
Ruby.define_options(parser)

(options, args) = parser.parse_args()

num_scratchpads = 2

# create the system we are going to simulate
system = System()

# Set the clock fequency of the system (and all of its children)
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

# Set up the system
system.mem_mode = 'timing'               # Use timing accesses
system.mem_ranges = [AddrRange('512MB')] # Create an address range

# Create a test driver
system.test_harness = TestScratchpadHarness()

# system.system_port is required to be connected to a slave port
# here we choose to connect it the system_port in the test_harness
system.test_harness.system_port = system.system_port
system.test_harness.num_test_ports = num_scratchpads

#
# Construct memory system
#

system.ruby = RubySystem()
system.ruby.num_of_sequencers = 0
system.ruby.number_of_virtual_networks = 2

# Network
network = SimpleNetwork(ruby_system = system.ruby,
                        routers = [],
                        ext_links = [],
                        int_links = [],
                        netifs = [],
                        number_of_virtual_networks = 2)

# Scratchpads
scratchpads = []
for i in xrange(num_scratchpads):
  sp = Scratchpad(version = i, ruby_system = system.ruby)

  sp.memReqBuffer             = MessageBuffer(ordered = True)
  sp.memReqBuffer.master      = network.slave

  sp.memRespBuffer            = MessageBuffer(ordered = True)
  sp.memRespBuffer.slave      = network.master

  sp.remoteReqBuffer          = MessageBuffer(ordered = True)
  sp.remoteReqBuffer.slave    = network.master

  sp.remoteRespBuffer         = MessageBuffer(ordered = True)
  sp.remoteRespBuffer.master  = network.slave

  scratchpads.append(sp)

system.scratchpads = scratchpads

# L2 cache
l2_cntrls = []
l2_cache = RubyCache(size = '256B', assoc = 2)
l2_cntrl = L2Cache_Controller(version = 0,
                              cacheMemory = l2_cache,
                              transitions_per_cycle = options.ports,
                              ruby_system = system.ruby)

l2_cntrl.requestToLLC           = MessageBuffer(ordered = True)
l2_cntrl.requestToLLC.slave     = network.master

l2_cntrl.responseFromLLC        = MessageBuffer(ordered = True)
l2_cntrl.responseFromLLC.master = network.slave

l2_cntrl.responseFromMemory     = MessageBuffer(ordered = True)

l2_cntrls.append(l2_cntrl)
system.l2_cntrls = l2_cntrls

#
# Construct network
#

all_cntrls = system.scratchpads + system.l2_cntrls

makeNetworkTopology(all_cntrls,
                    network,
                    SimpleIntLink,
                    SimpleExtLink,
                    Switch)

#
# Init network
#

network.buffer_size = 0   # infinite size
network.setup_buffers()
system.network = network

#
# Connect test harness to scratchpads
#

for i in xrange(num_scratchpads):
  system.scratchpads[i].cpu_port = system.test_harness.test_ports[i]

#
# Create and connect to memory controller
#

system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

system.mem_ctrl = DDR3_1600_8x8()
system.mem_ctrl.range = system.mem_ranges[0]
system.mem_ctrl.port = l2_cntrl.memory


#------------------------------------------------------------------------------
# Instantiate system
#------------------------------------------------------------------------------

# set up the root SimObject and start the simulation
root = Root(full_system = False, system = system)

# instantiate all of the objects we've created above
m5.instantiate()

print("Beginning simulation!")
exit_event = m5.simulate()
print('Exiting @ tick %i because %s' % (m5.curTick(), exit_event.getCause()))
