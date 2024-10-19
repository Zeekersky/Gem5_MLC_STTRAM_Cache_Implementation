#! /usr/bin/env python
#============================================================================
# doit_gem5_utils
#============================================================================
# This file contains useful functions for generating gem5 sim tasks:
#
# - get_base_simdict(): See docstring
# - gen_sims_per_app(): See docstring
#
# See workflow_sim_playground.py for an example of how to use these
# utils to run sims. At a high level, we grab a simulation dictionary
# from get_base_simdict() and then write fields to configure the sim.
#
# Search for #paramslist in this file to see all possible fields.
#
# The simulation dictionary is passed to gen_sims_per_app(), which
# generates simulation subtasks for each app. To do this,
# gen_sims_per_app() needs to know about the apps. This requires:
#
# 1. an app list containing the apps you actually want to sim
# 2. an app dictionary with app names / groups / options
#
# All workflows therefore need to import apps.py or another similar file
# to get this information.
#
# Date   : April 7, 2015
# Author : Christopher Torng
#
# Updated by: Tuan Ta
# Date      : June 25, 2018
#

import re
import ast
import json

from doit.tools import create_folder
from doit_utils import *

from app_paths import *

from clusterjob import *

#----------------------------------------------------------------------------
# Workflow dependencies
#----------------------------------------------------------------------------

from workflow_build_gem5 import *

#----------------------------------------------------------------------------
# Tasks
#----------------------------------------------------------------------------

# Paths

topdir    = os.path.abspath('../..')             # Top level gem5 directory
evaldir   = os.path.abspath('.')                 # Evaluation directory
appdir    = os.path.abspath(evaldir + '/links')  # App binaries directory
input_dir = appdir + '/inputs'                   # App input directory
ref_dir   = appdir + '/refs'                     # App reference output directory

#............................................................................
# Utility
#............................................................................

# Returns a list of labeled apps. Apps are labeled distinctly by
# their group in app_dict and by number if there are several sets of
# app_options. Only apps in app_list are returned.
#
# For example, with this entry in the app_dict:
#
#   'ubmark-parallel' : { 'mtpull' : [ '--ilp 0', '--ilp 1' ] }
#
# The list of apps would be:
#
# - ubmark-parallel-mtpull
# - ubmark-parallel-mtpull-1
#
# The sims for the two sets of app options are now uniquely labeled.

def get_labeled_apps(app_dict, app_list, app_group):

  labeled_apps   = []

  for app in app_dict.keys():
    # Only sim the apps in app_list:
    if app not in app_list:
      continue
    # For each app group in app_dict[app]
    for group, app_opts_list in app_dict[app].iteritems():
      # Only sim the apps in app_group:
      if group not in app_group:
        continue
      # For each set of app options
      for i, app_opts in enumerate(app_opts_list):
        # Label specially if more than one set of app_opts
        label       = '-' + str(i) if i > 0 else ''
        labeled_app = app + '-' + group + label
        labeled_apps.append( labeled_app )

  labeled_apps = sorted(labeled_apps)

  return labeled_apps

#............................................................................
# Generating base sim dictionaries
#............................................................................

# Returns a dictionary with metadata for a gem5 simulation. This
# dictionary can be passed to the `gen_sims_per_app` function to
# generate simulation tasks for doit to pick up.

def get_base_simdict():

  # Default task options

  basename     = 'base-sim'
  doc          = 'Sim all apps with basic configuration'

  #..........................................................................
  # Build simulation metadata dictionary
  #..........................................................................

  simdict = {}

  # gem5 options

  simdict['gem5_target']  = 'opt'   # gem5 target binary  ('opt', 'fast', 'debug')
  simdict['debug_flags']  = ''      # gem5 debug flags (e.g., 'Exec')
  simdict['debug_start']  = ''      # begin dumping debug stuff after this tick

  # target configuration

  simdict['cfg_script']   = os.path.abspath(topdir + '/configs/example/se.py')

  # configuration options

  simdict['cfg_opts']     = []       # general configuration options
  simdict['brg_opts']     = []       # BRG specific configuration options
  simdict['extra_opts']   = []       # simulation specific options

  # sim options

  simdict['basename']    = basename  # Name of the task
  simdict['doc']         = doc       # Docstring that is printed in `doit list`

  simdict['app_group']   = []        # Which group of apps to sim (e.g., ['scalar'])
  simdict['app_list']    = []        # List of apps to sim
  simdict['app_dict']    = {}        # Dict with app groups / opts to sim with

  simdict['verify']      = True      # Verify app outputs

  # cluster option

  simdict['use_cluster'] = False

  return simdict

