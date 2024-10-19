#!/usr/bin/env python
#==============================================================================
# network traffic stacked bar plot
#==============================================================================
#
# Author: Tuan Ta
# Date  : 19/08/07

from __future__ import print_function

import os
import re
import subprocess
import math
import json
import argparse

import matplotlib as mpl
mpl.use('Agg')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

from app_config_list import *
from common.stats_to_dict import *
from common.make_stacked_bar_plot import make_stacked_bar_plot

# traffic categories
traffic_cat = [ "cpu_req", "data_resp", "wb_req",
                "sync_req", "sync_resp",
                "dram_req", "dram_resp",
                "coh_req", "coh_resp" ]

traffic_breakdown = {
                # stat_name         # category
                "getx"            : "cpu_req",
                "gets"            : "cpu_req",
                "get_ins"         : "cpu_req",
                "getv"            : "cpu_req",

                "data"            : "data_resp",
                "data_exc"        : "data_resp",

                "putx"            : "wb_req",
                "putv"            : "wb_req",

                "atomic"          : "sync_req",
                "ll"              : "sync_req",
                "sc"              : "sync_req",

                "atomic_resp"     : "sync_resp",
                "sc_success"      : "sync_resp",
                "sc_failure"      : "sync_resp",

                "mem_data"        : "dram_req",
                "mem_ack"         : "dram_resp",

                "upgrade"         : "coh_req",
                "inv"             : "coh_req",
                "unlock"          : "coh_req",
                "unblock"         : "coh_req",
                "exc_unblock"     : "coh_req",

                "ack"             : "coh_resp",
                "wb_ack"          : "coh_resp",
              }

stats_name_dict = {
  # network stats
  "getx-count"            : 'coh_msg_count::GETX',
  "upgrade-count"         : 'coh_msg_count::UPGRADE',
  "gets-count"            : 'coh_msg_count::GETS',
  "get_ins-count"         : 'coh_msg_count::GET_INSTR',
  "inv-count"             : 'coh_msg_count::INV',
  "putx-count"            : 'coh_msg_count::PUTX',
  "unlock-count"          : 'coh_msg_count::UNLOCK',
  "mem_ack-count"         : 'coh_msg_count::MEMORY_ACK',
  "data-count"            : 'coh_msg_count::DATA',
  "data_exc-count"        : 'coh_msg_count::DATA_EXCLUSIVE',
  "mem_data-count"        : 'coh_msg_count::MEMORY_DATA',
  "ack-count"             : 'coh_msg_count::ACK',
  "wb_ack-count"          : 'coh_msg_count::WB_ACK',
  "unblock-count"         : 'coh_msg_count::UNBLOCK',
  "exc_unblock-count"     : 'coh_msg_count::EXCLUSIVE_UNBLOCK',
  "atomic-count"          : 'coh_msg_count::ATOMIC',
  "atomic_resp-count"     : 'coh_msg_count::ATOMIC_RESP',
  "ll-count"              : 'coh_msg_count::LL',
  "sc_success-count"      : 'coh_msg_count::SC_SUCCESS',
  "sc_failure-count"      : 'coh_msg_count::SC_FAILED',
  "sc-count"              : 'coh_msg_count::SC',
  "getv-count"            : 'coh_msg_count::GETV',
  "putv-count"            : 'coh_msg_count::PUTV',
  "getx-bytes"            : 'coh_msg_bytes::GETX',
  "upgrade-bytes"         : 'coh_msg_bytes::UPGRADE',
  "gets-bytes"            : 'coh_msg_bytes::GETS',
  "get_ins-bytes"         : 'coh_msg_bytes::GET_INSTR',
  "inv-bytes"             : 'coh_msg_bytes::INV',
  "putx-bytes"            : 'coh_msg_bytes::PUTX',
  "unlock-bytes"          : 'coh_msg_bytes::UNLOCK',
  "mem_ack-bytes"         : 'coh_msg_bytes::MEMORY_ACK',
  "data-bytes"            : 'coh_msg_bytes::DATA',
  "data_exc-bytes"        : 'coh_msg_bytes::DATA_EXCLUSIVE',
  "mem_data-bytes"        : 'coh_msg_bytes::MEMORY_DATA',
  "ack-bytes"             : 'coh_msg_bytes::ACK',
  "wb_ack-bytes"          : 'coh_msg_bytes::WB_ACK',
  "unblock-bytes"         : 'coh_msg_bytes::UNBLOCK',
  "exc_unblock-bytes"     : 'coh_msg_bytes::EXCLUSIVE_UNBLOCK',
  "atomic-bytes"          : 'coh_msg_bytes::ATOMIC',
  "atomic_resp-bytes"     : 'coh_msg_bytes::ATOMIC_RESP',
  "ll-bytes"              : 'coh_msg_bytes::LL',
  "sc_success-bytes"      : 'coh_msg_bytes::SC_SUCCESS',
  "sc_failure-bytes"      : 'coh_msg_bytes::SC_FAILED',
  "sc-bytes"              : 'coh_msg_bytes::SC',
  "getv-bytes"            : 'coh_msg_bytes::GETV',
  "putv-bytes"            : 'coh_msg_bytes::PUTV',
}

