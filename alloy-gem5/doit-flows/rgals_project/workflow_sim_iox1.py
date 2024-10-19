#! /usr/bin/env python
#============================================================================
# workflow_sim_iox1
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

def task_sim_iox1():

  simdict = get_base_simdict()

  # gem5 target

  simdict['gem5_target'] = 'opt'
  simdict['cfg_script']  = topdir + '/configs/brg/BRGLaneBasedSystem.py'

  # Task

  simdict['basename']    = 'sim-iox1'

  # Docstring is the current script name

  simdict['doc']         = os.path.basename(__file__).rstrip('c')
  simdict['build_dir']   = 'build-' + simdict['basename']

  # Config

  simdict['cfg_opts'] = \
    ' '.join( [ '--caches',
                '--l2cache',
#                '--sys-clock=333.0MHz',
#                '--cpu-clocks="' + '333.0MHz;'*16 + '"',
              ] )

  # Apps

  simdict['app_group']   = ['tiny']
  simdict['app_list']    = app_list
  simdict['app_dict']    = app_dict

  yield gen_sims_per_app( simdict )

