#! /usr/bin/env python
#============================================================================
# workflow_plot_activity_ssa
#============================================================================
# Example doit workflow to generate activity plots in (evaldir)/plots.
#
# Date   : April 10, 2015
# Author : Christopher Torng
#

import os
from doit_utils import *

#----------------------------------------------------------------------------
# Workflow dependencies
#----------------------------------------------------------------------------

# Used from doit_gem5_utils
# - gen_app_activity_plot_subtasks()
from doit_gem5_utils import *

#----------------------------------------------------------------------------
# Tasks
#----------------------------------------------------------------------------

def task_plot_activity_ssa():

  # Choose which gem5 build dir to generate activity plots for

  target_dir     = 'verify-ssa'

  # Choose which gem5 build dir to normalize execution time to

  normalizer_dir = ''

  # Choose a task name

  basename = 'plot-activity-ssa'

  # Make a docstring (shows up in 'doit list')
  # Default to current file name

  doc = os.path.basename(__file__).rstrip('c')

  # Pack into dictionary

  argsdict = {
      'basename'       : basename,
      'doc'            : doc,
      'target_dir'     : target_dir,
      'normalizer_dir' : normalizer_dir,
      'hook'           : 'ACTIVITY_STAT',
#      'hook2'          : 'WS_STEAL_STAT',
#      'hook3'          : 'WS_STEAL2_STAT',
#      'hook4'          : 'WS_STEAL3_STAT',
#      'dvfs'           : True,
      'nup'            : '2x2',
      }

  # Generate and yield sim subtasks for each app

  yield gen_app_activity_plot_subtasks( **argsdict )

