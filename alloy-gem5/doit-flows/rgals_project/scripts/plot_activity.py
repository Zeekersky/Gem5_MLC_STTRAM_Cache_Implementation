#!/usr/bin/env python
#============================================================================
# plot_activity.py [options]
#============================================================================
# This script calculates core activity and/or DVFS activity from gem5
# simulation dumps (*.out) and populates plot template scripts with
# data. It can also plot numcoresbusy bars (at each moment, how many
# cores are active?).
#
#  -h --help          Display this message
#  -v --verbose       Verbose mode
#     --target        Gem5 build directory to calculate activity for
#     --normalizer    Gem5 build directory to normalize x-axis (time) to
#     --numcoresbusy  Adds bars of info if numcoresbusy > 0
#     --hook          The hook in gem5 dump file (e.g., ACTIVITY_STAT)
#     --hook2         The hook in gem5 dump file (e.g., ACTIVITY_STAT)
#     --hook3         The hook in gem5 dump file (e.g., ACTIVITY_STAT)
#     --hook4         The hook in gem5 dump file (e.g., ACTIVITY_STAT)
#     --dvfs          Overlay core activity over DVFS decisions
#     --app           Choose an app to plot (overrides applications vector)
#     --output        Output filename for plot PDF
#     --load <file>   Load activity data from file
#     --dump <file>   Dump activity data to file
#
#     --awsteal-dvfs  Use special awsteal DVFS template
#
# Author : Chris Torng
# Date   : September 30, 2013
#

#----------------------------------------------------------------------------
# Details
#----------------------------------------------------------------------------
#
# The calculate_activity() function operates as follows:
#
#   Input: A gem5 dump in the format shown below
#   Output: A per-core activity dataset and state dataset
#
# Gem5 dumps should look like this:
#
#   STATS: CPU 0 reached stats region
#   STATS: ON {"tick_timestamp": 466456000, "cycle_timestamp": 0, }
#   ACTIVITY_STAT {"cpu": 1, "active": 1, "stat_val": 1, "stat_code": 0, "tick_timestamp": 485524000, "cycle_timestamp": 9534, }
#   ACTIVITY_STAT {"cpu": 2, "active": 1, "stat_val": 1, "stat_code": 0, "tick_timestamp": 485556000, "cycle_timestamp": 9550, }
#   ACTIVITY_STAT {"cpu": 3, "active": 1, "stat_val": 1, "stat_code": 0, "tick_timestamp": 485556000, "cycle_timestamp": 9550, }
#   ACTIVITY_STAT {"cpu": 3, "active": 0, "stat_val": 0, "stat_code": 0, "tick_timestamp": 486726000, "cycle_timestamp": 10135, }
#   ACTIVITY_STAT {"cpu": 2, "active": 0, "stat_val": 0, "stat_code": 0, "tick_timestamp": 486906000, "cycle_timestamp": 10225, }
#   ACTIVITY_STAT {"cpu": 1, "active": 0, "stat_val": 0, "stat_code": 0, "tick_timestamp": 491878000, "cycle_timestamp": 12711, }
#   ACTIVITY_STAT {"cpu": 0, "active": 0, "stat_val": 1, "stat_code": 1, "tick_timestamp": 502146000, "cycle_timestamp": 17845, }
#   ACTIVITY_STAT {"cpu": 0, "active": 1, "stat_val": 0, "stat_code": 1, "tick_timestamp": 502304000, "cycle_timestamp": 17924, }
#   STATS: CPU 0 finished stats region
#   STATS: OFF {"tick_timestamp": 586360000, "cycle_timestamp": 59952, }
#
# The data in {} are imported in JSON format into this script
# (ACTIVITY_STAT is a hook). For the specified core, the function adds
# blocks of time to the activity_set and the corresponding state to the
# state_set. For example, output data may look like this:
#
#   activity_set = {
#       "0": [21, 2, 6],
#       "1": [22, 3, 4]
#   }
#
#   state_set = {
#       "0": ["ACTIVE", "INACTIVE", "ACTIVE"],
#       "1": ["ACTIVE", "INACTIVE", "ACTIVE"]
#   }
#
# This dataset shows that CPU 0 has a block of 21 active time, a block
# of 2 inactive time, and a block of 6 active time for core 0. CPU 1 has
# a block of 22 active, active time, a block of 3 inactive time, and
# then a block of 4 active time.
#
# If opts.numcoresbusy is on with some value N, then we build N extra
# bars of data.  The Nth extra bar will be marked 'active' when exactly
# N cores are active.
#
# The calculate_dvfs_activity() function operates in the same way as
# calculate_activity() does. However, instead of hooking into
# ACTIVITY_STAT, it hooks into DVFS_STAT, which has information on when
# DVFS modes transition.
#
# The gem5 dump might look like this:
#
#   ACTIVITY_STAT { "cpu": 0, "active": 1, "stat_val": 0, "stat_code": 1, "tick_timestamp": 322865856, "cycle_timestamp": 9802 }
#   DVFS_STAT { "cpu": 0, "oldmode": 1, "newmode": 17, "tick_timestamp": 322867545 }
#   DVFS_STAT { "cpu": 1, "oldmode": 1, "newmode": 14, "tick_timestamp": 322867545 }
#   DVFS_STAT { "cpu": 2, "oldmode": 1, "newmode": 14, "tick_timestamp": 322867545 }
#   DVFS_STAT { "cpu": 3, "oldmode": 1, "newmode": 14, "tick_timestamp": 322867545 }
#   DVFS_STAT { "cpu": 4, "oldmode": 1, "newmode": 14, "tick_timestamp": 322867545 }
#   DVFS_STAT { "cpu": 5, "oldmode": 1, "newmode": 14, "tick_timestamp": 322867545 }
#   DVFS_STAT { "cpu": 6, "oldmode": 1, "newmode": 14, "tick_timestamp": 322867545 }
#   DVFS_STAT { "cpu": 7, "oldmode": 1, "newmode": 14, "tick_timestamp": 322867545 }
#   DVFS_STAT { "cpu": 1, "oldmode": 14, "newmode": 0, "tick_timestamp": 322867545 }
#
# Then, the DVFS activity AND the core activity are combined into a
# single activity plot with 2 bars per core.
#

import os
import sys
import argparse
import re
import json
import pprint

from utils import calculate_execution_time

#-------------------------------------------------------------------------------
# Command line processing
#-------------------------------------------------------------------------------

