#!/usr/bin/env python
#==============================================================================
# Make CPI table
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

config_list = config_list_big_tiny
num_cpus = 64

#-------------------------------------------------------------------------
# collect CPI
#-------------------------------------------------------------------------

def collect_cpi(stat_dict, num_cpus=64):
  if "system" not in stat_dict:
    return []
  stat_dict = stat_dict["system"]

  results = []
  for i in xrange(num_cpus):
    cpu_name = "main_cpu%02d" % i
    num_insts  = stat_dict[cpu_name]["committedInsts"]
    num_cycles = stat_dict[cpu_name]["numCycles"]
    results.append(float(num_cycles) / float(num_insts))

  assert(len(results) == num_cpus)
  return results

#-------------------------------------------------------------------------
# command-line options
#-------------------------------------------------------------------------

parser = argparse.ArgumentParser(description="Generate CPI table")
parser.add_argument('-i', '--input-dir', help="Input simout directory", default="../results-latest")
parser.add_argument('-o', '--output-file', help="Output table", default="table-big-tiny-cpi.xlsx")
args = parser.parse_args()

if not os.path.isdir(args.input_dir):
  print("Input directory (%s) does not exist" % args.input_dir)
  exit(1)

simout_dir = os.path.abspath(args.input_dir)

#-------------------------------------------------------------------------
# collect data
#-------------------------------------------------------------------------

data    = []
index   = []
columns = ["cpu%02d" % i for i in xrange(num_cpus)]

for app in app_list:
  for config in config_list:
    prefix     = dir_name_dict[config][0]
    runtime    = dir_name_dict[config][1]
    dir_name   = os.path.join(simout_dir, prefix + '-x-' + app + '-' + runtime+ '-' + dataset)
    stats_file = os.path.join(dir_name, "stats.txt")

    if os.path.isfile(stats_file):
      stat_dict = stats_to_dict(stats_file)
      data.append(collect_cpi(stat_dict, num_cpus))
      index.append(app + '-' + config)
    else:
      print("%s does not exist" % stats_file)

df = pd.DataFrame(data, columns=columns, index=index)
df.to_excel(args.output_file)