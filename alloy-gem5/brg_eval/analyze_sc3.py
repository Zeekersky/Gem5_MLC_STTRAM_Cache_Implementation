#! /usr/bin/env python
#=========================================================================
# analyze_sc3.py
#=========================================================================

import os
import re
import argparse
import matplotlib.pyplot as plt
import pandas as pd

from collect_gem5_stats import collect_gem5_stats

#-------------------------------------------------------------------------
# globals
#-------------------------------------------------------------------------

configs = [
  'mesi',
  'mesi-rand',
  'mesi+A',
  'sc3',
  'sc3+A'
]

apps = [
  'ubmark-fib',
]

# apps = ['cilk5-cholesky',
#         'cilk5-cilksort',
#         'cilk5-heat',
#         'cilk5-knapsack',
#         'cilk5-lcs',
#         'cilk5-matmul',
#         'cilk5-fft',
#         'cilk5-mattranspose',
#         'cilk5-lu',
#         'cilk5-nqueens',
#         'uts',
#         'BC',
#         'BellmanFord',
#         'BFS',
#         'CF',
#         'Components',
#         'KCore',
#         'MIS',
#         'PageRank',
#         'PageRankDelta',
#         'Radii',
#         'Triangle',
# ]

stat_list = [
  'sim_insts',
  'numCycles',

  # appl/sc3 stats
  'numActiveMessages',
  'applNumStealSuccess',
  'applNumStealFail',
  'applEnqueueCycles',
  'applDequeueCycles',
  'applRuntimeCycles',

  # CPU stats
  #   - in runtime
  'in_runtime_cycles',
  'in_runtime_icache_cycles',
  'in_runtime_icache_num_ifetch',
  'in_runtime_dcache_cycles',
  'in_runtime_dcache_num_access',
  'in_runtime_dcache_load_cycles',
  'in_runtime_dcache_load_hit_cycles',
  'in_runtime_dcache_load_miss_cycles',
  'in_runtime_dcache_num_load',
  'in_runtime_dcache_num_load_hit',
  'in_runtime_dcache_num_load_miss',
  'in_runtime_dcache_store_cycles',
  'in_runtime_dcache_store_hit_cycles',
  'in_runtime_dcache_store_miss_cycles',
  'in_runtime_dcache_num_store',
  'in_runtime_dcache_num_store_hit',
  'in_runtime_dcache_num_store_miss',
  'in_runtime_dcache_amo_cycles',
  'in_runtime_dcache_num_amo',
  'in_runtime_dcache_ll_cycles',
  'in_runtime_dcache_num_ll',
  'in_runtime_dcache_sc_cycles',
  'in_runtime_dcache_num_sc',
  'in_runtime_dcache_flush_cycles',
  'in_runtime_dcache_num_flush',

  #   - in tasks
  'in_task_cycles',
  'in_task_icache_cycles',
  'in_task_icache_num_ifetch',
  'in_task_dcache_cycles',
  'in_task_dcache_num_access',
  'in_task_dcache_load_cycles',
  'in_task_dcache_load_hit_cycles',
  'in_task_dcache_load_hit_cycles',
  'in_task_dcache_num_load',
  'in_task_dcache_num_load_hit',
  'in_task_dcache_num_load_miss',
  'in_task_dcache_store_cycles',
  'in_task_dcache_store_hit_cycles',
  'in_task_dcache_store_miss_cycles',
  'in_task_dcache_num_store',
  'in_task_dcache_num_store_hit',
  'in_task_dcache_num_store_miss',
  'in_task_dcache_amo_cycles',
  'in_task_dcache_num_amo',
  'in_task_dcache_ll_cycles',
  'in_task_dcache_num_ll',
  'in_task_dcache_sc_cycles',
  'in_task_dcache_num_sc',
  'in_task_dcache_flush_cycles',
  'in_task_dcache_num_flush',

  # Ruby cache stats
  'L1Dcache.demand_misses',
  'L1Dcache.demand_accesses',

  # Ruby sequencer stats
  'sequencer.num_load',
  'sequencer.load_cycles',
  'sequencer.num_store',
  'sequencer.store_cycles',
  'sequencer.num_LL',
  'sequencer.LL_cycles',
  'sequencer.num_SC',
  'sequencer.SC_cycles',
  'sequencer.num_AMO',
  'sequencer.AMO_cycles',
]

#-------------------------------------------------------------------------
# add entry
#-------------------------------------------------------------------------

def add_entry( app, config, stats_file, df ):
  results = []
  for stat in stat_list:
    results.append( collect_gem5_stats( stats_file, stat ) )
  df[app + '-' + config] = results
  return df

#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------

def main():

  # Command-line options
  parser = argparse.ArgumentParser( description='Collect gem5 stats' )
  parser.add_argument( '-i', '--input-dir',
                       help = 'Input app directory')
  parser.add_argument( '-o', '--output-file',
                       help = 'Output file')
  parser.add_argument( '-n', '--num-cpus',
                       help = 'Number of cpu')
  args = parser.parse_args()

  if not os.path.isdir( args.input_dir ):
    print "Path does not exist"
    exit( 1 )

  if args.num_cpus:
    num_cpus = args.num_cpus
  else:
    num_cpus = 16

  df = pd.DataFrame()
  df['stats'] = stat_list
  df.set_index('stats')

  for app in apps:
    for config in configs:
      print "apps: %s, config: %s, num_cpu = %s" % (app, config, num_cpus)
      input_dir = os.path.join( args.input_dir, app, config, str(num_cpus) )

      if not os.path.isdir( input_dir ):
        print " ... Directory " + input_dir + " does not exist"
        continue

      config_file = os.path.join( input_dir, 'config.json' )
      stats_file  = os.path.join( input_dir, 'stats.txt' )

      if not os.path.isfile( config_file ):
        print " ... " + config_file + " doesn't exist"
        continue

      if not os.path.isfile( stats_file ):
        print " ... " + stats_file + " doesn't exist"
        continue

      df = add_entry( app, config, stats_file, df )

  if args.output_file:
    output_file = args.output_file
    if not output_file.endswith(".csv"):
      output_file += ".csv"
    df.to_csv( output_file )

if __name__ == "__main__":
    main()
