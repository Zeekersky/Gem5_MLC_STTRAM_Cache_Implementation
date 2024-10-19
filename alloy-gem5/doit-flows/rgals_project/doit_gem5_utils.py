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

from verify_groups import *
from app_paths     import *

from clusterjob import *

#----------------------------------------------------------------------------
# Workflow dependencies
#----------------------------------------------------------------------------

from workflow_build_gem5 import *

#----------------------------------------------------------------------------
# Tasks
#----------------------------------------------------------------------------

# Paths

topdir         = '../..'               # Top level gem5 directory
evaldir        = '.'                   # Evaluation directory
scriptsdir     = evaldir + '/scripts'  # Scripts dir
plotdir        = evaldir + '/plots'    # Plots directory
statsdir       = evaldir + '/stats'    # Stats directory
appdir         = evaldir + '/links'    # App binaries directory
appinputdir    = appdir  + '/inputs'   # App inputs directory

genscriptsdir  = evaldir + '/generated-scripts'  # Generated scripts dir

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

  simdict['cfg_script']   = topdir + '/configs/example/se.py'

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

  # verify options

  simdict['verify']      = False     # Verify based on the verify_group

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

  gem5_binary = taskdict_build_gem5['targets'][0]

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

  build_dir_path = evaldir + '/sim-out/' + basename

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

    app_binary   = appdir + '/' + app

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

        app_build_dir   = build_dir_path + '/' + labeled_app
        app_dumpfile    = app_build_dir + '/' + labeled_app + '.out'
        timestamp_file  = app_build_dir + '/timestamp'
        time_stats_file = app_build_dir + '/time_stats.json'

        #.......................
        # App options
        #.......................

        # String substitute app options using the simdict
        # This is useful if you want to embed app params like this:
        # '--processors %(num_cpus)s'

        app_opts = app_opts % simdict

        #app_opts += ' ' + extra_app_opts

        #.......................
        # Misc
        #.......................

        # If verify is on and this is a maven-app-misc app, add --verify
        # to the app options

        if verify and app in verify_groups['maven']:
          app_opts += ' --verify'

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

#............................................................................
# Verify-related
#............................................................................

# General verify function

# Note that `verify_groups` must be defined so that we know which app
# group this app belongs to. This tells us which verify command to use
# for this app.

def verify( basename, subtask_list ):
  '''Given a list of sim subtasks, generate verify subtasks and a
  verification summary subtask for the build directory'''

  # Create path to build_dir inside evaldir

  build_dir_path = evaldir + '/sim-out/' + basename

  # Summary file

  summary_file = build_dir_path + '/summary'

  # Message template if no verify function is found for the app

  na_string = 'echo "N/A    : {} has no verify function" >> ' + summary_file

  # Add verify commands to actions that write to the summary file

  actions   = ['rm -rf ' + summary_file]
  task_dep  = []

  for subtask in subtask_list:

    # Skip docstring task

    if not subtask['actions']:
      continue

    task_dep.append( subtask['name'] )

    # Get metadata

    metadata = ast.literal_eval(subtask['doc'])
    app      = metadata['app']

    # Call verify for this app according to its verify group

    if   app in verify_groups['maven']:
      actions.append( maven_verify_cmd(subtask, summary_file) )
    else:
      actions.append( na_string.format(app) )

  # Add a final command to print the summary_file

  actions += ['cat ' + summary_file]

  # Yield task

  summary_taskdict = { \
      'basename' : basename,
      'name'     : 'summarize',
      'actions'  : actions,
      'task_dep' : task_dep,
      'uptodate' : [ False ], # Always re-execute
      'targets'  : [ summary_file ],
      'doc'      : 'Summarize',
    }

  yield summary_taskdict

# Verify maven-app-misc app

# Print a single line to the summary_file containing whether this
# maven-app-misc app passed or failed verification'''

def maven_verify_cmd( subtask, summary_file ):

  # Get metadata

  metadata = ast.literal_eval(subtask['doc'])

  # Grep the app dumpfile for the pass or fail strings

  dumpfile = metadata['app_dump']

  pass_string = "\\[ passed \\]"
  fail_string = "\\[ FAILED \\]"

  action = '; '.join([
    'if grep -q "\[ passed \]" ' + dumpfile,
      'then echo PASSED : '   + dumpfile + ' >> ' + summary_file,
      'else echo fail\ \  : ' + dumpfile + ' >> ' + summary_file,
    'fi'
  ])

  return action

