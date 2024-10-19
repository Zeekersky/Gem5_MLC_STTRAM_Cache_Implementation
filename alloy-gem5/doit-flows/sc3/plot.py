#!/usr/bin/env python
#==============================================================================
# process cilkprof data
#==============================================================================
#
# Author: Tuan Ta
# Date  : 19/08/07

import os
import re
import subprocess
import math
import json

import numpy as np
import matplotlib.pyplot as plt

# performance plot

with open("./stats/stat-sim-ticks.json", "r") as f:
  sim_ticks_dict = json.load( f )

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

config_list = [ "serial", "mesi", "denovo", "nope", "denovo-am", "nope-am", "nope-am-tbiw" ]

#
# { config : [] }
#
stat_dict = {}

for config in sim_ticks_dict:
  app_dict = sim_ticks_dict[ config ].values()[ 0 ]
  stat_dict[ config ] = []
  for app in app_list:
    value = 0
    if len( app_dict[ app ][ "small-0" ] ) > 0:
      value = int( app_dict[ app ][ "small-0" ][ 0 ] )
    stat_dict[ config ].append( value )

# normalize to mesi
norm_stat_dict = {}
for config in config_list:
  norm_stat_dict[ config ] = []
  for i in xrange( len( stat_dict[ config ] ) ):
    value = 0
    if stat_dict[ "serial" ][ i ] > 0 and stat_dict[ config ][ i ] > 0:
      value = float( stat_dict[ "serial" ][ i ] ) / stat_dict[ config ][ i ]
    norm_stat_dict[ config ].append( value )

# make plot
n_groups = len( app_list )

fig, ax = plt.subplots( figsize = ( 30, 15 ) )
index = np.arange( n_groups )
bar_width = 0.15

i = 0
for config in config_list:
  plt.bar( index + i * bar_width, norm_stat_dict[ config ], bar_width, label = config )
  i += 1

plt.xlabel( "apps" )
plt.ylabel( "Speedup vs MESI" )
plt.xticks( index + bar_width, app_list )
plt.legend()
plt.tight_layout()

fig.savefig("plot.png")
fig.clf()

## make plot
#app_list = app_dict.keys()
#
#n_cols = 3
#n_rows = int( math.ceil( len( app_list ) / float( n_cols ) ) )
#
#fig, axs = plt.subplots( nrows = n_rows, ncols = n_cols,
#                         figsize = (15, 25) )
#
#for i in xrange( len(app_list) ):
#  app      = app_list[ i ]
#  values   = app_dict[ app ]
#  values   = sorted( values, key = itemgetter(0) )
#
#  x_values = [ str(val[ 0 ]) for val in values ]
#  y_values = [ val[ 1 ] for val in values ]
#
#  print app
#  print "\t" + str(x_values)
#  print "\t" + str(y_values)
#
#  row_idx = i / n_cols
#  col_idx = i % n_cols
#
#  axs[row_idx][col_idx].set_title( app )
#  axs[row_idx][col_idx].set_xlabel('grain size')
#  axs[row_idx][col_idx].set_ylabel('logical parallelism')
#  axs[row_idx][col_idx].plot( x_values, y_values )
#
#fig.tight_layout()
#fig.savefig("plot.png")
#fig.clf()
