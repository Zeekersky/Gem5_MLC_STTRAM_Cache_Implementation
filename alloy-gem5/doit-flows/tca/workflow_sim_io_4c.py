#! /usr/bin/env python
#============================================================================
# workflow_sim_io_4c
#============================================================================
#
# Date   : Jun 25, 2018
# Author : Tuan Ta
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

def get_task_configs():

  simdict = get_base_simdict()

  # gem5 target

  simdict['gem5_target'] = 'opt'

  # Task

  simdict['basename']    = 'sim-io-4c'
  simdict['build_dir']   = 'build-{}'.format(simdict['basename'])
  simdict['doc']         = os.path.basename(__file__).rstrip('c')

  # Extra configs

  simdict['extra_opts']  = [
                             # CPU type
                             '--cpu-type', 'MinorCPU',
                             # num CPUs
                             '-n', '4',
                             # use classic cache
                             '--caches'
                           ]

  # Apps

  simdict['app_group']   = ['tiny']
  simdict['app_list']    = app_list
  simdict['app_dict']    = app_dict

  # Use cluster

  simdict['use_cluster'] = True

  return simdict

def task_sim_io_4c():

  yield gen_sims_per_app( get_task_configs() )


def task_verify_io_4c():

  yield gen_verify_per_app( get_task_configs() )
