#! /usr/bin/env python
#============================================================================
# workflow_verify_ssa
#============================================================================
# Date   : July 5, 2018
# Author : Chris Torng
#

import os
import re

from doit_utils import *
from doit_gem5_utils import *

#----------------------------------------------------------------------------
# Apps
#----------------------------------------------------------------------------

from apps import *

#----------------------------------------------------------------------------
# Tasks
#----------------------------------------------------------------------------

def task_verify_ssa():

  simdict = get_base_simdict()

  # gem5 target

  simdict['gem5_target'] = 'opt'
  simdict['debug_flags'] = [ 'DVFS' ]
  simdict['cfg_script']   = topdir + '/configs/brg/BRGLaneBasedSystem.py'

  # Task

  simdict['basename']    = 'verify-ssa'
  simdict['doc']         = os.path.basename(__file__).rstrip('c')

  # Extra configs

  simdict['extra_opts']  = [
                            '--lane-group-size=4',
                            '--l0i',
                            '--l0i-size=1',
                            '--shared-icache',
                            '--l2cache',
                           ]

  # Turn on verify

  simdict['verify']      = True
#  simdict['extra_opts'] += [ '--continue-after-stats' ]

  # Apps

  simdict['app_group']   = ['tiny']
  simdict['app_list']    = app_list
  simdict['app_dict']    = app_dict

  # Generate and yield sim subtasks for each app

  subtask_list = []

  for subtask in gen_sims_per_app( simdict ):
    subtask_list.append( subtask )
    yield subtask

  yield verify( simdict['basename'], subtask_list )