class ArgumentParserWithCustomError(argparse.ArgumentParser):
  def error( self, msg = "" ):
    if ( msg ): print("\n ERROR: %s" % msg)
    print("")
    file = open( sys.argv[0] )
    for ( lineno, line ) in enumerate( file ):
      if ( line[0] != '#' ): sys.exit(msg != "")
      if ( (lineno == 2) or (lineno >= 4) ): print( line[1:].rstrip("\n") )

def parse_cmdline():
  p = ArgumentParserWithCustomError( add_help=False )
  p.add_argument( "-v", "--verbose",       action="store_true"                  )
  p.add_argument( "-h", "--help",          action="store_true"                  )
  p.add_argument(       "--target",        default="../build-doit-mt8/"         )
  p.add_argument(       "--normalizer",    default=""                           )
  p.add_argument(       "--numcoresbusy",  type=int,  dest="boost", default=0   )
  p.add_argument(       "--hook",          default="ACTIVITY_STAT"              )
  p.add_argument(       "--hook2",                                              )
  p.add_argument(       "--hook3",                                              )
  p.add_argument(       "--hook4",                                              )
  p.add_argument(       "--dvfs",          action="store_true"                  )
  p.add_argument(       "--app",           dest="app"                           )
  p.add_argument(       "--output",        dest="output"                        )
  p.add_argument(       "--load",          dest="load"                          )
  p.add_argument(       "--dump",          dest="dump"                          )
  p.add_argument(       "--awsteal-dvfs",  action="store_true"                  )
  opts = p.parse_args()
  if opts.help: p.error()
  return opts

#-------------------------------------------------------------------------
# Parse command line arguments
#-------------------------------------------------------------------------

opts = parse_cmdline()

#-------------------------------------------------------------------------
# Plot templates
#-------------------------------------------------------------------------

current_script_path = os.path.dirname(os.path.abspath(__file__))

activity_bar_one_template = \
    current_script_path + '/activity_bar_one.py.template'

activity_bar_two_template = \
    current_script_path + '/activity_bar_two.py.template'

activity_bar_three_template = \
    current_script_path + '/activity_bar_three.py.template'

activity_bar_four_template = \
    current_script_path + '/activity_bar_four.py.template'

activity_bar_one_dvfs_template = \
    current_script_path + '/activity_bar_one_dvfs.py.template'

activity_bar_two_dvfs_template = \
    current_script_path + '/activity_bar_two_dvfs.py.template'

activity_bar_two_overlap_dvfs_template = \
    current_script_path + '/activity_bar_two_overlap_dvfs.py.template'

activity_bar_one_awsteal_dvfs_template = \
    current_script_path + '/activity_bar_one_awsteal_dvfs.py.template'

activity_bar_two_overlap_awsteal_dvfs_template = \
    current_script_path + '/activity_bar_two_overlap_awsteal_dvfs.py.template'

#-------------------------------------------------------------------------
# Applications Vector
#-------------------------------------------------------------------------

applications = [
  # Longer
  #'bilateral',
  #'mriq',
  #'parsec-scluster',
  #'pbbs-dr',
  #'pbbs-knn',
  #'pbbs-mm',
  ##'pbbs-mst',
  #'splash2-lu-c',
  #'splash2-fft',
  #'viterbi',

  # Shorter
  #'bfs',
  #'dither',
  #'kmeans',
  #'rsort',
  'strsearch',

#  'splash2-ocean-c',
#  'splash2-water-nsquared',

#  'splash2-lu-nc',
#  'splash2-ocean-nc',
#  'splash2-fmm',

#  'bksb',
#  'conv',
#  'median',
#  'mstpbbs',
#  'rgb2cmyk',
#  'sad',
#  'sgemm',
#  'ubmark-bin-search',
#  'ubmark-cmplx-mult',
#  'ubmark-gmemcpy',
#  'ubmark-vvadd',
#  'ubmark-masked-filter',
#  'ubmark-grow',

#  'mibench-adpcmdec',
#  'aes',
#  'sha',
]

# Overwrite applications vector if --app is on

if opts.app:
  applications = [ opts.app ]

#-------------------------------------------------------------------------
# Directories
#-------------------------------------------------------------------------

base_dir_target     = opts.target
base_dir_normalizer = opts.normalizer

# Paths

app_paths_target              = {}
app_paths_normalizer          = {}
app_timestat_paths_target     = {}
app_timestat_paths_normalizer = {}

for app in applications:
  app_paths_target[app] = \
    '/'.join([     base_dir_target, app, app + '.out'])
  app_paths_normalizer[app] = \
    '/'.join([ base_dir_normalizer, app, app + '.out'])
  app_timestat_paths_target[app] = \
    '/'.join([     base_dir_target, app, 'time_stats.json'])
  app_timestat_paths_normalizer[app] = \
    '/'.join([ base_dir_normalizer, app, 'time_stats.json'])

# Output script directory

generated_script_dir = current_script_path + '/../generated-scripts'

#-------------------------------------------------------------------------
# Data structures
#-------------------------------------------------------------------------

# For speedup calculation

execution_time_target     = {}
execution_time_normalizer = {}

# For activity calculation

num_cpus = 0

#-------------------------------------------------------------------------
# Calculation functions
#-------------------------------------------------------------------------

#...........................
# calculate_ratios
#...........................

def calculate_ratios( activity_dataset, state_dataset ):
  '''Given an activity_dataset and state_dataset from calculate_activity(),
  calculate the percentages of active time and return ratios_dataset'''

  ratios_dataset   = {}

  for dataset_key in activity_dataset.iterkeys():
    activity_set = activity_dataset[dataset_key]
    state_set    = state_dataset[dataset_key]

    ratio_set = {}
    for set_key in activity_set.iterkeys():

      active_counter = 0
      inactive_counter = 0

      activity_set_row = activity_set[set_key]
      state_set_row    = state_set[set_key]

      for data, state in zip(activity_set_row, state_set_row):
        if state == "ACTIVE":
          active_counter = active_counter + data
        elif state == "INACTIVE":
          inactive_counter = inactive_counter + data

      ratio_set[set_key] = \
        int(float(active_counter) / (active_counter + inactive_counter) * 100)

    ratios_dataset[dataset_key] = ratio_set

  return ratios_dataset

#...........................
# calculate_activity
#...........................

