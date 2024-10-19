#!/usr/bin/env python
#==============================================================================
# Speedup over iox1 bar plot
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

# config_list = config_list_serial + config_list_o3 + config_list_big_tiny
config_list = config_list_big_tiny

#-------------------------------------------------------------------------
# command-line options
#-------------------------------------------------------------------------

parser = argparse.ArgumentParser(description="Create speedup over IOx1 bar plot")
parser.add_argument('-i', '--input-dir', help="Input simout directory", default="../results-latest")
parser.add_argument('-o', '--output-file', help="Output plot", default="fig-big-tiny-speedup-io-bar.pdf")
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
  for config in config_list:
    data[app][config]      = 0
    data_norm[app][config] = 0.0

for app in app_list:
  for config in config_list:
    prefix     = dir_name_dict[config][0]
    runtime    = dir_name_dict[config][1]
    dir_name   = os.path.join(simout_dir, prefix + '-x-' + app + '-' + runtime+ '-' + dataset)
    stats_file = os.path.join(dir_name, "stats.txt")

    if os.path.isfile(stats_file):
      stat_dict = stats_to_dict(stats_file)
      if 'sim_ticks' in stat_dict:
        data[app][config] = stat_dict["sim_ticks"]
      else:
        print("\"sim_ticks\" is not in %s" % stats_file)
    else:
      print("%s does not exist" % stats_file)

# speedup over iox1
for app in app_list:
  for config in config_list:
    if data[app][config] > 0:
      data_norm[app][config] = float(data[app][config_list[0]]) / float(data[app][config])

data_arrays = {}

# # calculate geomean

# data_norm['geomean'] = {}
# for config in config_list:
#   data_norm['geomean'][config] = 1

# for app in app_list:
#   for config in config_list:
#     data_norm['geomean'][config] *= data_norm[app][config]

# num_apps = len(app_list)

# for config in config_list:
#   data_norm['geomean'][config] = data_norm['geomean'][config] ** (1.0 / float(num_apps))

# app_list.append('geomean')

for app in app_list:
  data_arrays[app] = [[],[]]
  for config in config_list:
    data_arrays[app][0].append(config)
    data_arrays[app][1].append(data_norm[app][config])

#-------------------------------------------------------------------------
# plotting
#-------------------------------------------------------------------------

def make_bar_plot(data, fig, ax, title):
  df = pd.DataFrame({'Speedup over serial IO' : data[1]}, index=data[0])
  ax.grid(zorder=0)
  df.plot.bar(ax=ax, rot=90, legend=False, title=title, edgecolor='black', zorder=3)

  ax.grid(which='both', linestyle='-', linewidth='0.5', axis='y')
  ax.spines['right'].set_visible(False)
  ax.spines['top'].set_visible(False)

  # group label
  labels = [item.get_text() for item in ax.get_xticklabels()]
  ticks  = xtickslocs = ax.get_xticks()
  assert(len(labels) == len(ticks))

  # cut off

  ax.set_ylim(0, 1.8)

  ymin, _  = ax.get_ylim()
  group_xs = {}

  for i in xrange(len(labels)):
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
    ax.text(x_pos, ymin-0.45, group, ha='center', va='center')
  ax.set_xticklabels(labels)

# create plot

font = {'family' : 'Times New Roman',
        'size'   : 15}
matplotlib.rc('font', **font)

fig, axes = plt.subplots(figsize = (20, 4),
                         nrows = 1, ncols = len(app_list),
                         sharey = True)

for i, app in enumerate(app_list):
  make_bar_plot(data=data_arrays[app], fig=fig, ax=axes[i], title=app)

axes[0].set_ylabel("Speedup")
handles, labels = axes[0].get_legend_handles_labels()

plt.savefig(args.output_file, bbox_inches="tight")
