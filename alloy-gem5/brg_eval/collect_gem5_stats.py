#! /usr/bin/env python
#=========================================================================
# collect_gem5_stats.py
#=========================================================================

import os
import re
import argparse

#-------------------------------------------------------------------------
# collect_gem5_stats
#-------------------------------------------------------------------------
# collect and accumulate a regular expression from a gem5 stats file

def collect_gem5_stats( stats_file, regex, as_float=False ):
  r = re.compile( regex )

  if as_float:
    result = 0.0
  else:
    result = 0

  with open( stats_file ) as f:
    for line in f:
      line = line.strip()
      if r.search( line ):
        l = line.split('#')[0].split()
        if as_float:
          result += float( l[1] )
        else:
          result += int( l[1] )

  return result

#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------

def main():
  # Command-line options
  parser = argparse.ArgumentParser( description='Collect gem5 stats' )
  parser.add_argument( '-i', '--input-file',
                       help = 'Input stats file')
  parser.add_argument( '-r', '--regex',
                       help = 'Pattern to find (as regex)')
  args = parser.parse_args()

  stats_file  = os.path.join( args.input_file )

  if not os.path.isfile( stats_file ):
    print "File doesn't exist"
    exit(1)

  print collect_gem5_stats( stats_file, args.regex )

if __name__ == "__main__":
    main()