def calculate_activity(opts, app, hook):
  '''See details at top of file. Reads a gem5 dump and returns a pair of
  datasets describing the activity and state across the execution time.'''

  app_path = app_paths_target[app]
  global num_cpus

  # Search for STATS: ON for configuration data and starting times

  data = {}

  fd = open(app_path, 'r')
  for line in fd:
    stats_on = re.search(r"^STATS: ON ({.*})$", line)

    if stats_on:
      data = json.loads(stats_on.group(1))
      break

  # Create data arrays and timestamp tracking array

  num_cpus          = data["num_cpus"]
  start_timestamp   = data["tick_timestamp"]

  activity_set = {}
  state_set    = {}
  for x in range(num_cpus + opts.boost):
    activity_set[str(x)] = []
    state_set[str(x)]    = []

  last_timestamps      = [ int(start_timestamp) for _ in xrange(num_cpus) ]
  last_active_state    = [ False for _ in xrange(num_cpus) ]

  if hook == "ACTIVITY_STAT":
    last_active_state[0] = True # Core 0 starts active

  # Search for hook and build activity data arrays

  search_str = "^" + hook + " ({.*})$"

  for line in fd:
    activity_stats = re.search(search_str, line)

    if activity_stats:
      data = json.loads(activity_stats.group(1))

      cpu             = data["cpu"]
      active          = data["active"]
      stat_code       = data["stat_code"]
      tick_timestamp  = data["tick_timestamp"]

      block_size      = tick_timestamp - last_timestamps[cpu]

      # Append time blocks and activity color to arrays

      activity_set[str(cpu)].append( block_size )
      if not last_active_state[cpu]:
        state_set[str(cpu)].append( "INACTIVE" )
      else:
        state_set[str(cpu)].append( "ACTIVE" )

      # Add data to boost bars

      if opts.boost > 0:

        block_size = tick_timestamp - max(last_timestamps)
        for i in range( 1, opts.boost + 1 ):

          index = str(num_cpus-1 + i)

          activity_set[index].append( block_size )
          if sum(last_active_state) == i:
            state_set[index].append( "ACTIVE" )
          else:
            state_set[index].append( "INACTIVE" )

          # Merge data if we have two adjacent bars of the same state

          if len(state_set[index]) > 1:
            if state_set[index][-1] == state_set[index][-2]:
              activity_set[index].append(activity_set[index].pop() + activity_set[index].pop())
              state_set[index].pop()

      # Update tracking information

      last_timestamps[cpu]   = tick_timestamp
      last_active_state[cpu] = bool(active)

    # End when we see STATS: OFF

    stats_off = re.search(r"^STATS: OFF ({.*})$", line)

    if stats_off:
      data = json.loads(stats_off.group(1))
      break

  fd.close()

  # Add final blocks of data before ending

  end_timestamp = data["tick_timestamp"]

  for cpu in range(num_cpus):
    block_size = end_timestamp - last_timestamps[cpu]
    activity_set[str(cpu)].append( block_size )
    if not last_active_state[cpu]:
      state_set[str(cpu)].append( "INACTIVE" )
    else:
      state_set[str(cpu)].append( "ACTIVE" )

  # Add final block of data to boost bars

  if opts.boost > 0:
    block_size = end_timestamp - max(last_timestamps)
    for i in range( 1, opts.boost + 1 ):
      index = str(num_cpus-1 + i)
      activity_set[index].append( block_size )
      if sum(last_active_state) == i:
        state_set[index].append( "ACTIVE" )
      else:
        state_set[index].append( "INACTIVE" )

  # Zero pad so all elements have same width

  max_len = 0
  for key, row in activity_set.iteritems():
    if len(row) > max_len:
      max_len = len(row)

  for key in activity_set.iterkeys():
    activity_set_row = activity_set[key]
    state_set_row    = state_set[key]
    while ( len( activity_set_row ) < max_len ):
      activity_set_row.append( 0 )
      state_set_row.append( "EMPTY" )

  return activity_set, state_set

#...........................
# calculate_dvfs_activity
#...........................

