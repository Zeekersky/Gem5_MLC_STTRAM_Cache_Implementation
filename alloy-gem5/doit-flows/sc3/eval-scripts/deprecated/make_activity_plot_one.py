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

#-------------------------------------------------------------------------
# Collect activity trace
#-------------------------------------------------------------------------

def collect_activity_trace(trace_file, toggle_csr = 0):
  start_cycle      = 0
  end_cycle        = 0
  num_cpus         = 0
  active_intervals = [[]]
  prev_cycle       = []
  with open(trace_file, 'r') as fd:
    for line in fd:
      if line.startswith("STATS: ON"):
        line = line[len("STATS: ON"):].strip()
        d = json.loads(line)
        num_cpus = int(d['num_cpus'])
        start_cycle = int(d['cycle'])
        for i in xrange(num_cpus):
          active_intervals.append([])
        prev_cycle = [-1] * num_cpus
      elif line.startswith("STATS: OFF"):
        line = line[len("STATS: OFF"):].strip()
        d = json.loads(line)
        end_cycle = int(d['cycle'])
      elif line.startswith("ACTIVITY_STAT"):
        line = line[len("ACTIVITY_STAT"):].strip()
        d = json.loads(line)
        if (int(d['toggle_csr']) != toggle_csr):
          continue
        cycle = int(d['cycle'])
        cpu   = int(d['cpu'])
        val   = int(d['csr_val'])
        if (val == 0 and prev_cycle > 0):
          active_intervals[cpu].append([prev_cycle[cpu], cycle])
          prev_cycle[cpu] = -1
        elif val == 1:
          prev_cycle[cpu] = cycle
  return num_cpus, start_cycle, end_cycle, active_intervals

#-------------------------------------------------------------------------
# Make a single activity plot
#-------------------------------------------------------------------------

def make_activity_plot(ax, num_cpus, start_cycle, end_cycle, active_intervals, total_cycles = -1):
  if total_cycles < 0:
    total_cycles = end_cycle - start_cycle
  print(total_cycles)
  height_unit  = 1.0 / float(num_cpus)
  width_unit   = 4.0 / float(total_cycles)

  for cpu in xrange(num_cpus):
    intervals = active_intervals[cpu]
    starts = [width_unit * (interval[0] - start_cycle) for interval in intervals]
    width  = [width_unit * (interval[1] - interval[0]) for interval in intervals]
    length = len(intervals)
    print("  - plotting for cpu %d, num. intervals = %d" % (cpu, length))
    ax.bar(starts, height=[height_unit] * length, width=width, bottom=[cpu * height_unit] * length, align='edge', color='green')

#-------------------------------------------------------------------------
# command-line options & top-level plotting
#-------------------------------------------------------------------------

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Create network traffic plot")
  parser.add_argument('-i', '--input-file', help="Input stdout file")
  parser.add_argument('-o', '--output-file', help="Output plot", default="plot-activity-one.png")
  args = parser.parse_args()

  if not os.path.isfile(args.input_file):
    print("File %s does not exist" % args.input_file)
    exit(1)

  ax = plt.gca()
  num_cpus, start_cycle, end_cycle, active_intervals = collect_activity_trace(args.input_file)
  make_activity_plot(ax, num_cpus, start_cycle, end_cycle, active_intervals)
  plt.savefig(args.output_file)
