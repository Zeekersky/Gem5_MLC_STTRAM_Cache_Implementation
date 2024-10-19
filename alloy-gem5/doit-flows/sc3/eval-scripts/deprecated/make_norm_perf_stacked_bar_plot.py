#!/usr/bin/env python
#==============================================================================
# make normalized performance stacked bar plot
#==============================================================================
#

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

from common.stats_to_dict import stats_to_dict
from common.get_sum import get_sum

#-------------------------------------------------------------------------
# lists
#-------------------------------------------------------------------------

app_list = [
  "cilk5-cs",
  "cilk5-lu",
  "cilk5-mm",
  "cilk5-mt",
  "cilk5-nq",
  "ligra-bc",
  "ligra-bf",
  "ligra-bfs",
  "ligra-bfsbv",
  "ligra-cc",
  "ligra-mis",
  "ligra-radii",
  "ligra-tc",
]

config_list = [
  "big-tiny-mesi",
  "big-tiny-nope",
  "big-tiny-nope-am",
  # "mesi-sc3",
  # "denovo",
  # "nope",
  # "denovo-am",
  # "nope-am",
  # "nope-am-tbiw",
]

dataset = "small-0"

runtimes = {
  "mesi"         : "applrts",
  "mesi-sc3"     : "applrts_sc3",
  "denovo"       : "applrts_sc3",
  "nope"         : "applrts_sc3",
  "denovo-am"    : "applrts_sc3_am",
  "nope-am"      : "applrts_sc3_am",
  "nope-am-tbiw" : "applrts_sc3_am_level",
  "mesi-new"     : "applrts",
  "big-tiny-mesi": "applrts",
  "big-tiny-nope": "applrts_sc3",
  "big-tiny-nope-am": "applrts_sc3_am",
}

categories = [
  "total",
  # "in_task",
  # "in_runtime",
  # "other"
]

num_cores = 64

def add_stats(data, app, config, stat_dict):
  if "system" in stat_dict:
    data[app][config]["total"]      = get_sum(stat_dict["system"], "numCycles", num_cores)
    # data[app][config]["in_runtime"] = get_sum(stat_dict["system"], "in_runtime_cycles", num_cores)
    # data[app][config]["in_task"]    = get_sum(stat_dict["system"], "in_task_cycles", num_cores)
    # data[app][config]["other"]      = data[app][config]["total"] - data[app][config]["in_task"] - data[app][config]["in_runtime"]
  return data

#-------------------------------------------------------------------------
# command-line options
#-------------------------------------------------------------------------

parser = argparse.ArgumentParser(description="Create network traffic plot")
parser.add_argument('-i', '--input-dir', help="Input simout directory", default="./simout")
parser.add_argument('-o', '--output-file', help="Output plot", default="plot-norm-perf-stacked-bar.png")
args = parser.parse_args()

if not os.path.isdir(args.input_dir):
  print("Input directory (%s) does not exist" % args.input_dir)
  exit(1)

simout_dir = os.path.abspath(args.input_dir)

#-------------------------------------------------------------------------
# collect data
#-------------------------------------------------------------------------
# data format:
# {
#   "app" : {
#     "config" : {
#       "total_cycles" : 0
#     }
#   }
# }

data = {}

# initialize

for app in app_list:
  data[app] = {}
  for config in config_list:
    data[app][config] = {}
    for cat in categories:
      data[app][config][cat] = 0

for app in app_list:
  for config in config_list:
    dir_name = config + '-x-' + app + '-' + runtimes[config] + '-' + dataset
    dir_name = os.path.join(simout_dir, dir_name)
    stats_file = os.path.join(dir_name, "stats.txt")
    if os.path.isfile(stats_file):
      stat_dict = stats_to_dict(stats_file)
      data = add_stats(data, app, config, stat_dict)
    else:
      print("%s does not exist" % stats_file)

# print(json.dumps(data, indent=4, sort_keys=True))
# exit(0)

# transform the format to array format
# { app : [ [ configs ], [ control/data ], [ value ] ] }

data_arrays = {}
for app in app_list:
  data_arrays[app] = [[],[],[]]
  for config in config_list:
    for cat in categories:
      data_arrays[app][0].append(config)
      data_arrays[app][1].append(cat)
      data_arrays[app][2].append(data[app][config][cat])

#-------------------------------------------------------------------------
# plotting
#-------------------------------------------------------------------------

def make_stacked_bar_plot( data, headers, fig, ax, title, x_label, y_label ):
  assert( len( data ) == 3 )

  colors = [  "#006D2C",
              "#31A354",
              "#74C476",
              "#9C661F",
              "#FF4040",
              "#DEB887",
              "#00EEEE",
              "#9932CC",
              "#FCE6C9",
              "#7FFF00",
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
                                                  legend = False )
    margin_bottom += values

# create plot
fig, axes = plt.subplots( figsize = ( 20, 7 ),
                          nrows = 1, ncols = len( app_list ),
                          sharey = True )

for i, app in enumerate( app_list ):
  make_stacked_bar_plot( data_arrays[ app ],
    ["config", "category", "value"],
    fig, axes[i], app,
    "config", "value")

axes[0].set_ylabel("Execution Time (cycles)")
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='lower right')

plt.savefig(args.output_file)
