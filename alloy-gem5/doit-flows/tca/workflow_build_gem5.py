#! /usr/bin/env python
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

# Paths

topdir = '../..' # Top level gem5 dir

# Targets

gem5_targets = [
                 'opt',
                 'fast',
                 'debug',
               ]

#-----------------------------------------------------------------------------
# Build each gem5 target
#-----------------------------------------------------------------------------

def task_build_gem5():

  file_dep = get_files_in_dir( '{}/src'.format(topdir) )

  doc = os.path.basename(__file__).rstrip('c')

  for target in gem5_targets:

    action = ' '.join([ \
                        'cd {};'.format(topdir),
                        'scons',
                        'build/RISCV/gem5.{} -j64;'.format(target),
                      ])

    taskdict = { \
                 'basename' : 'build-gem5-{}'.format(target),
                 'actions'  : [ action ],
                 'targets'  : [ '{}/build/RISCV/gem5.{}'.format(topdir, target) ],
                 'file_dep' : file_dep,
                 'doc'      : doc,
                 #'clean'    : [ 'rm -rf {}/build/RISCV'.format(topdir) ],
               }

    yield taskdict