def calculate_dvfs_activity(opts, app):
  '''See details at top of file. Reads a gem5 dump and returns a pair of
  datasets describing the DVFS activity and state across execution time.'''

  app_path = app_paths_target[app]
  global num_cpus

  # This has to be updated if the number of DVFS modes changes!
  num_base_dvfs_modes = 9

  # Search for STATS: ON for configuration data and starting times

  data = {}

  fd = open(app_path, 'r')
  for line in fd:
    stats_on = re.search(r"^STATS: ON ({.*})$", line)

    if stats_on:
      data = json.loads(stats_on.group(1))
      break

  # Create data arrays and timestamp tracking array

  num_cpus          = data["num_cpus"]
  start_timestamp   = data["tick_timestamp"]

  activity_set = {}
  state_set    = {}
  for x in range(num_cpus):
    activity_set[str(x)] = []
    state_set[str(x)]    = []

  last_timestamps      = [ int(start_timestamp) for _ in xrange(num_cpus) ]
  last_active_state    = [ 1 for _ in xrange(num_cpus) ] # All cores start at nominal

  # Search for hook and build activity data arrays

  for line in fd:
    dvfs_stats = re.search(r"^DVFS_STAT ({.*})$", line)

    if dvfs_stats:
      data = json.loads(dvfs_stats.group(1))

      cpu             = data["cpu"]
      mode            = data["oldmode"]
      newmode         = data["newmode"]
      tick_timestamp  = data["tick_timestamp"]

      block_size      = tick_timestamp - last_timestamps[cpu]

      # Append time blocks and activity color to arrays according to
      # DVFS mode.

      # If this is a transition mode, convert to base mode first.
      # This is okay because during transition modes for scaling voltage up,
      # the DVFS controller runs the core at the base mode's frequency.

      # Transition modes for scaling voltage down run at the _new_
      # mode's frequency, but frequency scaling down happens
      # instantaneously, so all of these blocks of time should be 0
      # anyway..

      base_mode = (mode / num_base_dvfs_modes) - 1 if (mode >= num_base_dvfs_modes) else mode;

      # Only go through with this if the block size is > 0.
      if block_size > 0.0:

        if   base_mode == 0:
          activity_set[str(cpu)].append( block_size )
          state_set[str(cpu)].append( "r" )
        elif base_mode == 1:
          activity_set[str(cpu)].append( block_size )
          state_set[str(cpu)].append( "0" )
        elif base_mode == 2:
          activity_set[str(cpu)].append( block_size )
          state_set[str(cpu)].append( "1" )
        elif base_mode == 3:
          activity_set[str(cpu)].append( block_size )
          state_set[str(cpu)].append( "2" )
        elif base_mode == 4:
          activity_set[str(cpu)].append( block_size )
          state_set[str(cpu)].append( "3" )
        elif base_mode == 5:
          activity_set[str(cpu)].append( block_size )
          state_set[str(cpu)].append( "4" )
        elif base_mode == 6:
          activity_set[str(cpu)].append( block_size )
          state_set[str(cpu)].append( "5" )
        elif base_mode == 7:
          activity_set[str(cpu)].append( block_size )
          state_set[str(cpu)].append( "6" )
        elif base_mode == 8:
          activity_set[str(cpu)].append( block_size )
          state_set[str(cpu)].append( "7" )

        # Merge data if we have two adjacent bars of the same state

        if len(state_set[str(cpu)]) > 1:
          if state_set[str(cpu)][-1] == state_set[str(cpu)][-2]:
            activity_set[str(cpu)].append(activity_set[str(cpu)].pop() + activity_set[str(cpu)].pop())
            state_set[str(cpu)].pop()

      # Update tracking information

      last_timestamps[cpu]   = tick_timestamp
      last_active_state[cpu] = newmode

    # End when we see STATS: OFF

    stats_off = re.search(r"^STATS: OFF ({.*})$", line)

    if stats_off:
      data = json.loads(stats_off.group(1))
      break

  fd.close()

  # Add final blocks of data before ending

  end_timestamp = data["tick_timestamp"]

  for cpu in range(num_cpus):

    # Calculate base mode first
    mode      = last_active_state[cpu]
    base_mode = (mode / num_base_dvfs_modes) - 1 if (mode >= num_base_dvfs_modes) else mode;

    block_size = end_timestamp - last_timestamps[cpu]
    if   base_mode == 0:
      activity_set[str(cpu)].append( block_size )
      state_set[str(cpu)].append( "r" )
    elif base_mode == 1:
      activity_set[str(cpu)].append( block_size )
      state_set[str(cpu)].append( "0" )
    elif base_mode == 2:
      activity_set[str(cpu)].append( block_size )
      state_set[str(cpu)].append( "1" )
    elif base_mode == 3:
      activity_set[str(cpu)].append( block_size )
      state_set[str(cpu)].append( "2" )
    elif base_mode == 4:
      activity_set[str(cpu)].append( block_size )
      state_set[str(cpu)].append( "3" )
    elif base_mode == 5:
      activity_set[str(cpu)].append( block_size )
      state_set[str(cpu)].append( "4" )
    elif base_mode == 6:
      activity_set[str(cpu)].append( block_size )
      state_set[str(cpu)].append( "5" )
    elif base_mode == 7:
      activity_set[str(cpu)].append( block_size )
      state_set[str(cpu)].append( "6" )
    elif base_mode == 8:
      activity_set[str(cpu)].append( block_size )
      state_set[str(cpu)].append( "7" )

  # Zero pad so all elements have same width

  max_len = 0
  for key, row in activity_set.iteritems():
    if len(row) > max_len:
      max_len = len(row)

  for key in activity_set.iterkeys():
    activity_set_row = activity_set[key]
    state_set_row    = state_set[key]
    while ( len( activity_set_row ) < max_len ):
      activity_set_row.append( 0 )
      state_set_row.append( "EMPTY" )

  return activity_set, state_set

#-------------------------------------------------------------------------
# Calculate execution times
#-------------------------------------------------------------------------

# From target build

for idx, app in enumerate(applications):
  app_timestat_path = app_timestat_paths_target[app]
  execution_time_target[app] = calculate_execution_time(app_timestat_path)

# From normalizer build

if opts.normalizer:
  for idx, app in enumerate(applications):
    app_timestat_path = app_timestat_paths_normalizer[app]
    execution_time_normalizer[app] = calculate_execution_time(app_timestat_path)

#-------------------------------------------------------------------------
# One-bar activity plot
#-------------------------------------------------------------------------

if opts.hook \
    and not opts.hook2 \
    and not opts.hook3 \
    and not opts.hook4 \
    and not opts.dvfs:

  #......................................
  # Load data from file (optional)
  #......................................

  if opts.load:
    fd_data = open(opts.load, 'r')
    dataset = json.load(fd_data)
    activity_dataset = dataset["activity"]
    state_dataset    = dataset["state"]
    labels_dataset   = dataset["labels"]
    ratios_dataset   = dataset["ratios"]
    fd_data.close()

  #......................................
  # Or calculate data
  #......................................

  else:

    # Calculate activity data and state

    activity_dataset = {}
    state_dataset    = {}

    for idx, app in enumerate(applications):
      activity_dataset[app], state_dataset[app] = \
          calculate_activity(opts, app, opts.hook)

    # Calculate activity ratios

    ratios_dataset = calculate_ratios( activity_dataset, state_dataset )

    # Labels

    labels_dataset   = {}

    total_size = len(activity_dataset.itervalues().next()) - opts.boost

    for i in range(total_size):
      labels_dataset[str(i)] = "C" + str(i)

    if opts.boost > 0:
      for i in range( 1, opts.boost + 1 ):
        labels_dataset[str( total_size-1 + i )] = "B" + str(i)

  #......................................
  # Dump data to file (optional)
  #......................................

  if opts.dump:
    dataset = { "activity": activity_dataset, "state": state_dataset, \
                "labels": labels_dataset,     "ratios": ratios_dataset }
    fd_data = open(opts.dump, 'w')
    json.dump(dataset, fd_data,\
        sort_keys=True, indent=4, separators=(',', ': '))
    fd_data.close()

  #......................................
  # Plot script generation
  #......................................

  # Populate bar plot template script for core activity

  basename_target     = re.search( r'([^/]+)/?$', base_dir_target ).group(1)

  if opts.app:
    plotscriptname = \
        generated_script_dir + '/activity-bar-one-' + basename_target + '-' + app + '.py'
  else:
    plotscriptname = \
        generated_script_dir + '/activity-bar-one-' + basename_target + '.py'

  template_fd = open(activity_bar_one_template, 'r')
  gen_script_fd = open(plotscriptname, 'w')
  print "Working on generating " + plotscriptname + "... ",

  for line in template_fd:

    if   line.startswith("## APPLICATIONS-HOOK ##"):
      print>>gen_script_fd, "applications = \\"
      pprint.pprint( applications, gen_script_fd )

    elif line.startswith("## ACTIVITY-DATASET-HOOK ##"):
      print>>gen_script_fd, "activity_dataset = \\"
      pprint.pprint( activity_dataset, gen_script_fd )

    elif line.startswith("## STATE-DATASET-HOOK ##"):
      print>>gen_script_fd, "state_dataset = \\"
      pprint.pprint( state_dataset, gen_script_fd )

    elif line.startswith("## RATIOS-DATASET-HOOK ##"):
      print>>gen_script_fd, "ratios_dataset = \\"
      pprint.pprint( ratios_dataset, gen_script_fd )

    elif line.startswith("## LABELS-DATASET-HOOK ##"):
      print>>gen_script_fd, "labels_dataset = \\"
      pprint.pprint( labels_dataset, gen_script_fd )

    elif line.startswith("## NORMALIZER-DATASET-HOOK ##"):
      print>>gen_script_fd, "normalizer_dataset = \\"
      pprint.pprint( execution_time_normalizer, gen_script_fd )

    else:
      print>>gen_script_fd, line,

  template_fd.close()
  gen_script_fd.close()

  print "done!"

  #......................................
  # Run plot script
  #......................................

  print "Running " + plotscriptname + "... "

  if opts.output:
    cmd = 'python ' + plotscriptname + ' --output ' + opts.output
  else:
    cmd = 'python ' + plotscriptname

  print cmd
  os.system( cmd )

  print "done!"

