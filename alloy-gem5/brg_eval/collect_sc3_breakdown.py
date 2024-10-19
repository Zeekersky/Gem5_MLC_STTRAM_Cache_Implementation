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

from parse_mem_breakdown import parse_mem_breakdown

#-------------------------------------------------------------------------
# configs
#-------------------------------------------------------------------------

configs = [
  # 'mesi',
  # 'sc3',
  # 'sc3+A',

  'tiny-mesi',

  'tiny-denovo',
  'tiny-denovo-am',

  'tiny-sc3',
  'tiny-sc3-am',
]

apps = [
  'cilk5-cilksort',
  'cilk5-lcs',
  # 'cilk5-fft',
  'cilk5-nqueens',
  'uts',

  'BellmanFord',
  'BFS',
  'CF',
  'Components',
  'MIS',
  'PageRankDelta',
  'Radii',
  'Triangle',

  # not working with garnet 2.0

  'cilk5-mattranspose',
  'cilk5-lu',
  # 'cilk5-matmul',
  'PageRank',
  'cilk5-heat',
  'BC',
  # lack of parallel speedup
  'KCore',

  # malloc in the ROI, not working with SC3
  # 'cilk5-cholesky',
]

#-------------------------------------------------------------------------
# collect results from the folder
#-------------------------------------------------------------------------

def sc3_collect( in_dir, apps, configs, num_cpu ):
  results = {}

  for app in apps:
    results[app] = {}

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

      j = parse_mem_breakdown( stats_file, config_file )

      if j['total']['numCycles'] != 0:
        results[app][config] = j['total']
      else:
        print "skipping " + app + " with config = "  + config + \
          " since its stats is empty"

  return results

#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------

def main():

  global apps
  global configs

  # Command-line options
  parser = argparse.ArgumentParser( description='plot sc3 breakdown' )
  parser.add_argument( '-i', '--input-dir',
                       help = 'Input directory name')
  parser.add_argument( '-n', '--nthreads',
                       help = 'Number of threads')
  parser.add_argument( '-o', '--output-file',
                       help = 'Output file name')
  args = parser.parse_args()

  num_cpu = int( args.nthreads )

  if not args.output_file:
    print "must specify an output file"
    exit(1)

  # collect result
  results = sc3_collect( args.input_dir, apps, configs, num_cpu )

  with open( args.output_file, 'w' ) as fd:
    json.dump( results, fd, indent=4 )

if __name__ == "__main__":
    main()
