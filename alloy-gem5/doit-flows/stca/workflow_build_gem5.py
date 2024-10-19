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

from commons import topdir, gem5_target

#-----------------------------------------------------------------------------
# Build each gem5 target
#-----------------------------------------------------------------------------

def task_build_gem5():

  file_dep = get_files_in_dir( '{}/src'.format(topdir) )

#  doc = os.path.basename(__file__).rstrip('c')

  action = ' '.join([ 'cd {};'.format(topdir),
                      'scons',
                      'build/RISCV/gem5.{} -j64;'.format(gem5_target),
                    ])

  taskdict = { 'basename' : 'build-gem5',
               'actions'  : [ action ],
               'targets'  : [ '{}/build/RISCV/gem5.{}'.format(topdir, gem5_target) ],
               'file_dep' : file_dep,
               'clean'    : [ 'rm -rf {}/build/RISCV'.format(topdir) ],
             }

  yield taskdict