#-------------------------------------------------------------------------
# DVFS activity with overlay bar
#-------------------------------------------------------------------------

elif opts.hook \
    and not opts.hook2 \
    and not opts.hook3 \
    and not opts.hook4 \
    and     opts.dvfs:

  # Calculate activity data and state

  activity_dataset = {}
  state_dataset    = {}

  for idx, app in enumerate(applications):
    activity_dataset[app], state_dataset[app] = calculate_dvfs_activity(opts, app)

  # Labels

  labels_dataset   = {}

  total_size = len(activity_dataset.itervalues().next())

  for i in range(total_size):
    labels_dataset[str(i)] = "C" + str(i)

  #......................................
  # Overlay data (core activity)
  #......................................

  overlay_activity_dataset = {}
  overlay_state_dataset    = {}

  for idx, app in enumerate(applications):
    overlay_activity_dataset[app], overlay_state_dataset[app] = \
        calculate_activity(opts, app, opts.hook)

  #......................................
  # Plot script generation
  #......................................

  # Populate bar plot template script for DVFS activity + core activity

  basename_target     = re.search( r'([^/]+)/?$', base_dir_target ).group(1)

  if opts.app:
    plotscriptname = \
        generated_script_dir + '/activity-bar-one-dvfs-' + basename_target + '-' + app + '.py'
  else:
    plotscriptname = \
        generated_script_dir + '/activity-bar-one-dvfs-' + basename_target + '.py'

  # Use special awsteal template if --awsteal-dvfs is on

  if opts.awsteal_dvfs:
    template_fd = open(activity_bar_one_awsteal_dvfs_template, 'r')
  else:
    template_fd = open(activity_bar_one_dvfs_template, 'r')

  gen_script_fd = open(plotscriptname, 'w')
  print "Working on generating " + plotscriptname + "... ",

  for line in template_fd:

    if   line.startswith("## APPLICATIONS-HOOK ##"):
      print>>gen_script_fd, "applications = \\"
      pprint.pprint( applications, gen_script_fd )

    elif line.startswith("## ACTIVITY-DATASET-HOOK ##"):
      print>>gen_script_fd, "activity_dataset = \\"
      pprint.pprint( activity_dataset, gen_script_fd )

    elif line.startswith("## STATE-DATASET-HOOK ##"):
      print>>gen_script_fd, "state_dataset = \\"
      pprint.pprint( state_dataset, gen_script_fd )

    elif line.startswith("## OVERLAY-ACTIVITY-DATASET-HOOK ##"):
      print>>gen_script_fd, "overlay_activity_dataset = \\"
      pprint.pprint( overlay_activity_dataset, gen_script_fd )

    elif line.startswith("## OVERLAY-STATE-DATASET-HOOK ##"):
      print>>gen_script_fd, "overlay_state_dataset = \\"
      pprint.pprint( overlay_state_dataset, gen_script_fd )

    elif line.startswith("## LABELS-DATASET-HOOK ##"):
      print>>gen_script_fd, "labels_dataset = \\"
      pprint.pprint( labels_dataset, gen_script_fd )

    elif line.startswith("## NORMALIZER-DATASET-HOOK ##"):
      print>>gen_script_fd, "normalizer_dataset = \\"
      pprint.pprint( execution_time_normalizer, gen_script_fd )

    else:
      print>>gen_script_fd, line,

  template_fd.close()
  gen_script_fd.close()

  print "done!"

  #......................................
  # Run plot script
  #......................................

  print "Running " + plotscriptname + "... "

  if opts.output:
    cmd = 'python ' + plotscriptname + ' --output ' + opts.output
  else:
    cmd = 'python ' + plotscriptname

  print cmd
  os.system( cmd )

  print "done!"

#-------------------------------------------------------------------------
# DVFS activity with two overlay bars
#-------------------------------------------------------------------------

