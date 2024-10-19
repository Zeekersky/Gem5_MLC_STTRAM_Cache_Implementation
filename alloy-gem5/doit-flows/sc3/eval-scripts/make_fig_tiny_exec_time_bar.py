#!/usr/bin/env python
#==============================================================================
# Execution time bar plot (big-tiny only)
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
from app_config_list import *

#-------------------------------------------------------------------------
# command-line options
#-------------------------------------------------------------------------

parser = argparse.ArgumentParser(description="Create execution time bar plot")
parser.add_argument('-i', '--input-dir', help="Input simout directory", default="../results-latest")
parser.add_argument('-o', '--output-file', help="Output plot", default="fig-tiny-exec-time-bar.png")
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
data_norm = {}

# initialize

for app in app_list:
  data[app]      = {}
  data_norm[app] = {}
  for config in config_list_tiny:
    data[app][config]      = 0
    data_norm[app][config] = 0.0

for app in app_list:
  for config in config_list_tiny:
    prefix  = dir_name_dict[config][0]
    runtime = dir_name_dict[config][1]
    dir_name = prefix + '-x-' + app + '-' + runtime+ '-' + dataset
    dir_name = os.path.join(simout_dir, dir_name)
    stats_file = os.path.join(dir_name, "stats.txt")
    if os.path.isfile(stats_file):
      stat_dict = stats_to_dict(stats_file)
      if 'sim_ticks' in stat_dict:
        data[app][config] = stat_dict["sim_ticks"]
      else:
        print("\"sim_ticks\" is not in %s" % stats_file)
    else:
      print("%s does not exist" % stats_file)

# normalize to big-tiny-mesi
for app in app_list:
  for config in config_list_tiny:
    if data[app][config_list_tiny[0]] > 0:
      data_norm[app][config] = float(data[app][config]) / float(data[app][config_list_tiny[0]])

data_arrays = {}
for app in app_list:
  data_arrays[app] = [[],[]]
  for config in config_list_tiny:
    data_arrays[app][0].append(config)
    data_arrays[app][1].append(data_norm[app][config])

#-------------------------------------------------------------------------
# plotting
#-------------------------------------------------------------------------

def make_bar_plot(data, fig, ax, title):
  df = pd.DataFrame({'Execution Time' : data[1]}, index=data[0])
  df.plot.bar(ax=ax, rot=90, legend=False, title=title)

# create plot
fig, axes = plt.subplots(figsize = (2*len(app_list), 10),
                         nrows = 1, ncols = len(app_list),
                         sharey = True)

for i, app in enumerate(app_list):
  make_bar_plot(data=data_arrays[app], fig=fig, ax=axes[i], title=app)

axes[0].set_ylabel("Execution Time (cycles)")
handles, labels = axes[0].get_legend_handles_labels()

plt.savefig(args.output_file)
