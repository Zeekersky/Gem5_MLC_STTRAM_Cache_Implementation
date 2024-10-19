#! /usr/bin/env python
#============================================================================
# utils.py
#============================================================================
# Commonly used functions across scripts for parsing gem5 dumps
#
# Date   : June 8, 2015
# Author : Christopher Torng
#

import sys
import os
import re
import json

#-------------------------------------------------------------------------
# calculate_execution_time
#-------------------------------------------------------------------------
# Returns execution time in seconds of a gem5 simulation

def calculate_execution_time(app_timestat_path):

  # Get time stats

  data = get_time_stats(app_timestat_path)

  # Convert to seconds from ps

  exec_time = data['total'] / 1.0e12

  return exec_time

#-------------------------------------------------------------------------
# get_time_stats
#-------------------------------------------------------------------------
# This function reads time stats for a gem5 simulation from its JSON
# time stat dump.
#
# These stats include:
#
# {
#   "total": 113162049,     # Total execution time in gem5 ticks (ps)
#   "parallel": 87327240,   # Total parallel  time in gem5 ticks (ps)
#   "serial": 25834809,     # Total serial    time in gem5 ticks (ps)
#   "parallel_fraction": 1, # parallel_time / total_time
#   "serial_fraction": 0,   # serial_time / total_time
#   "n_cores_active": {     # Total time spent with N cores active
#     "0": 645645,
#     "1": 26243217,
#     "2": 693693,
#     "3": 282282,
#     "4": 738738,
#     "5": 270270,
#     "6": 174174,
#     "7": 750750,
#     "8": 83363280
#   }
# }


def get_time_stats(json_path):
  return json.load( open(json_path, 'r') )

#-------------------------------------------------------------------------
# calculate_N_cores_active_time
#-------------------------------------------------------------------------
# Return a dict with time in seconds with 0 through N cores active.
#
# This method reads the ACTIVITY_STAT json strings in a gem5 dump file.
# It steps through each stat and adds the time blocks to a dictionary
# that keeps track of the aggregate execution time for 0..N cores active.
#
# NOTE: This information is identical to the data in the JSON time stat
# dump (this is what the get_time_stats() function uses). However, using
# ACTIVITY_STAT allows for capturing the data in special cases -- e.g.,
# tracking time with one active core that is _not_ the master core.

def calculate_N_cores_active_time(app_path):

  # Search for STATS: ON to find configuration data and starting times

  data = {}
  num_big_cores = 1

  fd = open(app_path, 'r')
  for line in fd:
    stats_on = re.search(r"^STATS: ON ({.*})$", line)
    # find number of big cores (o3 core)
    core_type = re.search( r"--heterogeneous (\d);(\d)", line)

    if core_type:
      num_big_cores = int( core_type.group(1) )

    if stats_on:
      data = json.loads(stats_on.group(1))
      break

  if not data:
    sys.exit("ERROR: Cannot find 'STATS: ON' in " + app_path + "!")

  # Grab some important information from data

  num_cores       = data["num_cpus"]
  start_timestamp = data["tick_timestamp"]

  # Initialize dict to hold execution times for n_cores_active
  # (including zero cores active).

  n_cores_active_execution_time = {}

  for i in range( num_cores + 1 ):
    n_cores_active_execution_time[ i ] = 0

  # Special case: track time with one active non-master core

  n_cores_active_execution_time['BI>=LA'] = 0
  n_cores_active_execution_time['BI<LA']  = 0

  # Initialize data arrays and timestamp tracking array

  last_timestamps      = [ int(start_timestamp) for _ in xrange(num_cores) ]
  last_active_state    = [ False for _ in xrange(num_cores) ]
  last_active_state[0] = True # Core 0 starts active

  # Search for ACTIVITY_STAT hook and build activity data arrays

  for line in fd:
    activity_stats = re.search(r"^ACTIVITY_STAT ({.*})$", line)

    if activity_stats:
      data = json.loads(activity_stats.group(1))

      core             = data["cpu"]
      active           = data["active"]
      stat_code        = data["stat_code"]
      tick_timestamp   = data["tick_timestamp"]

      block_size             = tick_timestamp - max(last_timestamps)
      num_active_cores       = sum( last_active_state )
      num_active_big_cores   = sum( last_active_state[0:num_big_cores] )
      num_active_small_cores = sum( last_active_state[num_big_cores:] )

      # Update dict of total time N cores are active

      n_cores_active_execution_time[ num_active_cores ] += block_size

      # Special case: track time with at least one master core inactive
      # and at least one non-master core active

      if num_active_big_cores < num_big_cores and num_active_small_cores >= 1:
        if ( num_big_cores - num_active_big_cores >= num_active_small_cores ):
          n_cores_active_execution_time['BI>=LA'] += block_size
        else:
          n_cores_active_execution_time['BI<LA']  += block_size

      # Update activity tracking information

      last_timestamps   [core] = tick_timestamp
      last_active_state [core] = bool(active)

    # End when we see STATS: OFF

    stats_off = re.search(r"^STATS: OFF ({.*})$", line)

    if stats_off:
      data = json.loads(stats_off.group(1))
      break

  fd.close()

  # Add final blocks of data before ending

  end_timestamp    = data["tick_timestamp"]
  block_size       = end_timestamp - max(last_timestamps)
  num_active_cores = sum( last_active_state )

  # Update dict of total time N cores are active

  n_cores_active_execution_time[ num_active_cores ] += block_size

  # Convert to seconds from ps

  for key in n_cores_active_execution_time.keys():
    n_cores_active_execution_time[key] /= 1.0e12

  return n_cores_active_execution_time