elif opts.hook \
    and     opts.hook2 \
    and not opts.hook3 \
    and not opts.hook4 \
    and     opts.dvfs:

  # Calculate activity data and state

  activity_dataset = {}
  state_dataset    = {}

  for idx, app in enumerate(applications):
    activity_dataset[app], state_dataset[app] = calculate_dvfs_activity(opts, app)

  # Labels

  labels_dataset   = {}

  total_size = len(activity_dataset.itervalues().next())

  for i in range(total_size):
    labels_dataset[str(i)] = "C" + str(i)

  #......................................
  # Overlay data (core activity)
  #......................................

  overlay_activity_dataset = {}
  overlay_state_dataset    = {}

  for idx, app in enumerate(applications):
    overlay_activity_dataset[app], overlay_state_dataset[app] = \
        calculate_activity(opts, app, opts.hook)

  #......................................
  # Overlay second bar
  #......................................

  overlay2_activity_dataset = {}
  overlay2_state_dataset    = {}

  for idx, app in enumerate(applications):
    overlay2_activity_dataset[app], overlay2_state_dataset[app] = \
        calculate_activity(opts, app, opts.hook2)

  #......................................
  # Plot script generation
  #......................................

  # Populate bar plot template script for DVFS activity + core activity

  basename_target     = re.search( r'([^/]+)/?$', base_dir_target ).group(1)

  if opts.app:
    plotscriptname = \
        generated_script_dir + '/activity-bar-two-dvfs-' + basename_target + '-' + app + '.py'
  else:
    plotscriptname = \
        generated_script_dir + '/activity-bar-two-dvfs-' + basename_target + '.py'

  # Use special awsteal template if --awsteal-dvfs is on

  if opts.awsteal_dvfs:
    template_fd = open(activity_bar_two_overlap_awsteal_dvfs_template, 'r')
  else:
    template_fd = open(activity_bar_two_overlap_dvfs_template, 'r')

  gen_script_fd = open(plotscriptname, 'w')
  print "Working on generating " + plotscriptname + "... ",

  for line in template_fd:

    if   line.startswith("## APPLICATIONS-HOOK ##"):
      print>>gen_script_fd, "applications = \\"
      pprint.pprint( applications, gen_script_fd )

    elif line.startswith("## ACTIVITY-DATASET-HOOK ##"):
      print>>gen_script_fd, "activity_dataset = \\"
      pprint.pprint( activity_dataset, gen_script_fd )

    elif line.startswith("## STATE-DATASET-HOOK ##"):
      print>>gen_script_fd, "state_dataset = \\"
      pprint.pprint( state_dataset, gen_script_fd )

    elif line.startswith("## OVERLAY-ACTIVITY-DATASET-HOOK ##"):
      print>>gen_script_fd, "overlay_activity_dataset = \\"
      pprint.pprint( overlay_activity_dataset, gen_script_fd )

    elif line.startswith("## OVERLAY-STATE-DATASET-HOOK ##"):
      print>>gen_script_fd, "overlay_state_dataset = \\"
      pprint.pprint( overlay_state_dataset, gen_script_fd )

    elif line.startswith("## OVERLAY2-ACTIVITY-DATASET-HOOK ##"):
      print>>gen_script_fd, "overlay2_activity_dataset = \\"
      pprint.pprint( overlay2_activity_dataset, gen_script_fd )

    elif line.startswith("## OVERLAY2-STATE-DATASET-HOOK ##"):
      print>>gen_script_fd, "overlay2_state_dataset = \\"
      pprint.pprint( overlay2_state_dataset, gen_script_fd )

    elif line.startswith("## LABELS-DATASET-HOOK ##"):
      print>>gen_script_fd, "labels_dataset = \\"
      pprint.pprint( labels_dataset, gen_script_fd )

    elif line.startswith("## NORMALIZER-DATASET-HOOK ##"):
      print>>gen_script_fd, "normalizer_dataset = \\"
      pprint.pprint( execution_time_normalizer, gen_script_fd )

    else:
      print>>gen_script_fd, line,

  template_fd.close()
  gen_script_fd.close()

  print "done!"

  #......................................
  # Run plot script
  #......................................

  print "Running " + plotscriptname + "... "

  if opts.output:
    cmd = 'python ' + plotscriptname + ' --output ' + opts.output
  else:
    cmd = 'python ' + plotscriptname

  print cmd
  os.system( cmd )

  print "done!"

#-------------------------------------------------------------------------
# Two-bar activity plot
#-------------------------------------------------------------------------

elif opts.hook \
    and     opts.hook2 \
    and not opts.hook3 \
    and not opts.hook4 \
    and not opts.dvfs:

  # Calculate activity data and state

  activity_dataset = {}
  state_dataset    = {}

  for idx, app in enumerate(applications):
    activity_dataset[app], state_dataset[app] = \
        calculate_activity(opts, app, opts.hook)

  # Calculate activity ratios

  ratios_dataset = calculate_ratios( activity_dataset, state_dataset )

  # Labels

  labels_dataset   = {}

  total_size = len(activity_dataset.itervalues().next())

  for i in range(total_size):
    labels_dataset[str(i)] = "C" + str(i)

  #......................................
  # Overlay secondary data
  #......................................

  overlay_activity_dataset = {}
  overlay_state_dataset    = {}

  for idx, app in enumerate(applications):
    overlay_activity_dataset[app], overlay_state_dataset[app] = \
        calculate_activity(opts, app, opts.hook2)

  # Calculate ratios

  overlay_ratios_dataset = \
      calculate_ratios( overlay_activity_dataset, overlay_state_dataset )

  #......................................
  # Plot script generation
  #......................................

  # Populate bar plot template script for DVFS activity + core activity

  basename_target     = re.search( r'([^/]+)/?$', base_dir_target ).group(1)

  if opts.app:
    plotscriptname = \
        generated_script_dir + '/activity-bar-two-' + basename_target + '-' + app + '.py'
  else:
    plotscriptname = \
        generated_script_dir + '/activity-bar-two-' + basename_target + '.py'

  template_fd = open(activity_bar_two_template, 'r')
  gen_script_fd = open(plotscriptname, 'w')
  print "Working on generating " + plotscriptname + "... ",

  for line in template_fd:

    if   line.startswith("## APPLICATIONS-HOOK ##"):
      print>>gen_script_fd, "applications = \\"
      pprint.pprint( applications, gen_script_fd )

    elif line.startswith("## ACTIVITY-DATASET-HOOK ##"):
      print>>gen_script_fd, "activity_dataset = \\"
      pprint.pprint( activity_dataset, gen_script_fd )

    elif line.startswith("## STATE-DATASET-HOOK ##"):
      print>>gen_script_fd, "state_dataset = \\"
      pprint.pprint( state_dataset, gen_script_fd )

    elif line.startswith("## RATIOS-DATASET-HOOK ##"):
      print>>gen_script_fd, "ratios_dataset = \\"
      pprint.pprint( ratios_dataset, gen_script_fd )

    elif line.startswith("## OVERLAY-ACTIVITY-DATASET-HOOK ##"):
      print>>gen_script_fd, "overlay_activity_dataset = \\"
      pprint.pprint( overlay_activity_dataset, gen_script_fd )

    elif line.startswith("## OVERLAY-STATE-DATASET-HOOK ##"):
      print>>gen_script_fd, "overlay_state_dataset = \\"
      pprint.pprint( overlay_state_dataset, gen_script_fd )

    elif line.startswith("## OVERLAY-RATIOS-DATASET-HOOK ##"):
      print>>gen_script_fd, "overlay_ratios_dataset = \\"
      pprint.pprint( overlay_ratios_dataset, gen_script_fd )

    elif line.startswith("## LABELS-DATASET-HOOK ##"):
      print>>gen_script_fd, "labels_dataset = \\"
      pprint.pprint( labels_dataset, gen_script_fd )

    elif line.startswith("## NORMALIZER-DATASET-HOOK ##"):
      print>>gen_script_fd, "normalizer_dataset = \\"
      pprint.pprint( execution_time_normalizer, gen_script_fd )

    else:
      print>>gen_script_fd, line,

  template_fd.close()
  gen_script_fd.close()

  print "done!"

  #......................................
  # Run plot script
  #......................................

  print "Running " + plotscriptname + "... "

  if opts.output:
    cmd = 'python ' + plotscriptname + ' --output ' + opts.output
  else:
    cmd = 'python ' + plotscriptname

  print cmd
  os.system( cmd )

  print "done!"