#............................................................................
# Plot-related
#............................................................................

def task_mkdir_genscriptsdir():
  '''Make the generated-scripts directory in %s''' % genscriptsdir
  basename = '_mkdir-genscriptsdir'
  yield gen_mkdir_task( target=genscriptsdir, basename=basename )

def task_mkdir_plotdir():
  '''Make the plots directory in %s''' % plotdir
  basename = '_mkdir-plotdir'
  yield gen_mkdir_task( target=plotdir, basename=basename )

def gen_app_activity_plot_subtasks( basename, doc, target_dir, normalizer_dir='',
    nup='4x4', crop=False, rasterize=True, dvfs=False,
    hook='ACTIVITY_STAT', hook2='', hook3='', hook4=''):
  '''Given a target gem5 build directory (and optionally a normalizer gem5
  build directory), loop and yield an activity plot subtask for each app'''

  # Yield a docstring subtask

  docstring_taskdict = { \
      'basename' : basename,
      'name'     : None,
      'doc'      : doc,
    }

  yield docstring_taskdict

  # Script command components

  script_path           = scriptsdir + '/plot_activity.py'
  script_target         = evaldir + '/sim-out/' + target_dir
  script_normalizer_str = '--normalizer ' + evaldir + '/sim-out/' + normalizer_dir if normalizer_dir else ''

  # Save outputs for PDF N-up subtask

  script_outputs = []

  # List all subdirectories (i.e., apps)

  target_dir  = target_dir.rstrip('/')
  target_path = evaldir + '/sim-out/' + target_dir

  sub_dir_list = []
  if os.path.isdir( target_path ):
    sub_dir_list = \
        [ x for x in os.listdir( target_path ) if os.path.isdir(target_path+'/'+x) ]

  # Yield a plotting subtask for each subdirectory (i.e., each app)

  for sub_dir in sub_dir_list:

    # The name of the subdirectory is the name of the sim

    sim = sub_dir

    script_output = \
        plotdir + '/' + basename + '-' + sim + '.pdf'
    script_outputs.append( script_output )

    app_dumpfile = target_path + '/' + sim + '/' + sim + '.out'

    # Build action

    action = ' '.join([
      script_path,
      '--target ' + script_target,
      script_normalizer_str,
      '--hook ' + hook,
      '--hook2 ' + hook2 if hook2 else '',
      '--hook3 ' + hook3 if hook3 else '',
      '--hook4 ' + hook4 if hook4 else '',
      '--dvfs' * dvfs,
      '--app ' + sim,
      '--output ' + script_output,
      ])

    taskdict = { \
      'basename' : basename,
      'name'     : sim,
      'actions'  : [ action ],
      'targets'  : [ script_output ],
      'setup'    : [ '_mkdir-plotdir', '_mkdir-genscriptsdir' ],
      # ctorng : comment file_dep to decouple dump/plotting from sims
      #'file_dep' : [ script_path, app_dumpfile ],
      'clean'    : [ clean_targets ],
      'doc'      : 'Plot activity for {} in {}'.format(sim, target_dir),
      }

    yield taskdict

  # Yield a subtask to tile all activity plots together

  nupped_pdf = plotdir + '/' + basename + '-nupped.pdf'
  targets    = [nupped_pdf]
  nup_action = \
      scriptsdir + '/pdfnup --nup ' + nup + ' --paper a4paper --quiet ' \
      + ' '.join(script_outputs) \
      + ' --outfile ' + nupped_pdf

  if crop:
    nup_action += '; ' + scriptsdir + '/pdfcrop ' + nupped_pdf + ' ' + nupped_pdf

  if rasterize:
    # Use -%02d to create a png file for each page of the pdf
    # Otherwise, only the first page is created
    nupped_png = nupped_pdf.replace('.pdf', '-%%02d.png')
    nup_action += '; gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -r300'
    nup_action += ' -sOutputFile=' + nupped_png + ' ' + nupped_pdf

  taskdict = { \
    'basename' : basename,
    'name'     : 'nup',
    'actions'  : [ nup_action ],
    'targets'  : targets,
    'file_dep' : script_outputs,
    'clean'    : [ clean_targets ],
    'doc'      : 'Nup {} activity plots'.format(basename),
    }

  yield taskdict

