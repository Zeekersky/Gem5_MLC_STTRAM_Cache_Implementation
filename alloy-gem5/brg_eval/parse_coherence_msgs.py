#!/usr/bin/env python
#=========================================================================
# parse_coherence_msgs.py
#=========================================================================

import argparse
import csv
import re
import sys
import subprocess

#-------------------------------------------------------------------------
# Utility Functions
#-------------------------------------------------------------------------

def execute(cmd):
  try:
    return subprocess.check_output(cmd, shell=True)
  except  subprocess.CalledProcessError, err:
    print "ERROR: " + err.output

#-------------------------------------------------------------------------
# Command-line options
#-------------------------------------------------------------------------

# parser = argparse.ArgumentParser( description='Parse gem5 output' )

# parser.add_argument( '-i', '--stats-file',
#                      help = 'Input stats file')
# parser.add_argument( '-o', '--output',
#                      help = 'Output file')
# parser.add_argument( '-p',
#                      '--protocol',
#                      default = 'RISCV_MESI_Two_Level')

# args = parser.parse_args()

#-------------------------------------------------------------------------
# Input configs
#-------------------------------------------------------------------------

# configs = [ 'cilk-apps-4-mesi',
#             'cilk-apps-4-sc3',
#           ]

#-------------------------------------------------------------------------
# Coherence types
#-------------------------------------------------------------------------

#             protocol         type                  control
type_dict = { 'mesi' :  {   'GETX'               :    True    ,
                            'UPGRADE'            :    True    ,
                            'GETS'               :    True    ,
                            'GET_INSTR'          :    True    ,
                            'INV'                :    True    ,
                            'PUTX'               :    False   ,
                            'MEMORY_ACK'         :    True    ,
                            'DATA'               :    False   ,
                            'DATA_EXCLUSIVE'     :    False   ,
                            'MEMORY_DATA'        :    False   ,
                            'ACK'                :    True    ,
                            'WB_ACK'             :    True    ,
                            'UNBLOCK'            :    True    ,
                            'EXCLUSIVE_UNBLOCK'  :    True    ,
                        },
              'sc3'  :  {   'GETX'               :    True    ,
                            'PUTX'               :    False   ,
                            'WB_ACK'             :    True    ,
                            'ATOMIC'             :    False   ,
                            'LL'                 :    False   ,
                            'SC_SUCCESS'         :    False   ,
                            'SC_FAILED'          :    False   ,
                            'SC'                 :    False   ,
                            'DATA'               :    False   ,
                            'ATOMIC_RESP'        :    False   ,
                        },
            }

#                   0         1         2         3           4
category_list = [ 'fetch', 'control', 'data', 'writeback', 'atomic' ]

#                 protocol         type                  category
type_cat_dict  = { 'mesi' :  {   'GETX'               :      0     ,
                                 'UPGRADE'            :      1     ,
                                 'GETS'               :      0     ,
                                 'GET_INSTR'          :      0     ,
                                 'INV'                :      1     ,
                                 'PUTX'               :      3     ,
                                 'MEMORY_ACK'         :      1     ,
                                 'DATA'               :      2     ,
                                 'DATA_EXCLUSIVE'     :      2     ,
                                 'MEMORY_DATA'        :      2     ,
                                 'ACK'                :      1     ,
                                 'WB_ACK'             :      1     ,
                                 'UNBLOCK'            :      1     ,
                                 'EXCLUSIVE_UNBLOCK'  :      1     ,
                             },
                   'sc3'  :  {   'GETX'               :      0     ,
                                 'PUTX'               :      3     ,
                                 'WB_ACK'             :      1     ,
                                 'ATOMIC'             :      4     ,
                                 'DATA'               :      2     ,
                                 'ATOMIC_RESP'        :      4     ,
                             },
                 }

# extract raw stats into stats_dict
# ( app, config ) : ( control_msg_count, data_msg_count )
stats_dict = {}

# stats_cat
# ( app, config ) : [ ... ]
stats_cat  = {}

#for config in configs:
#  cmd = 'grep -r \"%s\" %s' % ( 'coh_msg_count', config )
#  lines = filter( None, execute(cmd).split('\n') )
#
#  for line in lines:
#    # filter out the comments in the results
#    line            = line.split('#')[0].split()
#
#    # extract stat value
#    stat            = int( line[1] )
#
#    # extract ( config, app )
#    text            = line[0].split('/')
#    config          = text[0]
#    app             = text[1]
#    protocol        = config.split('-')[3]
#
#    # extract coherence type
#    coherence_type  = text[2].split(':')[3]
#
#    if ( app, config ) not in stats_dict:
#      stats_dict[ ( app, config ) ] = [ 0, 0 ]
#      stats_cat [ ( app, config ) ] = [ 0 ] * len(category_list)
#
#    if coherence_type in type_dict[ protocol ]:
#
#      if type_dict[ protocol ][ coherence_type ]:
#        stats_dict[ ( app, config ) ][ 0 ] += stat
#      else:
#        stats_dict[ ( app, config ) ][ 1 ] += stat
#
#      category = type_cat_dict[ protocol ][ coherence_type ]
#      stats_cat[ ( app, config ) ][ category ] += stat
#
## Write stats_dict to csv file
#with open( 'data-control-msg-stats.csv', 'w' ) as f:
#  writer = csv.writer( f )
#  writer.writerow( [ 'app', 'config', 'control_msg_count', 'data_msg_count'])
#  for key in sorted(stats_dict.keys()):
#    writer.writerow([ key[0],
#                      key[1],
#                      str( stats_dict[key][0] ),
#                      str( stats_dict[key][1] )
#                    ] )
#
## Write stats_cat to csv file
#with open( 'msg-cat-stats.csv', 'w' ) as f:
#  writer = csv.writer( f )
#  writer.writerow( [ 'app', 'config' ] + category_list )
#  for key in sorted(stats_cat.keys()):
#    writer.writerow( [ key[0], key[1] ] +
#                     [ str(s) for s in stats_cat[ key ] ] )

def get_network_traffic( file_path, protocol ):
  cmd = 'grep -r \"%s\" %s' % ( 'coh_msg_count', file_path )
  lines = filter( None, execute(cmd).split('\n') )

  control_msg_count = 0
  data_msg_count = 0

  for line in lines:
    # filter out the comments in the results
    line            = line.split('#')[0].split()

    # extract stat value
    stat            = int( line[1] )

    # extract ( config, app )
    text            = line[0].split('/')
    coherence_type  = text[0].split(':')[2]

    if coherence_type == 'UNLOCK':
      continue

    if type_dict[ protocol ][ coherence_type ]:
      control_msg_count += stat
    else:
      data_msg_count += stat

  return ( control_msg_count, data_msg_count )

    # extract coherence type
#    coherence_type  = text[2].split(':')[3]
#
#    if ( app, config ) not in stats_dict:
#      stats_dict[ ( app, config ) ] = [ 0, 0 ]
#      stats_cat [ ( app, config ) ] = [ 0 ] * len(category_list)
#
#    if coherence_type in type_dict[ protocol ]:
#
#      if type_dict[ protocol ][ coherence_type ]:
#        stats_dict[ ( app, config ) ][ 0 ] += stat
#      else:
#        stats_dict[ ( app, config ) ][ 1 ] += stat
#
#      category = type_cat_dict[ protocol ][ coherence_type ]
#      stats_cat[ ( app, config ) ][ category ] += stat
#
#  print stats_dict

#----------------