# stat_dict: { stat : { config : { runtime : { app : { data_set : [ value ] } } } } }

parser = argparse.ArgumentParser(description="Create network traffic plot")
parser.add_argument('-i', '--input-dir', help="Input simout directory", default="../results-latest")
parser.add_argument('-o', '--output-file', help="Output plot", default="fig-tiny-nw-traffic-stacked-bar.png")
args = parser.parse_args()

if not os.path.isdir(args.input_dir):
  print("Input directory (%s) does not exist" % args.input_dir)
  exit(1)

simout_dir = os.path.abspath(args.input_dir)

# { app : { config : { cat : value } } }

msg_count_dict = {}
for app in app_list:
  msg_count_dict[app] = {}
  for config in config_list_tiny:
    msg_count_dict[app][config] = {}
    for cat in traffic_cat:
      msg_count_dict[app][config][cat] = 0

for app in app_list:
  for config in config_list_tiny:

    prefix   = dir_name_dict[config][0]
    runtime  = dir_name_dict[config][1]
    dir_name = os.path.join(simout_dir, prefix + '-x-' + app + '-' + runtime+ '-' + dataset)
    stats_file = os.path.join(dir_name, "stats.txt")

    if os.path.isfile(stats_file):
      stat_dict = stats_to_dict(stats_file)
    else:
      print("%s does not exist" % stats_file)
      continue

    for stat in traffic_breakdown:
      cat = traffic_breakdown[stat]
      assert( cat in traffic_cat )

      if cat not in msg_count_dict[app][config]:
        msg_count_dict[app][config][cat] = 0
      if stats_name_dict[stat+'-bytes'] in stat_dict:
        val = stat_dict[stats_name_dict[stat+'-bytes']]
        msg_count_dict[app][config][cat] += int(val)

# transform the format to array format
# { app : [ [ configs ], [ control/data ], [ value ] ] }

msg_count_array = { }

for app in app_list:
  msg_count_array[ app ] = [ [], [], [] ]
  for config in msg_count_dict[ app ]:
    for cat in traffic_cat:
      msg_count_array[ app ][ 0 ].append( config )
      msg_count_array[ app ][ 1 ].append( cat )
      msg_count_array[ app ][ 2 ].append( msg_count_dict[ app ][ config ][ cat ] )

# create plot

fig, axes = plt.subplots(figsize=(2*len(app_list), 10),
                         nrows=1, ncols=len(app_list),
                         sharey=True)

for i, app in enumerate(app_list):
  make_stacked_bar_plot(msg_count_array[app],
                        ["config", "category", "value"],
                        fig, axes[i],
                        app, "config", "value")

axes[0].set_ylabel("Network Traffic (in Bytes)")
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='lower right')

plt.savefig(args.output_file)
