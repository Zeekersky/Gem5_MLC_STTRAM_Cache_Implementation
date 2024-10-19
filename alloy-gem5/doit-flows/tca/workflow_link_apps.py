#! /usr/bin/env python
#============================================================================
# workflow_link_apps
#============================================================================
# Doit tasks to make symbolic links to apps
#
# Date   : April 4, 2015
# Author : Christopher Torng
#
# Updated by: Tuan Ta
# Date      : June 18, 2018
#

import os
from app_paths import path_dict
from doit_gem5_utils import appdir

#............................................................................
# Paths + Tasks
#............................................................................

# Link application binaries to one directory. This uses the application
# binary paths imported from app_paths.py.

def task_link_apps():

  # Link all app binaries (i.e., files that have no extension) to one place

  action = 'mkdir -p ' + appdir + '; rm -rf ' + appdir + '/*; '

  for key in path_dict:
    path = path_dict[key]
    action += '; '.join([ 'for x in $(ls -1 ' + path + ' | grep -v -e "\.")',
                          'do ln -s ' + path + '/$x ' + appdir + ' 2> /dev/null',
                          'done; ' ])

  taskdict = { \
    'basename' : 'link-apps',
    'actions'  : [ action ],
    'uptodate' : [ False ], # always re-execute
    'doc'      : os.path.basename(__file__).rstrip('c'),
    #'clean'    : ['rm -rf ' + appdir + '/*']
    }

  yield taskdict
