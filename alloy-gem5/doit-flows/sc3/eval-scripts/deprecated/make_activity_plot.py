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
import string

import matplotlib as mpl
mpl.use('Agg')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

from common.stats_to_dict import stats_to_dict
from common.get_sum import get_sum

from make_activity_plot_one import collect_activity_trace, make_activity_plot

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
  # "denovo",
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
# command-line options & top-level plotting
#-------------------------------------------------------------------------

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Create network traffic plot")
  parser.add_argument('-i', '--input-dir', help="Input simout directory", default="./simout")
  parser.add_argument('-o', '--output-file', help="Output plot", default="plot-activity.pdf")
  args = parser.parse_args()

  if not os.path.isdir(args.input_dir):
    print("Input directory (%s) does not exist" % args.input_dir)
    exit(1)

  simout_dir = os.path.abspath(args.input_dir)

  # create plot
  fig, axes = plt.subplots(figsize = (3*len(config_list), 3*len(app_list)), nrows = len(app_list), ncols = len(config_list), sharey=True)

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
      dirname  = "-".join([config, "x", app, runtimes[config], dataset])
      dirname  = os.path.join(args.input_dir, dirname)
      filename = os.path.join(dirname, "stdout")
      if not os.path.isdir(dirname):
        print("warning, directory %s does not exist, skipped" % dirname)
        continue
      elif not os.path.isfile(filename):
        print("warning, file %s does not exist, skipped" % filename)
        continue
      else:
        print("collecting from %s ..." % filename)
      num_cpus, start_cycle, end_cycle, active_intervals = collect_activity_trace(filename)
      make_activity_plot(ax, num_cpus, start_cycle, end_cycle, active_intervals)
      ax = axes[i, j]

  plt.savefig(args.output_file)
