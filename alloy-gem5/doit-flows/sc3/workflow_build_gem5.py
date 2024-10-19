#============================================================================
# workflow_build_gem5
#============================================================================
# Doit tasks to build the gem5 simulator.
#
# Date   : April 4, 2015
# Author : Christopher Torng
#
# Updated by: Tuan Ta
# Date      : June 18, 2018
#

import os
from doit.task import clean_targets
from doit.tools import create_folder

from doit_utils import *

from commons import topdir

#-----------------------------------------------------------------------------
# Build each gem5 target
#-----------------------------------------------------------------------------

def task_build_gem5_MESI():

  file_dep = get_files_in_dir( '{}/src'.format(topdir) )
  gem5_bin = 'build/RISCV_MESI_Two_Level/gem5.opt'

  action = ' '.join([ 'cd {};'.format(topdir),
                      'scons',
                      '{} --default=RISCV PROTOCOL=MESI_Two_Level -j64;'.format( gem5_bin ),
                    ])

  taskdict = { 'basename' : 'build-gem5-mesi',
               'actions'  : [ action ],
               'targets'  : [ '{}/{}'.format(topdir, gem5_bin) ],
               'file_dep' : file_dep,
               'clean'    : [ 'rm -rf {}/build/RISCV_MESI_Two_Level'.format(topdir) ],
             }

  yield taskdict

def task_build_gem5_DeNovo():

  file_dep = get_files_in_dir( '{}/src'.format(topdir) )
  gem5_bin = 'build/RISCV_DeNovo_Two_Level/gem5.opt'

  action = ' '.join([ 'cd {};'.format(topdir),
                      'scons',
                      '{} --default=RISCV PROTOCOL=DeNovo_Two_Level -j64;'.format( gem5_bin ),
                    ])

  taskdict = { 'basename' : 'build-gem5-denovo',
               'actions'  : [ action ],
               'targets'  : [ '{}/{}'.format(topdir, gem5_bin) ],
               'file_dep' : file_dep,
               'clean'    : [ 'rm -rf {}/build/RISCV_DeNovo_Two_Level'.format(topdir) ],
             }

  yield taskdict

def task_build_gem5_NOPE():

  file_dep = get_files_in_dir( '{}/src'.format(topdir) )
  gem5_bin = 'build/RISCV_NOPE_Two_Level/gem5.opt'

  action = ' '.join([ 'cd {};'.format(topdir),
                      'scons',
                      '{} --default=RISCV PROTOCOL=SC3_Two_Level -j64;'.format( gem5_bin ),
                    ])

  taskdict = { 'basename' : 'build-gem5-nope',
               'actions'  : [ action ],
               'targets'  : [ '{}/{}'.format(topdir, gem5_bin) ],
               'file_dep' : file_dep,
               'clean'    : [ 'rm -rf {}/build/RISCV_NOPE_Two_Level'.format(topdir) ],
             }

  yield taskdict

def task_build_gem5_GPUWT():

  file_dep = get_files_in_dir( '{}/src'.format(topdir) )
  gem5_bin = 'build/RISCV_GPUWT_Two_Level/gem5.opt'

  action = ' '.join([ 'cd {};'.format(topdir),
                      'scons',
                      '{} --default=RISCV PROTOCOL=SC3_Two_Level_WT -j64;'.format( gem5_bin ),
                    ])

  taskdict = { 'basename' : 'build-gem5-gpuwt',
               'actions'  : [ action ],
               'targets'  : [ '{}/{}'.format(topdir, gem5_bin) ],
               'file_dep' : file_dep,
               'clean'    : [ 'rm -rf {}/build/RISCV_GPUWT_Two_Level'.format(topdir) ],
             }

  yield taskdict

def task_build_gem5_big_tiny_NOPE():

  file_dep = get_files_in_dir( '{}/src'.format(topdir) )
  gem5_bin = 'build/RISCV_Big_Tiny_NOPE/gem5.opt'

  action = ' '.join([ 'cd {};'.format(topdir),
                      'scons',
                      '{} --default=RISCV PROTOCOL=HETERO_SC3 -j64;'.format( gem5_bin ),
                    ])

  taskdict = { 'basename' : 'build-gem5-big-tiny-nope',
               'actions'  : [ action ],
               'targets'  : [ '{}/{}'.format(topdir, gem5_bin) ],
               'file_dep' : file_dep,
               'clean'    : [ 'rm -rf {}/build/RISCV_Big_Tiny_NOPE'.format(topdir) ],
             }

  yield taskdict

def task_build_gem5_big_tiny_DeNovo():

  file_dep = get_files_in_dir( '{}/src'.format(topdir) )
  gem5_bin = 'build/RISCV_Big_Tiny_DeNovo/gem5.opt'

  action = ' '.join([ 'cd {};'.format(topdir),
                      'scons',
                      '{} --default=RISCV PROTOCOL=HETERO_DeNovo -j64;'.format( gem5_bin ),
                    ])

  taskdict = { 'basename' : 'build-gem5-big-tiny-denovo',
               'actions'  : [ action ],
               'targets'  : [ '{}/{}'.format(topdir, gem5_bin) ],
               'file_dep' : file_dep,
               'clean'    : [ 'rm -rf {}/build/RISCV_Big_Tiny_DeNovo'.format(topdir) ],
             }

  yield taskdict

def task_build_gem5_big_tiny_GPUWT():

  file_dep = get_files_in_dir( '{}/src'.format(topdir) )
  gem5_bin = 'build/RISCV_Big_Tiny_GPUWT/gem5.opt'

  action = ' '.join([ 'cd {};'.format(topdir),
                      'scons',
                      '{} --default=RISCV PROTOCOL=HETERO_SC3_WT -j64;'.format( gem5_bin ),
                    ])

  taskdict = { 'basename' : 'build-gem5-big-tiny-gpuwt',
               'actions'  : [ action ],
               'targets'  : [ '{}/{}'.format(topdir, gem5_bin) ],
               'file_dep' : file_dep,
               'clean'    : [ 'rm -rf {}/build/RISCV_Big_Tiny_GPUWT'.format(topdir) ],
             }

  yield taskdict