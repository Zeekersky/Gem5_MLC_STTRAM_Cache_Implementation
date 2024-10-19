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
import copy

from matplotlib import rcParams

from collect_sc3_breakdown import configs, apps
from parse_coherence_msgs import get_network_traffic

def short_name( name ):
  if name.startswith( 'cilk5-' ):
    return name[6:]
  else:
    return name.lower()

rcParams['font.family'] = 'serif'

def collect_network( in_dir, num_cpu ):
  global configs
  global apps

  j = {}

  for app in apps:
    j[app] = {}
    for config in configs:
      j[app][config] = {}

  for app in apps:
    for config in configs:
      print "apps: %s, config: %s, num_cpu = %s" % (app, config, num_cpu)
      input_dir = os.path.join( in_dir, app, config, str(num_cpu) )

      if not os.path.isdir( input_dir ):
        print " ... Directory " + input_dir + " does not exist"
        continue

      config_file = os.path.join( input_dir, 'config.json' )
      stats_file  = os.path.join( input_dir, 'stats.txt' )
      output_file = os.path.join( input_dir, "sc3-breakdown.json")

      if not os.path.isfile( config_file ):
        print " ... " + config_file + " doesn't exist"
        continue

      if not os.path.isfile( stats_file ):
        print " ... " + stats_file + " doesn't exist"
        continue

      if config == 'mesi':
        j[app][config]['Control'], j[app][config]['Data']  = get_network_traffic( stats_file, 'mesi' )
      else:
        j[app][config]['Control'], j[app][config]['Data']  = get_network_traffic( stats_file, 'sc3' )

  nj = {}
  for app in apps:
    nj[app] = {}
    for config in configs:
      nj[app][config] = {}
      nj[app][config]['Control'] = float( j[app][config]['Control'] ) / float ( ( j[app][configs[0]]['Control'] + j[app][configs[0]]['Data'] ) )
      nj[app][config]['Data'] = float( j[app][config]['Data'] ) / float( ( j[app][configs[0]]['Control'] + j[app][configs[0]]['Data'] ) )

  return nj

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
  parser.add_argument( '-i', '--input-dir',
                       help = 'Input JSON')
  parser.add_argument( '-n', '--nthreads',
                       help = 'Number of threads')
  parser.add_argument( '-o', '--output-file',
                       help = 'Output file name')
  args = parser.parse_args()

  num_cpu = int( args.nthreads )
  if not os.path.isdir( args.input_dir ):
    print 'input directory does not exist'
    exit(1)

  data = collect_network( args.input_dir, args.nthreads )

  categories = [
    'Control',
    'Data',
  ]

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
  plt.legend([p[0] for p in ps], categories, loc='center left', bbox_to_anchor=(0.45, -0.12), ncol=8, prop={'size': fsize})

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
