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
parser.add_argument('-o', '--output-file', help="Output plot", default="fig-big-tiny-l1-hit-rate-bar.pdf")
args = parser.parse_args()

if not os.path.isdir(args.input_dir):
  print("Input directory (%s) does not exist" % args.input_dir)
  exit(1)

simout_dir = os.path.abspath(args.input_dir)

#-------------------------------------------------------------------------
# collect execution time breakdown
#-------------------------------------------------------------------------

categories = [
  'Hits',
  'Misses'
]

cat_to_stat_name = {
  'Hits'   : ["demand_hits"],
  "Misses" : ["demand_misses"],
}

num_l1  = 64
num_sc3 = 64

def collect_breakdown(stat_dict):
  d = {}
  stat_dict = stat_dict["ruby"]
  for cat in categories:
    d[cat] = 0
  for cat in categories:
    stat_name_list = cat_to_stat_name[cat]
    for i in xrange(0, num_l1):
      for s in stat_name_list:
        if ("l1_cntrl%d" % i in stat_dict) and (s in stat_dict["l1_cntrl%d" % i]["L1Dcache"]):
          d[cat] += stat_dict["l1_cntrl%d" % i]["L1Dcache"][s]
    for i in xrange(0, num_sc3):
      for s in stat_name_list:
        if ("sc3_cntrl%d" % i in stat_dict) and (s in stat_dict["sc3_cntrl%d" % i]["L1Dcache"]):
          d[cat] += stat_dict["sc3_cntrl%d" % i]["L1Dcache"][s]
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
  data_arrays[app] = [[], []]
  for config in config_list_big_tiny:
    data_arrays[app][0].append(config)
    data_arrays[app][1].append(float(data[app][config]['Hits']) / float(data[app][config]['Hits'] + data[app][config]['Misses']) )

#-------------------------------------------------------------------------
# plotting
#-------------------------------------------------------------------------

def make_bar_plot(data, fig, ax, title):
  ax.grid(zorder=0)
  df = pd.DataFrame({'L1D Miss Rate (%)' : data[1]}, index=data[0])
  df.plot.bar(ax=ax, rot=90, legend=False, title=title, edgecolor='black', zorder=3)

# create plot


font = {'family' : 'Times New Roman',
        'size'   : 15}
matplotlib.rc('font', **font)

fig, axes = plt.subplots(figsize = (20, 4),
                         nrows = 1, ncols = len(app_list),
                         sharey = True)

for i, app in enumerate(app_list):
  ax = axes[i]

  ax.grid(which='both', linestyle='-', linewidth='0.5', axis='y')
  ax.spines['right'].set_visible(False)
  ax.spines['top'].set_visible(False)
  make_bar_plot(data=data_arrays[app], fig=fig, ax=axes[i], title=app)

  ax.set_ylim(0.4, 1)

  # group label
  labels = [item.get_text() for item in ax.get_xticklabels()]
  ticks  = xtickslocs = ax.get_xticks()
  assert(len(labels) == len(ticks))

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
    ax.text(x_pos, ymin - 0.14, group, ha='center', va='center')
  ax.set_xticklabels(labels)
  ax.set_xlabel('')

axes[0].set_ylabel("L1D Hit Rate (%)")
handles, labels = axes[0].get_legend_handles_labels()


plt.savefig(args.output_file, bbox_inches="tight")
