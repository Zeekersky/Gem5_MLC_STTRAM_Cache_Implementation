#!/usr/bin/env python
#==============================================================================
# make task distribution plot
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
  "mesi",
  # "mesi-sc3",
  "denovo",
  "nope",
  # "denovo-am",
  "nope-am",
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
}

num_cores = 64

#-------------------------------------------------------------------------
# command-line options
#-------------------------------------------------------------------------

parser = argparse.ArgumentParser(description="Create network traffic plot")
parser.add_argument('-i', '--input-dir', help="Input simout directory", default="./simout")
parser.add_argument('-o', '--output-file', help="Output plot", default="plot-task-distribution.png")
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
    for i in xrange(0, num_cores):
      data[app][config][i] = 0

for app in app_list:
  for config in config_list:
    dir_name = config + '-x-' + app + '-' + runtimes[config] + '-' + dataset
    dir_name = os.path.join(simout_dir, dir_name)
    stats_file = os.path.join(dir_name, "stats.txt")
    if os.path.isfile(stats_file):
      stat_dict = stats_to_dict(stats_file)
      if "system" in stat_dict:
        for i in xrange(0, num_cores):
          data[app][config][i] = stat_dict["system"]["main_cpu%02d" % i]["appl_num_execute"]
    else:
      print("%s does not exist" % stats_file)

# print(json.dumps(data, indent=4, sort_keys=True))
# exit(0)

#-------------------------------------------------------------------------
# plotting
#-------------------------------------------------------------------------

# create plot
fig, axes = plt.subplots(figsize = (3*len(config_list), 3*len(app_list)), nrows = len(app_list), ncols = len(config_list), sharex=True, sharey='row')

pad = 5 # in points

for ax, config in zip(axes[0], config_list):
  ax.annotate(config, xy=(0.5, 1), xytext=(0, pad),
              xycoords='axes fraction', textcoords='offset points',
              size='large', ha='center', va='baseline')

for ax, app in zip(axes[:,0], app_list):
  ax.annotate(app, xy=(0, 0.5), xytext=(-ax.yaxis.labelpad - pad, 0),
              xycoords=ax.yaxis.label, textcoords='offset points',
              size='large', ha='right', va='center')

for i, app in enumerate(app_list):
  for j, config in enumerate(config_list):
    ax = axes[i, j]
    ax.bar(range(0, num_cores), [data[app][config][n] for n in xrange(0, num_cores)])

plt.savefig(args.output_file)
