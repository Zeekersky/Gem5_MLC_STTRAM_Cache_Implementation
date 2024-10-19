#! /usr/bin/env python
#=========================================================================
# gem5_stats_to_dict.py
#=========================================================================

import os
import re
import argparse
import json
from collections import defaultdict

#-------------------------------------------------------------------------
# gem5_stats_to_dict
#-------------------------------------------------------------------------
# convert gem5 stats to a nested python dict

def gem5_stats_to_dict( stats_file ):
  nested_dict = lambda: defaultdict(nested_dict)
  results = nested_dict()

  with open( stats_file ) as f:
    for line in f:
      if line.startswith( '----------' ):
        continue

      line = line.strip()
      l = line.split('#')[0].split()

      if len(l) < 2:
        continue

      name = l[0]
      val  = l[1]

      if l[1] == '|':
        continue

      name = name.split('.')
      r = results
      for n in name[0:-1]:
        r = r[n]
      r[ name[-1] ] = val

  return results

#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------

def main():
  # Command-line options
  parser = argparse.ArgumentParser( description='Collect gem5 stats' )
  parser.add_argument( '-i', '--input-file',
                       help = 'Input stats file')
  parser.add_argument( '-o', '--output-file',
                       help = 'Ouput file (as JSON)')
  args = parser.parse_args()

  stats_file  = os.path.join( args.input_file )

  if not os.path.isfile( stats_file ):
    print "File doesn't exist"
    exit(1)

  results = gem5_stats_to_dict( stats_file )

  if args.output_file:
    with open( args.output_file, 'w' ) as fd:
      json.dump( results, fd, indent=2 )
  else:
    print json.dumps( results, indent=4 )

if __name__ == "__main__":
    main()
