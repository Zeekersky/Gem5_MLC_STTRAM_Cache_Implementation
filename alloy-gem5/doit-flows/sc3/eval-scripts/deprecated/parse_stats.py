#!/usr/bin/env python
#==============================================================================
# parse-stats.py
#==============================================================================
# Parse gem5 stats
#
# Author  : Tuan Ta
# Date    : 19/04/09

from __future__ import print_function

import os
import re
import json
import argparse

#------------------------------------------------------------------------------
# Common variables
#------------------------------------------------------------------------------

parser = argparse.ArgumentParser(description="Parse all stats in simout folder into a single JSON")
parser.add_argument('-i', '--input-dir', help="Input simout directory", default="./simout")
parser.add_argument('-o', '--output-file', help="Output JSON", default="all-stats.json")
args = parser.parse_args()

if not os.path.isdir(args.input_dir):
  print("Input directory (%s) does not exist" % args.input_dir)
  exit(1)

simout_dir = os.path.abspath(args.input_dir)
sim_list = os.listdir(simout_dir)

regex_dict = {
                "sim-ticks"       : re.compile(r'^sim_ticks'),
                "sim-insts"       : re.compile(r'^sim_insts'),
                "runtime-cycles"  : re.compile(r'main_cpu\d*\.appl_runtime_cycles'),
                "task-cycles"     : re.compile(r'main_cpu\d*\.in_task_cycles'),

               # network stats
               "getx-count"            : re.compile(r'coh_msg_count::GETX '),
               "upgrade-count"         : re.compile(r'coh_msg_count::UPGRADE '),
               "gets-count"            : re.compile(r'coh_msg_count::GETS '),
               "get_ins-count"         : re.compile(r'coh_msg_count::GET_INSTR'),
               "inv-count"             : re.compile(r'coh_msg_count::INV '),
               "putx-count"            : re.compile(r'coh_msg_count::PUTX '),
               "unlock-count"          : re.compile(r'coh_msg_count::UNLOCK '),
               "mem_ack-count"         : re.compile(r'coh_msg_count::MEMORY_ACK'),
               "data-count"            : re.compile(r'coh_msg_count::DATA '),
               "data_exc-count"        : re.compile(r'coh_msg_count::DATA_EXCLUSIVE'),
               "mem_data-count"        : re.compile(r'coh_msg_count::MEMORY_DATA'),
               "ack-count"             : re.compile(r'coh_msg_count::ACK '),
               "wb_ack-count"          : re.compile(r'coh_msg_count::WB_ACK '),
               "unblock-count"         : re.compile(r'coh_msg_count::UNBLOCK '),
               "exc_unblock-count"     : re.compile(r'coh_msg_count::EXCLUSIVE_UNBLOCK'),
               "atomic-count"          : re.compile(r'coh_msg_count::ATOMIC '),
               "atomic_resp-count"     : re.compile(r'coh_msg_count::ATOMIC_RESP'),
               "ll-count"              : re.compile(r'coh_msg_count::LL '),
               "sc_success-count"      : re.compile(r'coh_msg_count::SC_SUCCESS'),
               "sc_failure-count"      : re.compile(r'coh_msg_count::SC_FAILED'),
               "sc-count"              : re.compile(r'coh_msg_count::SC '),
               "getv-count"            : re.compile(r'coh_msg_count::GETV '),
               "putv-count"            : re.compile(r'coh_msg_count::PUTV '),

               "getx-bytes"            : re.compile(r'coh_msg_bytes::GETX '),
               "upgrade-bytes"         : re.compile(r'coh_msg_bytes::UPGRADE '),
               "gets-bytes"            : re.compile(r'coh_msg_bytes::GETS '),
               "get_ins-bytes"         : re.compile(r'coh_msg_bytes::GET_INSTR'),
               "inv-bytes"             : re.compile(r'coh_msg_bytes::INV '),
               "putx-bytes"            : re.compile(r'coh_msg_bytes::PUTX '),
               "unlock-bytes"          : re.compile(r'coh_msg_bytes::UNLOCK '),
               "mem_ack-bytes"         : re.compile(r'coh_msg_bytes::MEMORY_ACK'),
               "data-bytes"            : re.compile(r'coh_msg_bytes::DATA '),
               "data_exc-bytes"        : re.compile(r'coh_msg_bytes::DATA_EXCLUSIVE'),
               "mem_data-bytes"        : re.compile(r'coh_msg_bytes::MEMORY_DATA'),
               "ack-bytes"             : re.compile(r'coh_msg_bytes::ACK '),
               "wb_ack-bytes"          : re.compile(r'coh_msg_bytes::WB_ACK'),
               "unblock-bytes"         : re.compile(r'coh_msg_bytes::UNBLOCK '),
               "exc_unblock-bytes"     : re.compile(r'coh_msg_bytes::EXCLUSIVE_UNBLOCK'),
               "atomic-bytes"          : re.compile(r'coh_msg_bytes::ATOMIC '),
               "atomic_resp-bytes"     : re.compile(r'coh_msg_bytes::ATOMIC_RESP'),
               "ll-bytes"              : re.compile(r'coh_msg_bytes::LL'),
               "sc_success-bytes"      : re.compile(r'coh_msg_bytes::SC_SUCCESS'),
               "sc_failure-bytes"      : re.compile(r'coh_msg_bytes::SC_FAILED'),
               "sc-bytes"              : re.compile(r'coh_msg_bytes::SC '),
               "getv-bytes"            : re.compile(r'coh_msg_bytes::GETV '),
               "putv-bytes"            : re.compile(r'coh_msg_bytes::PUTV '),

               "num-cycles"    : re.compile(r'main_cpu\d*\.numCycles'),
               "unique-insts"  : re.compile(r'main_cpu\d*\.fetch\.uniqueInstCount'),
               "total-insts"   : re.compile(r'main_cpu\d*\.fetch\.totalInstCount'),
             }

