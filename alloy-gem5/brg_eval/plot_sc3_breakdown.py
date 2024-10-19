#!/usr/bin/env python
#=========================================================================
# plot_sc3_breakdown.py
#=========================================================================

import argparse
import csv
import json
import sys
import subprocess
import os
import numpy as np
import matplotlib.pyplot as plt
import math
from matplotlib import rcParams

from collect_sc3_breakdown import configs, apps

def short_name( name ):
  if name.startswith( 'cilk5-' ):
    return name[6:]
  else:
    return name.lower()

rcParams['font.family'] = 'serif'

#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------

def main():

  global apps
  global configs

  fsize = 24
  plt.figure(figsize=(35,10))

  # Command-line options
  parser = argparse.ArgumentParser( description='plot sc3 breakdown' )
  parser.add_argument( '-i', '--input-file',
                       help = 'Input JSON')
  parser.add_argument( '-n', '--nthreads',
                       help = 'Number of threads')
  parser.add_argument( '-o', '--output-file',
                       help = 'Output file name')
  args = parser.parse_args()

  num_cpu = int( args.nthreads )
  if not os.path.isfile( args.input_file ):
    print 'input does not exist'
    exit(1)

  results = {}

  with open( args.input_file ) as f_in:
    results = json.load( f_in )

  # normalize to MESI's total
  for app in apps:
    if configs[0] in results[app] and results[app][configs[0]]['numCycles'] != 0:
      norm = float( results[app][configs[0]]['numCycles'] )
      for config in configs:
        if config in results[app]:
          for key, val in results[app][config].iteritems():
            results[app][config][key] = float(val) / norm
    else:
      # normalizer is not available
      for config in configs:
        if config in results[app]:
          for key, val in results[app][config].iteritems():
            results[app][config][key] = 0

  data = {}

  geo_mean = {}
  count = {}
  for config in configs:
    geo_mean[config] = 1
    count[config] = 0

  categories = [
    'Inst Fetch',
    'Load Hit',
    'Load Miss',
    'Store Hit',
    'Store Miss',
    'Atomic - Task',
    'Atomic - Runtime',
    'Runtime',
    'Flush',
  ]

  for app in apps:
    data[app] = {}
    for config in configs:
      data[app][config] = {}
      if config in results[app]:
        data[app][config]['Inst Fetch'] = results[app][config]['in_task_icache_cycles']
        data[app][config]['Load Hit'] = results[app][config]['in_task_dcache_load_hit_cycles']
        data[app][config]['Load Miss']   = results[app][config]['in_task_dcache_load_miss_cycles']
        data[app][config]['Store Hit']  = results[app][config]['in_task_dcache_store_hit_cycles']
        data[app][config]['Store Miss']  = results[app][config]['in_task_dcache_store_miss_cycles']
        data[app][config]['Atomic - Task']  = results[app][config]['in_task_dcache_amo_cycles'] + \
                                              results[app][config]['in_task_dcache_ll_cycles'] +\
                                              results[app][config]['in_task_dcache_sc_cycles']
        data[app][config]['Atomic - Runtime']  = results[app][config]['in_runtime_dcache_amo_cycles'] + \
                                                 results[app][config]['in_runtime_dcache_ll_cycles'] + \
                                                 results[app][config]['in_runtime_dcache_sc_cycles']
        data[app][config]['Flush']  = results[app][config]['in_task_dcache_flush_cycles'] + \
                                      results[app][config]['in_runtime_dcache_flush_cycles']
        data[app][config]['Runtime'] = results[app][config]['numCycles'] - \
                                       data[app][config]['Inst Fetch'] - \
                                       data[app][config]['Load Hit'] - \
                                      data[app][config]['Load Miss'] - \
                                      data[app][config]['Store Hit'] - \
                                      data[app][config]['Store Miss'] - \
                                      data[app][config]['Atomic - Task'] - \
                                      data[app][config]['Atomic - Runtime'] - \
                                      data[app][config]['Flush']

      else:
        for cat in categories:
          data[app][config][cat] = 0

  # plot setup
  bar_width = 1.0 / ( len(configs) + 1 )

  colors = ['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c','#fdbf6f','#ff7f00','#cab2d6','#6a3d9a','#ffff99']

  j = 0
  bottoms = [[0] * len(apps)] * len(configs)
  ps = []

  for cat in categories:
    x_pos = np.arange(len(apps))
    i = 0
    for config in configs:
      x_val = [x + i*bar_width for x in x_pos]
      y_val = [data[app][config][cat] for app in apps]
      p = plt.bar( x_val,
                   y_val,
                   bottom=bottoms[i],
                   color=colors[j % len(colors)],
                   width=bar_width,
                   label=cat,
                   edgecolor='black' )
      if i == 0:
        ps.append( p )
      bottoms[i] = [sum(x) for x in zip(bottoms[i], y_val)]
      i += 1
    j += 1

  plt.xticks( [ x + (len(configs)/2 - 0.5) * bar_width for x in range(len(apps))], [short_name(app) for app in apps], rotation='horizontal' )
  plt.legend([p[0] for p in ps], categories, loc='center left', bbox_to_anchor=(0.04, -0.12), ncol=8, prop={'size': fsize})

  ax = plt.gca()
  ax.xaxis.set_tick_params(labelsize=fsize)
  ax.yaxis.set_tick_params(labelsize=fsize)

  # save fig
  if (args.output_file):
    output_file = args.output_file
    if not output_file.endswith(".pdf"):
      output_file += ".pdf"
    plt.savefig(output_file, bbox_inches='tight')

if __name__ == "__main__":
    main()