#............................................................................
# Generating sim tasks per app
#............................................................................
# Given a simulation dictionary, yield simulation tasks for doit to find.
#
# Loop and yield a task for:
#
# - for each app in app_dict.keys()
#   - for each app group in app_dict[app]
#     - for each set of app options

def gen_sims_per_app( simdict ):

  # Simulation configuration params from simdict

  basename        = simdict['basename']
  doc             = simdict['doc']

  gem5_target     = simdict['gem5_target']
  debug_flags     = simdict['debug_flags']
  debug_start     = simdict['debug_start']

  cfg_script      = simdict['cfg_script']

  cfg_opts        = simdict['cfg_opts']
  brg_opts        = simdict['brg_opts']
  extra_opts      = simdict['extra_opts']

  app_group       = simdict['app_group']
  app_list        = simdict['app_list']
  app_dict        = simdict['app_dict']

  verify          = simdict['verify']

  use_cluster     = simdict['use_cluster']

  # Yield a docstring subtask

  docstring_taskdict = { \
                         'basename' : basename,
                         'name'     : None,
                         'doc'      : doc,
                       }

  yield docstring_taskdict

  #....................................................................
  # gem5 Target / Project Target
  #....................................................................

  # Get gem5 binary path from task_build_gem5 metadata

  taskdict_build_gem5 = get_taskdict(task_build_gem5,
                                     'build-gem5-{}'.format(gem5_target))

  gem5_binary = os.path.abspath(taskdict_build_gem5['targets'][0])

  # Keep a list of all sim subtasks for verify

  sim_list = []

  # Make string for specified debug flags
  if debug_flags:
    if debug_start:
      debug_flags_str = '--debug-start=' + debug_start + ' --debug-flags=' + ','.join(debug_flags)
    else:
      debug_flags_str = '--debug-flags=' + ','.join(debug_flags)
  else:
    debug_flags_str = ''

  # Create path to build_dir inside evaldir

  build_dir_path = os.path.abspath(evaldir + '/sim-out/' + basename)

  #....................................................................
  # Generate subtasks for each app
  #....................................................................

  # Loop and yield a task for:
  #
  # - for each app in app_dict.keys()
  #   - for each app group in app_dict[app]
  #     - for each set of app options

  for app in app_dict.keys():

    # Only sim the apps in app_list:

    if app not in app_list:
      continue

    # Path to app binary

    app_binary = os.path.abspath(appdir + '/' + app)

    # For each app group in app_dict[app]

    for group, app_opts_list in app_dict[app].iteritems():

      # Only sim the apps in app_group:

      if group not in app_group:
        continue

      # For each set of app options

      for i, app_opts in enumerate(app_opts_list):

        # Label specially to accomodate more than one set of app_opts

        label       = '-' + str(i) if i > 0 else ''
        labeled_app = app + '-' + group + label

        #.......................
        # Simulation output directory and files
        #.......................

        app_build_dir   = os.path.abspath(build_dir_path + '/' + labeled_app)
        base_filename   = app_build_dir + '/' + labeled_app
        app_dumpfile    = base_filename + '.dump'
        timestamp_file  = app_build_dir + '/timestamp'
        time_stats_file = app_build_dir + '/time_stats.json'

        #.......................
        # App options
        #.......................

        # String substitute app options using the simdict
        # This is useful if you want to embed app params like this:
        # '--processors %(num_cpus)s'

        app_opts = app_opts % simdict

        # Add verify option

        if verify:
          if app.split('-')[0] == 'pbbs':
            app_opts = ' -o ' +  app_dumpfile + ' ' + app_opts

        #.......................
        # Misc
        #.......................

        # Save some metadata in the 'doc' field of the task dictionary
        # This is a bit of a hack but lets me easily access information
        # about each sim for its verify task.

        metadata = ', '.join([ "{ 'app'      : '" + app + "'",
                                " 'app_dump' : '" + app_dumpfile + "'",
                                " 'app_opts' : '" + app_opts + "'",
                                " }"
                                ])

        # Put app_opts in double quotes

        app_opts = '\"' + app_opts + '\"'

        # Define targets

        # Note that if verify is on, the time_stats may or may not dump,
        # depending on the verify group

        targets = [ app_dumpfile, timestamp_file ]

        #.......................
        # Assemble gem5 command
        #.......................

        gem5_cmd = ' '.join([
                                # gem5 binary
                                gem5_binary,

                                # debug flags
                                debug_flags_str,

                                # outputs
                                '--outdir', app_build_dir,
                                '--redirect-stdout',
                                '--redirect-stderr',
                                '--stdout-file', base_filename + '.out',
                                '--stderr-file', base_filename + '.err',

                                # config script
                                cfg_script,

                                # app binary and options
                                '-c', app_binary,
                                '-o', app_opts,

                                # config options
                                ' '.join(cfg_opts),
                                ' '.join(brg_opts),
                                ' '.join(extra_opts),

                                # app dumpfile
                                '2>&1', '| tee', app_dumpfile,
                            ])

        if use_cluster:

          #.......................
          # Build Task Dictionary
          #.......................

          taskdict = { \
                       'basename' : basename,
                       'name'     : labeled_app,
                       'actions'  : [ (create_folder, [app_build_dir]), \
                                      (submit_job, [gem5_cmd, labeled_app, app_build_dir]) ],
                       'targets'  : targets,
                       'task_dep' : [ 'link-apps' ],
                       'file_dep' : [ gem5_binary, app_binary ],
                       'uptodate' : [ True ], # Don't rebuild if targets exists
                       'clean'    : [ 'rm -rf {}'.format(app_build_dir) ],
                       'doc'      : metadata,
                     }

        else:

          #.......................
          # Retry functionality
          #.......................

          # Wrap gem5_cmd with retry functionality if we get a socket error

          retry_cmd = ' '.join([ \
              'while : ; do',
                'date +%%Y-%%m%%d-%%H%%M-%%S > ' + timestamp_file + ';',
                gem5_cmd + ';',
                'grep -r -e "listen() failed" -e "Can\'t create socket" ' + app_dumpfile + ';',
                '[[ $? -eq 0 ]] || break;',
              'done;',
              'date +%%Y-%%m%%d-%%H%%M-%%S >> ' + timestamp_file + ';',
              ])

          #.......................
          # Build Task Dictionary
          #.......................

          taskdict = { \
                       'basename' : basename,
                       'name'     : labeled_app,
                       'actions'  : [ (create_folder, [app_build_dir]), retry_cmd ],
                       'targets'  : targets,
                       'task_dep' : [ 'link-apps' ],
                       'file_dep' : [ gem5_binary, app_binary ],
                       'uptodate' : [ True ], # Don't rebuild if targets exists
                       'clean'    : [ 'rm -rf {}'.format(app_build_dir) ],
                       'doc'      : metadata,
                     }

        # Save sim subtasks in a list for verify

        sim_list.append( taskdict )

        yield taskdict