#------------------------------------------------------------------------------
# Extract value from a stat line
#------------------------------------------------------------------------------
# A typical gem5 statistic line looks like this
#   [stat-name]    [stat-val]    [stat-comment]

def extract_val( line ):
  return re.split( r"\s+", line )[ 1 ]

#------------------------------------------------------------------------------
# Extract sim name
#------------------------------------------------------------------------------
# extract config-name and app-input
# sim-name format
#     sim-[config-name]-[app-suite]-[app-name]-[runtime]-[input-group]-[idx]

def extract_sim_name( sim ):
  input_name  = "-".join( sim.split("-")[ -2:    ] )   # [input-group]-[idx]
  runtime     = "-".join( sim.split("-")[ -3: -2 ] )   # [runtime]
  app         = "-".join( sim.split("-")[ -5: -3 ] )   # [app-name]
  config_name = "-".join( sim.split("-")[ 0 : -6 ] )   # [config-name]

  return config_name, runtime, app, input_name

#------------------------------------------------------------------------------
# Loop through all simulations
#------------------------------------------------------------------------------

#
# stat_dict: { stat_name : { config-name : { runtime : { app : { input: [ val_0, val_1, ... ] } } } } }
#

stat_dict = {}

for stat in regex_dict:

  pattern = regex_dict[ stat ]
  stat_dict[ stat ] = {}

  for sim in sim_list:
    stat_file = "/".join( [ simout_dir, sim, "stats.txt" ] )

    if not os.path.isfile( stat_file ):
      print("No stats.txt for {}".format( sim ))
      continue

    config, runtime, app, inp = extract_sim_name( sim )

    if config not in stat_dict[ stat ]:
      stat_dict[ stat ][ config ] = {}

    if runtime not in stat_dict[ stat ][ config ]:
      stat_dict[ stat ][ config ][ runtime ] = {}

    if app not in stat_dict[ stat ][ config ][ runtime ]:
      stat_dict[ stat ][ config ][ runtime ][ app ] = {}

    if inp not in stat_dict[ stat ][ config ][ runtime ][ app ]:
      stat_dict[ stat ][ config ][ runtime ][ app ][ inp ] = []

    with open(stat_file, "r") as f:
      for line in f.readlines():
        match = re.search( pattern, line )
        if match:
          stat_dict[ stat ][ config ][ runtime ][ app ][ inp ].append( extract_val( line ) )

with open(args.output_file, "w") as f:
  json.dump( stat_dict, f, sort_keys = True, indent = 4 )
