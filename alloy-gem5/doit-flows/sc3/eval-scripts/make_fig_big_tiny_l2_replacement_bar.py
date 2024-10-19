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
from common.make_stacked_bar_plot import make_stacked_bar_plot
from app_config_list import *

#-------------------------------------------------------------------------
# command-line options
#-------------------------------------------------------------------------

parser = argparse.ArgumentParser(description="Create execution time bar plot")
parser.add_argument('-i', '--input-dir', help="Input simout directory", default="../results-latest")
parser.add_argument('-o', '--output-file', help="Output plot", default="fig-big-tiny-l2-replacement-bar.png")
args = parser.parse_args()

if not os.path.isdir(args.input_dir):
  print("Input directory (%s) does not exist" % args.input_dir)
  exit(1)

simout_dir = os.path.abspath(args.input_dir)

#-------------------------------------------------------------------------
# collect execution time breakdown
#-------------------------------------------------------------------------

categories = [
  'Replacement',
  'Replacement_clean'
]

cat_to_stat_name = {
  'Replacement_clean' : ["L2_Replacement_clean::total"],
  'Replacement'       : ["L2_Replacement::total"],
}

num_l2 = 8

def collect_breakdown(stat_dict):
  d = {}
  stat_dict = stat_dict["ruby"]
  for cat in categories:
    d[cat] = 0
  for cat in categories:
    stat_name_list = cat_to_stat_name[cat]
    for s in stat_name_list:
      if s in stat_dict["L2Cache_Controller"]:
        d[cat] += stat_dict["L2Cache_Controller"][s]
  return d

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
  data[app]      = {}
  for config in config_list_big_tiny:
    data[app][config] = {}
    for cat in categories:
      data[app][config][cat] = 0

for app in app_list:
  for config in config_list_big_tiny:
    prefix  = dir_name_dict[config][0]
    runtime = dir_name_dict[config][1]
    dir_name = prefix + '-x-' + app + '-' + runtime+ '-' + dataset
    dir_name = os.path.join(simout_dir, dir_name)
    stats_file = os.path.join(dir_name, "stats.txt")
    if os.path.isfile(stats_file):

      stat_dict = stats_to_dict(stats_file)
      num_cores = num_cores_dict[config]

      if 'system' in stat_dict:
        data[app][config] = collect_breakdown(stat_dict['system'])
      else:
        print("\"system\" is not in %s" % stats_file)
    else:
      print("%s does not exist" % stats_file)

data_arrays = {}
for app in app_list:
  data_arrays[app] = [[], [], []]
  for config in config_list_big_tiny:
    for cat in categories:
      data_arrays[app][0].append(config)
      data_arrays[app][1].append(cat)
      data_arrays[app][2].append(data[app][config][cat])

#-------------------------------------------------------------------------
# plotting
#-------------------------------------------------------------------------

# create plot
fig, axes = plt.subplots(figsize = (20, 4),
                         nrows = 1, ncols = len(app_list),
                         sharey = True)

for i, app in enumerate(app_list):
  make_stacked_bar_plot(data_arrays[app],
                        ["config", "category", "value"],
                        fig, axes[i],
                        app, "config", "value")

axes[0].set_ylabel("L2 Replacement")
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='lower center', ncol=len(categories))

plt.tight_layout()
plt.savefig(args.output_file)
