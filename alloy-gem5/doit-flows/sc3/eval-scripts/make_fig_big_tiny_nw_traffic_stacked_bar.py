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
# mpl.use('Agg')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

from app_config_list import *
from common.stats_to_dict import *

# This assumes data is organized as an array of three arrays
# [ [ 'group' ], [ 'sub_group' ], [ 'value' ] ]

def make_stacked_bar_plot( data, headers, fig, ax, title, x_label, y_label ):
  assert( len( data ) == 3 )
  ax.grid(zorder=0)
  colors = [
    "#e41a1c",
    "#377eb8",
    "#4daf4a",
    "#984ea3",
    "#ff7f00",
    "#ffff33",
    "#a65628",
    "#f781bf",
    "#999999",
  ]

  rows = zip( data[0], data[1], data[2] )
  df = pd.DataFrame( rows, columns = headers )

  sub_groups = df[ headers[ 1 ] ].drop_duplicates()
  margin_bottom = np.zeros( len( df[ headers[ 0 ] ].drop_duplicates() ) )

  for num, sub_group in enumerate( sub_groups ):
    values = list( df[ df[ headers[ 1 ] ] == sub_group ].loc[ :, headers[ 2 ] ] )

    df[ df[ headers[1] ] == sub_group ].plot.bar( title = title,
                                                  x = x_label,
                                                  y = y_label,
                                                  ax = ax,
                                                  stacked = True,
                                                  bottom = margin_bottom,
                                                  color = colors[ num ],
                                                  label = sub_group,
                                                  legend = False,
                                                  edgecolor='black',
                                                  zorder=3 )
    margin_bottom += values

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
parser.add_argument('-o', '--output-file', help="Output plot", default="fig-big-tiny-nw-traffic-stacked-bar.pdf")
args = parser.parse_args()

if not os.path.isdir(args.input_dir):
  print("Input directory (%s) does not exist" % args.input_dir)
  exit(1)

simout_dir = os.path.abspath(args.input_dir)

# { app : { config : { cat : value } } }

msg_count_dict = {}
for app in app_list:
  msg_count_dict[app] = {}
  for config in config_list_big_tiny:
    msg_count_dict[app][config] = {}

for app in app_list:
  for config in config_list_big_tiny:

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

# normalize to total of MESI
norm_value = {}
for app in app_list:
  norm_value[app] = 0
  for cat in msg_count_dict[app][config_list_big_tiny[0]]:
    norm_value[app] += msg_count_dict[app][config_list_big_tiny[0]][cat]

# transform the format to array format
# { app : [ [ configs ], [ control/data ], [ value ] ] }

msg_count_array = { }

for app in app_list:
  msg_count_array[ app ] = [ [], [], [] ]
  for config in config_list_big_tiny:
    for cat in traffic_cat:
      msg_count_array[ app ][ 0 ].append( config )
      msg_count_array[ app ][ 1 ].append( cat )
      if cat in msg_count_dict[ app ][ config ]:
        msg_count_array[ app ][ 2 ].append( float(msg_count_dict[ app ][ config ][ cat ] ) / norm_value[app] )
      else:
        msg_count_array[ app ][ 2 ].append(0)

# create plot

font = {'family' : 'Times New Roman',
        'size'   : 15}
matplotlib.rc('font', **font)

fig, axes = plt.subplots(figsize=(20, 4),
                         nrows=1, ncols=len(app_list),
                         sharey=True)

for i, app in enumerate(app_list):
  ax = axes[i]
  make_stacked_bar_plot(msg_count_array[app],
                        ["config", "category", "value"],
                        fig, ax,
                        app, "config", "value")

  ax.grid(which='both', linestyle='-', linewidth='0.5', axis='y')
  ax.spines['right'].set_visible(False)
  ax.spines['top'].set_visible(False)

  # group label
  labels = [item.get_text() for item in ax.get_xticklabels()]
  ticks  = xtickslocs = ax.get_xticks()
  assert(len(labels) == len(ticks))
  # cut-off
  ax.set_ylim(0, 4)
  ymin, _  = ax.get_ylim()
  group_xs = {}

  for i in range(len(labels)):
    label = labels[i]
    tick = ticks[i]
    l = label.rsplit('-', 1)
    group = ''
    if len(l) > 1:
      group     = l[0]
      labels[i] = l[1]
    if group != '':
      if group not in group_xs:
        group_xs[group] = [tick]
      else:
        group_xs[group].append(tick)

  for group in group_xs:
    xs = group_xs[group]
    x_pos = float(sum(xs)) / float(len(xs))
    group = group.replace('-', '\n')
    ax.text(x_pos, ymin - 0.9, group, ha='center', va='center')
  ax.set_xticklabels(labels)
  ax.set_xlabel('')

axes[0].set_ylabel("Normalized Network Traffic")
handles, labels = axes[0].get_legend_handles_labels()
lgd = axes[ len(axes) / 2 ].legend(handles, labels, loc='lower center', ncol=len(traffic_cat),
                                   frameon=False, bbox_to_anchor=(0.5, -0.45))

plt.savefig(args.output_file, bbox_extra_artists=(lgd,), bbox_inches="tight")
