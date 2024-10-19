#!/usr/bin/env python

from __future__ import print_function

import argparse
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from adjustText import adjust_text

from common.stats_to_dict import stats_to_dict
from app_config_list import *

fig_height = 4

config_list = config_list_all

#-------------------------------------------------------------------------
# command-line options & top-level plotting
#-------------------------------------------------------------------------

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Create speed up scatter plot")
  parser.add_argument('-i', '--input-dir', help="Input simout directory", default="../results-latest")
  parser.add_argument('-o', '--output-file', help="Output plot", default="fig-big-tiny-speedup-scatter.png")
  args = parser.parse_args()

  if not os.path.isdir(args.input_dir):
    print("Input directory (%s) does not exist" % args.input_dir)
    exit(1)

  simout_dir = os.path.abspath(args.input_dir)
  pad = 5 # in points

  # create plot
  fig, axes = plt.subplots(figsize = (fig_height * len(app_list), fig_height), nrows = 1, ncols = len(app_list), sharey=True)

  for i, app in enumerate(app_list):
    ax = axes[i]

    x = []
    y = []

    for config in config_list:
      x.append(num_cores_dict[config])

      prefix     = dir_name_dict[config][0]
      runtime    = dir_name_dict[config][1]
      dir_name   = os.path.join(simout_dir, prefix + '-x-' + app + '-' + runtime+ '-' + dataset)
      stats_file = os.path.join(dir_name, "stats.txt")

      if not os.path.isfile(stats_file):
        print("stats file: %s doesn't exist" % stats_file)
        y.append(0)
        continue
      d = stats_to_dict(stats_file)
      if ("sim_ticks" in d):
        y.append(d["sim_ticks"])
      else:
        y.append(0)

    assert(len(x) == len(config_list))
    assert(len(y) == len(config_list))
    y_norm = [0] * len(y)
    for i in xrange(1, len(y)):
      if y[i] != 0:
        y_norm[i] = y[0] / y[i]
    assert(len(y_norm) == len(config_list))
    ax.scatter(x, y_norm)
    ax.set_title(app)
    ax.set_xlabel("Number of cores")
    ax.set_ylabel("Speedup")

    text = []
    for i, config in enumerate(config_list):
      t = ax.text(x[i], y_norm[i], config)
      text.append(t)
    adjust_text(text, ax=ax, arrowprops=dict(arrowstyle='->', color='red'))

  plt.savefig(args.output_file)


