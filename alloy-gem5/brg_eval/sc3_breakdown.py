#!/usr/bin/env python
#=========================================================================
# sc3_breakdown.py
#=========================================================================
# Generate sc3 execution breakdown (flush)

import argparse
import json
import os
import subprocess

#-------------------------------------------------------------------------
# Parse gem5 output
#-------------------------------------------------------------------------

def parse_gem5_stats( stats_file, config_file ):

  num_cpus = 1
  output   = {}

  # read config file
  with open( config_file ) as f:
    config = json.load( f )
    num_cpus = len( config['system']['cpu'] )

  total_cycles   = 0
  flush_cycles   = 0
  runtime_cycles = 0
  enqueue_cycles = 0
  dequeue_cycles = 0

  for cpu in xrange( num_cpus ):
    if (num_cpus < 10):
      prefix = "system.cpu%d" % cpu
    elif (num_cpus < 100):
      prefix = "system.cpu%02d" % cpu

    output[cpu] = {}

    with open( stats_file ) as f:
      for line in f:
        line = line.strip()

        if line.startswith(prefix + '.flushCycles'):
          # filter out the comments in the results
          l = line.split('#')[0].split()
          output[cpu]['flush_cycles'] = int( l[1] )
          flush_cycles += output[cpu]['flush_cycles']
        elif line.startswith(prefix + '.applRuntimeCycles'):
          # filter out the comments in the results
          l = line.split('#')[0].split()
          output[cpu]['runtime_cycles'] = int( l[1] )
          runtime_cycles += output[cpu]['runtime_cycles']
        elif line.startswith(prefix + '.applEnqueueCycles'):
          # filter out the comments in the results
          l = line.split('#')[0].split()
          output[cpu]['enqueue_cycles'] = int( l[1] )
          enqueue_cycles += output[cpu]['enqueue_cycles']
        elif line.startswith(prefix + '.applDequeueCycles'):
          # filter out the comments in the results
          l = line.split('#')[0].split()
          output[cpu]['dequeue_cycles'] = int( l[1] )
          dequeue_cycles += output[cpu]['dequeue_cycles']
        elif line.startswith(prefix + '.numCycles'):
          # filter out the comments in the results
          l = line.split('#')[0].split()
          output[cpu]['total_cycles'] = int( l[1] )
          total_cycles += output[cpu]['total_cycles']

  output['total'] = {}
  output['total']['total_cycles']   = total_cycles
  output['total']['dequeue_cycles'] = dequeue_cycles
  output['total']['runtime_cycles'] = runtime_cycles
  output['total']['enqueue_cycles'] = enqueue_cycles
  output['total']['flush_cycles']   = flush_cycles

  return output

#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------

def main():

  # Command-line options
  parser = argparse.ArgumentParser( description='Parse gem5 output' )
  parser.add_argument( '-i', '--input-dir',
                       help = 'Input directory (gem5\'s output) name')
  parser.add_argument( '-o', '--output-file',
                       help = 'Output JSON file')
  args = parser.parse_args()

  if not os.path.isdir( args.input_dir ):
    print "Directory does not exist"
    exit(1)

  config_file = os.path.join( args.input_dir, 'config.json' )
  stats_file  = os.path.join( args.input_dir, 'stats.txt' )

  if not os.path.isfile( config_file ):
    print "config.json doesn't exist"
    exit(1)

  if not os.path.isfile( stats_file ):
    print "stats.txt doesn't exist"
    exit(1)

  output = parse_gem5_stats( stats_file, config_file )

  if args.output_file:
    with open( args.output_file, 'w' ) as f:
      json.dump( output, f, indent=4 )
  else:
    print json.dumps( output, indent=4 )

if __name__ == "__main__":
    main()
