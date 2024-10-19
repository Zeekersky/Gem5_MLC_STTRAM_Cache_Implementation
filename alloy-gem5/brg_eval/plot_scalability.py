#! /usr/bin/env python
#=========================================================================
# plot_scalability.py
#=========================================================================

import os
import re
import argparse
import matplotlib.pyplot as plt
import numpy as np

from collect_gem5_stats import collect_gem5_stats

#-------------------------------------------------------------------------
# plot_scalability
#-------------------------------------------------------------------------
# create a scalability plot for a single app

def plot_scalability( input_dir, configs, num_cpus, app_name, fsize, speedup=False,
                      ax=None, standalone=True ):

  # collect cycle counts
  results = []

  for config in configs:
    cycles = []
    for cpu in num_cpus:
      stats_file = os.path.join( input_dir, config, str( cpu ), "stats.txt" )
      if not os.path.isfile( stats_file ):
        print "stats file: " + stats_file + " does not exist, skipped"
        cycles.append( None )
      else:
        cycles.append( collect_gem5_stats( stats_file, r"numCycles" ) / cpu )
    results.append( cycles )

  normalizer = 1

  if speedup:
    # collect serial implementation
    stats_file = os.path.join( input_dir, 'serial', '1', "stats.txt" )
    if not os.path.isfile( stats_file ):
      print "stats file: " + stats_file + " does not exist, abort!"
      return None
    normalizer = collect_gem5_stats( stats_file, r"numCycles" )
    if normalizer == 0:
      print "normalizer is zero, abort!"
      exit( 1 )
  elif results[0][0] != 0:
    normalizer = results[0][0]

  for i in xrange(len(results)):
    for j in xrange(len(results[i])):
      if results[i][j]:
        results[i][j] = float( normalizer ) / float( results[i][j] )

  if ax is None:
    ax = plt.gca()

  colors  = ['#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00','#ffff33','#a65628','#f781bf','#999999']
  markers = [ '.', '+', '*', 'o',"x" ]

  assert len(configs) <= len( markers )

  for i in xrange( len( configs ) ):
    ax.plot( num_cpus, results[i], label=configs[i], color=colors[i % len(colors)], marker=markers[i], markersize=17 )
    ax.xaxis.set_tick_params(labelsize=fsize)
    ax.yaxis.set_tick_params(labelsize=fsize)

  ax.set_ylim( 0, 64 )
  start, end = ax.get_ylim()
  ax.yaxis.set_ticks(np.arange(16, end+1, 16))

  ax.set_xlim( 0, 64 )
  start, end = ax.get_xlim()
  ax.xaxis.set_ticks(np.arange(start, end+1, 16))

  # set aspect ratio
  ratio = 1.0
  xleft, xright = ax.get_xlim()
  ybottom, ytop = ax.get_ylim()
  ax.set_aspect( abs((xright-xleft) / (ybottom-ytop))*ratio, adjustable='box-forced' )

  if standalone:
    ax.legend(loc='upper left')
    if speedup:
      ax.set_title( "Speedup of %s" % app_name, fontsize=fsize )
    else:
      ax.set_title( "Scalability of %s" % app_name )
    ax.set_xlabel( "Number of cores" )
  else:
    ax.set_title( app_name, fontsize=fsize )
  return ax

#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------

def main():

  configs = [
    'mesi',
    'mesi+A',
    'sc3',
    'sc3+A'
  ]

  num_cpus = [1, 4, 16, 64]

  # Command-line options
  parser = argparse.ArgumentParser( description='Collect gem5 stats' )
  parser.add_argument( '-i', '--input-dir',
                       help = 'Input app directory')
  parser.add_argument( '-o', '--output-file',
                       help = 'Output file')
  parser.add_argument( '-s', '--speedup',
                       help = 'Plot speedup instead of scalability, serial impl required',
                       action='store_true' )
  args = parser.parse_args()

  if not os.path.isdir( args.input_dir ):
    print "Path does not exist"
    exit( 1 )

  if args.input_dir[-1] == '/':
    input_dir = args.input_dir[:-1]
  else:
    input_dir = args.input_dir

  app_name = os.path.basename( input_dir )

  ax = plt.axes()
  ax.legend(configs, loc='bottom', bbox_to_anchor=(0.5, 1))

  plot_scalability( input_dir, configs, num_cpus, app_name, args.speedup, 0, ax, True )

  if (args.output_file):
    output_file = args.output_file
    if not output_file.endswith(".pdf"):
      output_file += ".pdf"
    plt.savefig(output_file, bbox_inches='tight')

if __name__ == "__main__":
    main()
