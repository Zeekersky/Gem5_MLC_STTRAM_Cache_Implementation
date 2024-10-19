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

config_list = config_list_serial + config_list_o3 + config_list_big_tiny

#-------------------------------------------------------------------------
# command-line options
#-------------------------------------------------------------------------

parser = argparse.ArgumentParser(description="Create execution time table")
parser.add_argument('-i', '--input-dir', help="Input simout directory", default="../results-latest")
parser.add_argument('-o', '--output-file', help="Output plot", default="table-big-tiny-exec-time.xlsx")
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
  data[app] = []
  for i, config in enumerate(config_list):
    data[app].append(0)

for app in app_list:
  for i, config in enumerate(config_list):
    prefix  = dir_name_dict[config][0]
    runtime = dir_name_dict[config][1]
    dir_name = prefix + '-x-' + app + '-' + runtime+ '-' + dataset
    dir_name = os.path.join(simout_dir, dir_name)
    stats_file = os.path.join(dir_name, "stats.txt")
    if os.path.isfile(stats_file):
      stat_dict = stats_to_dict(stats_file)
      if 'sim_ticks' in stat_dict:
        data[app][i] = stat_dict["sim_ticks"]
      else:
        print("\"sim_ticks\" is not in %s" % stats_file)
    else:
      print("%s does not exist" % stats_file)

# convert to pd.DataFrame

df = pd.DataFrame.from_dict(data, orient='index')
df.columns = config_list
df.to_excel(args.output_file)