#----------------------------------------------------------------------------
# summarize_timing
#----------------------------------------------------------------------------
# Returns a header, separator, and data string that summarize timing
# stats for a gem5 time stats JSON file. Percentages less than 1% are
# blanked out.
#
# Here is an example:
#
#  Application        | total (us) |  serial %  | parallel % |   0    |   1    |   2    |   3    |   4    |   5    |   6    | BI<LA  | BI>=LA 
# ---------------------------------------------------------------------------------------------------------------------------------------------
#  ubmark-parallel-mt |    79.0    |    0.8%    |   99.2%    |        |        |        |        |        | 54.5%  | 44.7%  |        |

def summarize_timing_app( app_path, app_timestat_path ):

  app = os.path.splitext(os.path.basename( app_path ))[0]

  # Get stats

  time_stats           = get_time_stats(app_timestat_path)
  n_cores_active_stats = calculate_N_cores_active_time(app_path)

  # Convert n_cores_active to percentages of parallel time
  # To do this, we need to subtract serial time from 1-core-active time

  serial_time_s            = time_stats['serial'] / 1.0e12
  n_cores_active_stats[1] -= serial_time_s

  parallel_time_s          = time_stats['parallel'] / 1.0e12
  for key in n_cores_active_stats.keys():
    try:
      n_cores_active_stats[key] /= float(parallel_time_s)
    except ZeroDivisionError:
      n_cores_active_stats[key] = 0.0

  # Grab specific data for table

  len_n_cores_active_stats = len( n_cores_active_stats )

  total_time_us            = time_stats['total'] / 1.0e6
  serial_frac              = time_stats['serial_fraction']
  parallel_frac            = time_stats['parallel_fraction']
  single_non_master_active = n_cores_active_stats['BI<LA'] + n_cores_active_stats['BI>=LA']

  # Format n_cores_active_stats into percentages
  # Also filter out percentages less than 1.0%

  n_cores_active_stats_formatted = []

  for key in sorted(n_cores_active_stats):
    data = n_cores_active_stats[key]
    if data > 0.01:
      n_cores_active_stats_formatted.append( '{:.1%}'.format(data) )
    else:
      n_cores_active_stats_formatted.append( '' )

  # Formatter

  head_fmt = ' {:<50} | {:>10} | {:>10} | {:>10} ' + '| {:>6} ' *len_n_cores_active_stats
  data_fmt = ' {:<50} | {:>10.0f} | {:>10.1%} | {:>10.1%} ' + '| {:>6} ' *len_n_cores_active_stats

  # Header

  header = head_fmt.format( 'Application', 'total (us)', 'serial %', 'parallel %',
                            *sorted(n_cores_active_stats) )
  # Separator

  separator = '-' * len(header)

  # Data

  data = data_fmt.format( app, total_time_us, serial_frac, parallel_frac,
                          *n_cores_active_stats_formatted )

  return header, separator, data