#-------------------------------------------------------------------------
# Three-bar activity plot
#-------------------------------------------------------------------------

elif opts.hook \
    and     opts.hook2 \
    and     opts.hook3 \
    and not opts.hook4 \
    and not opts.dvfs:

  # Calculate activity data and state

  activity_dataset = {}
  state_dataset    = {}

  for idx, app in enumerate(applications):
    activity_dataset[app], state_dataset[app] = \
        calculate_activity(opts, app, opts.hook)

  # Calculate activity ratios

  ratios_dataset = calculate_ratios( activity_dataset, state_dataset )

  # Labels

  labels_dataset   = {}

  total_size = len(activity_dataset.itervalues().next())

  for i in range(total_size):
    labels_dataset[str(i)] = "C" + str(i)

  #......................................
  # Overlay secondary data
  #......................................

  overlay_activity_dataset = {}
  overlay_state_dataset    = {}

  for idx, app in enumerate(applications):
    overlay_activity_dataset[app], overlay_state_dataset[app] = \
        calculate_activity(opts, app, opts.hook2)

  # Calculate ratios

  overlay_ratios_dataset = \
      calculate_ratios( overlay_activity_dataset, overlay_state_dataset )

  #......................................
  # Overlay tertiary data
  #......................................

  overlay2_activity_dataset = {}
  overlay2_state_dataset    = {}

  for idx, app in enumerate(applications):
    overlay2_activity_dataset[app], overlay2_state_dataset[app] = \
        calculate_activity(opts, app, opts.hook3)

  # Calculate ratios

  overlay2_ratios_dataset = \
      calculate_ratios( overlay2_activity_dataset, overlay2_state_dataset )

  #......................................
  # Plot script generation
  #......................................

  # Populate bar plot template script for DVFS activity + core activity

  basename_target     = re.search( r'([^/]+)/?$', base_dir_target ).group(1)

  if opts.app:
    plotscriptname = \
        generated_script_dir + '/activity-bar-three-' + basename_target + '-' + app + '.py'
  else:
    plotscriptname = \
        generated_script_dir + '/activity-bar-three-' + basename_target + '.py'

  template_fd = open(activity_bar_three_template, 'r')
  gen_script_fd = open(plotscriptname, 'w')
  print "Working on generating " + plotscriptname + "... ",

  for line in template_fd:

    if   line.startswith("## APPLICATIONS-HOOK ##"):
      print>>gen_script_fd, "applications = \\"
      pprint.pprint( applications, gen_script_fd )

    elif line.startswith("## ACTIVITY-DATASET-HOOK ##"):
      print>>gen_script_fd, "activity_dataset = \\"
      pprint.pprint( activity_dataset, gen_script_fd )

    elif line.startswith("## STATE-DATASET-HOOK ##"):
      print>>gen_script_fd, "state_dataset = \\"
      pprint.pprint( state_dataset, gen_script_fd )

    elif line.startswith("## RATIOS-DATASET-HOOK ##"):
      print>>gen_script_fd, "ratios_dataset = \\"
      pprint.pprint( ratios_dataset, gen_script_fd )

    elif line.startswith("## OVERLAY-ACTIVITY-DATASET-HOOK ##"):
      print>>gen_script_fd, "overlay_activity_dataset = \\"
      pprint.pprint( overlay_activity_dataset, gen_script_fd )

    elif line.startswith("## OVERLAY-STATE-DATASET-HOOK ##"):
      print>>gen_script_fd, "overlay_state_dataset = \\"
      pprint.pprint( overlay_state_dataset, gen_script_fd )

    elif line.startswith("## OVERLAY-RATIOS-DATASET-HOOK ##"):
      print>>gen_script_fd, "overlay_ratios_dataset = \\"
      pprint.pprint( overlay_ratios_dataset, gen_script_fd )

    elif line.startswith("## OVERLAY2-ACTIVITY-DATASET-HOOK ##"):
      print>>gen_script_fd, "overlay2_activity_dataset = \\"
      pprint.pprint( overlay2_activity_dataset, gen_script_fd )

    elif line.startswith("## OVERLAY2-STATE-DATASET-HOOK ##"):
      print>>gen_script_fd, "overlay2_state_dataset = \\"
      pprint.pprint( overlay2_state_dataset, gen_script_fd )

    elif line.startswith("## OVERLAY2-RATIOS-DATASET-HOOK ##"):
      print>>gen_script_fd, "overlay2_ratios_dataset = \\"
      pprint.pprint( overlay2_ratios_dataset, gen_script_fd )

    elif line.startswith("## LABELS-DATASET-HOOK ##"):
      print>>gen_script_fd, "labels_dataset = \\"
      pprint.pprint( labels_dataset, gen_script_fd )

    elif line.startswith("## NORMALIZER-DATASET-HOOK ##"):
      print>>gen_script_fd, "normalizer_dataset = \\"
      pprint.pprint( execution_time_normalizer, gen_script_fd )

    else:
      print>>gen_script_fd, line,

  template_fd.close()
  gen_script_fd.close()

  print "done!"

  #......................................
  # Run plot script
  #......................................

  print "Running " + plotscriptname + "... "

  if opts.output:
    cmd = 'python ' + plotscriptname + ' --output ' + opts.output
  else:
    cmd = 'python ' + plotscriptname

  print cmd
  os.system( cmd )

  print "done!"

#-------------------------------------------------------------------------
# Four-bar activity plot
#-------------------------------------------------------------------------