#....................................................................
# Generate Verify Subtasks
#....................................................................

def gen_verify_per_app( simdict ):

  # Simulation configuration params from simdict

  basename        = simdict['basename']
  doc             = simdict['doc']
  app_group       = simdict['app_group']
  app_list        = simdict['app_list']
  app_dict        = simdict['app_dict']
  verify          = simdict['verify']

  # path to build_dir inside evaldir

  build_dir_path  = os.path.abspath(evaldir + '/sim-out/' + basename)
  summary_file    = build_dir_path + '/summary'
  rm_summary_cmd  = 'rm -rf ' + summary_file
  actions         = [ rm_summary_cmd ]

  #....................................................................
  # Generate subtasks for each app
  #....................................................................

  # Loop and yield a task for:
  #
  # - for each app in app_dict.keys()
  #   - for each app group in app_dict[app]
  #     - for each set of app options

  for app in app_dict.keys():

    # Only sim the apps in app_list:

    if app not in app_list:
      continue

    # Path to app binary

    app_binary = os.path.abspath(appdir + '/' + app)

    # For each app group in app_dict[app]

    for group, app_opts_list in app_dict[app].iteritems():

      # Only sim the apps in app_group:

      if group not in app_group:
        continue

      # For each set of app options

      for i, app_opts in enumerate(app_opts_list):

        # Label specially to accomodate more than one set of app_opts

        label       = '-' + str(i) if i > 0 else ''
        labeled_app = app + '-' + group + label

        #.......................
        # Simulation output directory and files
        #.......................

        app_build_dir   = os.path.abspath(build_dir_path + '/' + labeled_app)
        base_filename   = app_build_dir + '/' + labeled_app
        app_dumpfile    = base_filename + '.dump'
        app_stdout      = base_filename + '.out'

        #.......................
        # App options
        #.......................

        # String substitute app options using the simdict
        # This is useful if you want to embed app params like this:
        # '--processors %(num_cpus)s'

        app_opts = app_opts % simdict

        # Message template if no verify function is found for the app

        na_string = 'echo "N/A    : {} has no verify function" >> ' + summary_file

        # Call verify for this app according to its verify group

        if app.split('-')[0] == 'pbbs':
          actions.append( pbbs_verify_cmd(app, app_opts, app_dumpfile, summary_file) )
        elif app.split('-')[0] == 'ligra':
          actions.append( ligra_verify_cmd(app, app_stdout, summary_file) )

  # Add a final command to print the summary_file

  actions += ['cat ' + summary_file]

  # Yield verify / summary task

  summary_taskdict = { \
      'basename' : 'verify-' + basename,
      'name'     : 'summarize',
      'actions'  : actions,
      'uptodate' : [ False ], # Always re-execute
      'targets'  : [ summary_file ],
      'doc'      : 'Summarize',
    }

  yield summary_taskdict

