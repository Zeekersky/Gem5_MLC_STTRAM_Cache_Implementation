#! /usr/bin/env python
#============================================================================
# workflow_sim_ssa
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

def simdict_ssa():

  simdict = get_base_simdict()

  # gem5 target

  simdict['gem5_target'] = 'opt'
#  simdict['debug_flags'] = [ 'Exec' ]
  simdict['cfg_script']   = topdir + '/configs/brg/BRGLaneBasedSystem.py'

  # Task

  simdict['basename']    = 'sim-ssa'

  # Docstring is the current script name

  simdict['doc']         = os.path.basename(__file__).rstrip('c')

  # Extra configs

  simdict['extra_opts']  = [
#                            '--lane-group-size=4',
                            '--l0i',
                            '--l0i-size=1',
                            '--shared-icache',
                            '--shared-dcache',
                            '--l2cache',
                            '--cpu-clock=1GHz',
#                            '--cache-clock=1GHz',
#                            '--cache-latency-multiplier=1',
                           ]

  # Apps

#  simdict['app_group']   = ['medium']
  simdict['app_list']    = app_list
  simdict['app_dict']    = app_dict

#  yield gen_sims_per_app( simdict )
  return simdict

def task_sim_ssa():
  yield gen_sims_per_app( simdict_ssa() )

def generate_sim_ssa():
  cores  = [ '2', '4', '8', ]

  clocks = [ '1.0GHz',
             '1.1GHz',
             '1.2GHz',
             '1.3GHz',
             '1.4GHz',
             '1.5GHz',
             '2.0GHz',
           ]

  latencies = [ '1', '2', '3', '4', ]

  for c in cores:
    for f in clocks:
      for l in latencies:
        simdict = simdict_ssa()
        simdict['basename']  += '-cores' + c + '-' + f + '-cachelatency' + l
        simdict['extra_opts'] += [ '--lane-group-size=' + c,
                                   '--cache-clock=' + f,
                                   '--cache-latency-multiplier=' + l,
                                   ]
        if   c == '2' : simdict['app_group'] = ['medium2']
        elif c == '4' : simdict['app_group'] = ['medium4']
        elif c == '8' : simdict['app_group'] = ['medium8']

        yield simdict

def task_sim_ssa_gen():
  for simdict in generate_sim_ssa():
    yield gen_sims_per_app( simdict )