elif opts.hook \
    and     opts.hook2 \
    and     opts.hook3 \
    and     opts.hook4 \
    and not opts.dvfs:

  # Calculate activity data and state

  activity_dataset = {}
  state_dataset    = {}

  for idx, app in enumerate(applications):
    activity_dataset[app], state_dataset[app] = \
        calculate_activity(opts, app, opts.hook)

  # Calculate activity ratios

  ratios_dataset = calculate_ratios( activity_dataset, state_dataset )

  # Labels

  labels_dataset   = {}

  total_size = len(activity_dataset.itervalues().next())

  for i in range(total_size):
    labels_dataset[str(i)] = "C" + str(i)

  #......................................
  # Overlay secondary data
  #......................................

  overlay_activity_dataset = {}
  overlay_state_dataset    = {}

  for idx, app in enumerate(applications):
    overlay_activity_dataset[app], overlay_state_dataset[app] = \
        calculate_activity(opts, app, opts.hook2)

  # Calculate ratios

  overlay_ratios_dataset = \
      calculate_ratios( overlay_activity_dataset, overlay_state_dataset )

  #......................................
  # Overlay tertiary data
  #......................................

  overlay2_activity_dataset = {}
  overlay2_state_dataset    = {}

  for idx, app in enumerate(applications):
    overlay2_activity_dataset[app], overlay2_state_dataset[app] = \
        calculate_activity(opts, app, opts.hook3)

  # Calculate ratios

  overlay2_ratios_dataset = \
      calculate_ratios( overlay2_activity_dataset, overlay2_state_dataset )

  #......................................
  # Overlay quaternary data
  #......................................

  overlay3_activity_dataset = {}
  overlay3_state_dataset    = {}

  for idx, app in enumerate(applications):
    overlay3_activity_dataset[app], overlay3_state_dataset[app] = \
        calculate_activity(opts, app, opts.hook4)

  # Calculate ratios

  overlay3_ratios_dataset = \
      calculate_ratios( overlay3_activity_dataset, overlay3_state_dataset )

  #......................................
  # Plot script generation
  #......................................

  # Populate bar plot template script for DVFS activity + core activity

  basename_target     = re.search( r'([^/]+)/?$', base_dir_target ).group(1)

  if opts.app:
    plotscriptname = \
        generated_script_dir + '/activity-bar-four-' + basename_target + '-' + app + '.py'
  else:
    plotscriptname = \
        generated_script_dir + '/activity-bar-four-' + basename_target + '.py'

  template_fd = open(activity_bar_four_template, 'r')
  gen_script_fd = open(plotscriptname, 'w')
  print "Working on generating " + plotscriptname + "... ",

  for line in template_fd:

    if   line.startswith("## APPLICATIONS-HOOK ##"):
      print>>gen_script_fd, "applications = \\"
      pprint.pprint( applications, gen_script_fd )

    elif line.startswith("## ACTIVITY-DATASET-HOOK ##"):
      print>>gen_script_fd, "activity_dataset = \\"
      pprint.pprint( activity_dataset, gen_script_fd )

    elif line.startswith("## STATE-DATASET-HOOK ##"):
      print>>gen_script_fd, "state_dataset = \\"
      pprint.pprint( state_dataset, gen_script_fd )

    elif line.startswith("## RATIOS-DATASET-HOOK ##"):
      print>>gen_script_fd, "ratios_dataset = \\"
      pprint.pprint( ratios_dataset, gen_script_fd )

    elif line.startswith("## OVERLAY-ACTIVITY-DATASET-HOOK ##"):
      print>>gen_script_fd, "overlay_activity_dataset = \\"
      pprint.pprint( overlay_activity_dataset, gen_script_fd )

    elif line.startswith("## OVERLAY-STATE-DATASET-HOOK ##"):
      print>>gen_script_fd, "overlay_state_dataset = \\"
      pprint.pprint( overlay_state_dataset, gen_script_fd )

    elif line.startswith("## OVERLAY-RATIOS-DATASET-HOOK ##"):
      print>>gen_script_fd, "overlay_ratios_dataset = \\"
      pprint.pprint( overlay_ratios_dataset, gen_script_fd )

    elif line.startswith("## OVERLAY2-ACTIVITY-DATASET-HOOK ##"):
      print>>gen_script_fd, "overlay2_activity_dataset = \\"
      pprint.pprint( overlay2_activity_dataset, gen_script_fd )

    elif line.startswith("## OVERLAY2-STATE-DATASET-HOOK ##"):
      print>>gen_script_fd, "overlay2_state_dataset = \\"
      pprint.pprint( overlay2_state_dataset, gen_script_fd )

    elif line.startswith("## OVERLAY2-RATIOS-DATASET-HOOK ##"):
      print>>gen_script_fd, "overlay2_ratios_dataset = \\"
      pprint.pprint( overlay2_ratios_dataset, gen_script_fd )

    elif line.startswith("## OVERLAY3-ACTIVITY-DATASET-HOOK ##"):
      print>>gen_script_fd, "overlay3_activity_dataset = \\"
      pprint.pprint( overlay3_activity_dataset, gen_script_fd )

    elif line.startswith("## OVERLAY3-STATE-DATASET-HOOK ##"):
      print>>gen_script_fd, "overlay3_state_dataset = \\"
      pprint.pprint( overlay3_state_dataset, gen_script_fd )

    elif line.startswith("## OVERLAY3-RATIOS-DATASET-HOOK ##"):
      print>>gen_script_fd, "overlay3_ratios_dataset = \\"
      pprint.pprint( overlay3_ratios_dataset, gen_script_fd )

    elif line.startswith("## LABELS-DATASET-HOOK ##"):
      print>>gen_script_fd, "labels_dataset = \\"
      pprint.pprint( labels_dataset, gen_script_fd )

    elif line.startswith("## NORMALIZER-DATASET-HOOK ##"):
      print>>gen_script_fd, "normalizer_dataset = \\"
      pprint.pprint( execution_time_normalizer, gen_script_fd )

    else:
      print>>gen_script_fd, line,

  template_fd.close()
  gen_script_fd.close()

  print "done!"

  #......................................
  # Run plot script
  #......................................

  print "Running " + plotscriptname + "... "

  if opts.output:
    cmd = 'python ' + plotscriptname + ' --output ' + opts.output
  else:
    cmd = 'python ' + plotscriptname

  print cmd
  os.system( cmd )

  print "done!"

