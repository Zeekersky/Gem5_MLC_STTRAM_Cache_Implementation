#!/usr/bin/env python
#==============================================================================
# make performance plot
#==============================================================================
#
# Author: Tuan Ta
# Date  : 19/08/07

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

# app list
app_list = [  "cilk5-cs",
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
              "ligra-tc", ]

config_list = [ "serial", "mesi-scalar" ]

# stat_dict
# { config : [] }

parser = argparse.ArgumentParser(description="Create Performance Plot")
parser.add_argument('-i', '--input-file', help="Input all-stats JSON", default="./all-stats.json")
parser.add_argument('-o', '--output-file', help="Output plot", default="plot-scalar-serial-perf.png")
args = parser.parse_args()

if not os.path.isfile(args.input_file):
  print("Input file (%s) does not exist" % args.input_file)
  exit(1)

with open(args.input_file, "r") as f:
  stat_dict = json.load( f )

simtick_dict = stat_dict[ 'sim-ticks' ]
ninst_dict   = stat_dict[ 'sim-insts' ]

perf_dict = {}
inst_dict = {}

for config in config_list:
  perf_dict[ config ] = []
  inst_dict[ config ] = []

  for app in app_list:
    value = simtick_dict[ config ].values()[0][ app ].values()[0][0]
    perf_dict[ config ].append( int( value ) )

    value = ninst_dict[ config ].values()[0][ app ].values()[0][0]
    inst_dict[ config ].append( int( value ) )

fig, axes = plt.subplots( figsize = ( 20, 7 ), nrows = 2, ncols = 1,
                          sharex = True )

df = pd.DataFrame( perf_dict, index = app_list )
df.plot.bar( ax = axes[0], rot = 0 )
axes[0].set_ylabel( "ps" )

df = pd.DataFrame( inst_dict, index = app_list )
df.plot.bar( ax = axes[1], rot = 0 )
axes[1].set_ylabel( "instruction count" )

plt.savefig(args.output_file)