#----------------------------------------------------------------------------
# Verify tasks
#----------------------------------------------------------------------------

# Verify PBBS app
#
# Print a single line to the summary_file containing whether this
# PBBS app passed or failed verification

def pbbs_verify_cmd( app, app_opts, app_dumpfile, summary_file ):

  checker_dir = appdir + '/' + 'checkers-pbbs'

  # The checker binary should be named as 'pbbs-<app>-check' and is
  # common for verifying all implementations of the app

  check_bin_brg   = checker_dir + '/' + \
    '-'.join(app.split('-')[0:2]) \
    + '-check'

  # Get input and output files
  # For PBBS, the input is always the last option given
  # The output is the token after "-o"

  app_opt_tokens  = app_opts.split()
  app_input_file  = app_opt_tokens[-1]
  verify_file     = app_dumpfile + '.verify'

  check_cmd = ' '.join([
    check_bin_brg,
    app_opts,
    app_dumpfile,
    '; echo $? > ' + verify_file,
    ])

  summarize_cmd = \
      'if grep -q -e 0 '        + verify_file + '; ' \
      'then echo PASSED : \"'   + check_cmd   + '\" >> ' + summary_file + '; ' \
      'else echo fail\ \  : \"' + check_cmd   + '\" >> ' + summary_file + '; ' \
      'fi'

  action = check_cmd + '; ' + summarize_cmd

  return action

# Verify LIGRA app
#
# Print a single line to the summary_file containing whether this
# LIGRA app passed or failed verification

def ligra_verify_cmd( app, app_stdout, summary_file ):
  summarize_cmd = \
      'if grep -q -e \"PASS\" ' + app_stdout + '; ' \
      'then echo PASSED : \"'   + app_stdout  + '\" >> ' + summary_file + '; ' \
      'else echo fail\ \  : \"' + app_stdout  + '\" >> ' + summary_file + '; ' \
      'fi'

  return summarize_cmd
