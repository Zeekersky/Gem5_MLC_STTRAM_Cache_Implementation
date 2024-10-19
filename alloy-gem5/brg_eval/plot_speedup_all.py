#! /usr/bin/env python
#=========================================================================
# plot_scalability.py
#=========================================================================

import os
import re
import matplotlib.pyplot as plt
import argparse

from collect_gem5_stats import collect_gem5_stats
from plot_scalability import plot_scalability

#-------------------------------------------------------------------------
# globals
#-------------------------------------------------------------------------

# plot_scalability( input_dir, configs, num_cpus, app_name, speedup=False,
#                   ax=None )

configs = [
  'mesi',
  'sc3',
  'sc3+A',
]

apps = [
  'cilk5-cilksort',
  'cilk5-lcs',
  'cilk5-fft',
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

  # -- hangs with small/garnet
  'BC',

  # -- not working with small/garnet
  'cilk5-mattranspose',
  'cilk5-lu',
  'cilk5-matmul',
  'PageRank',
  'cilk5-heat',

  # -- lack of parallel speedup
  'KCore',

  # -- malloc in the ROI, not working with SC3
  # 'cilk5-cholesky',
]

num_cpus = [1, 4, 16, 64]

num_columns = 6

fsize = 23

def short_name( name ):
  if name.startswith( 'cilk5-' ):
    return name[6:]
  else:
    return name.lower()

#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------

def main():

  global configs
  global apps
  global num_cpus
  global num_columns
  global fsize

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

  num_rows = len( apps ) / num_columns + 1
  if len(apps) % num_columns == 0:
    num_rows -= 1

  num_columns = min( num_columns, len(apps) )

  plt.rcParams["font.family"] = "serif"

  fig, ax_array = plt.subplots( num_rows, num_columns, sharey='row',
                                figsize=(30,15) )

  for i in xrange( len(apps) ):
    app_dir = os.path.join( input_dir, apps[i] )
    if num_rows == 1:
      plot_scalability( app_dir, configs, num_cpus, short_name(apps[i]),
                        fsize, args.speedup, ax_array[i], False )
    else:
      plot_scalability( app_dir, configs, num_cpus, short_name(apps[i]),
                        fsize, args.speedup,
                        ax_array[i / num_columns, i % num_columns],
                        False )

  # not display the rest
  for i in xrange( len(apps) % num_columns, num_columns ):
    if num_rows == 1:
      fig.delaxes( ax_array[i] )
    else:
      fig.delaxes( ax_array[num_rows-1, i] )

  # add legend
  if num_rows == 1:
    ax = ax_array[num_columns-1]
  else:
    ax= ax_array[0, num_columns-1]

  handles, labels = ax.get_legend_handles_labels()

  fig.legend(handles, labels, fontsize=20, loc='lower right', bbox_to_anchor=(0.996, 0.18) )

  fig.text(0.5, -0.02, 'Number of Cores', ha='center', fontsize=fsize )

  fig.text(-0.02, 0.5, 'Speedup', va='center', rotation='vertical', fontsize=fsize)

  if (args.output_file):
    output_file = args.output_file
    if not output_file.endswith(".pdf"):
      output_file += ".pdf"
    plt.tight_layout()
    plt.savefig(output_file, bbox_inches='tight')

if __name__ == "__main__":
    main()
