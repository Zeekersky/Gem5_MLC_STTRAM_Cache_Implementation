#! /usr/bin/env python
#=========================================================================
# dodo
#=========================================================================
# Doit dodo file to import workflows.
#
# Date   : April 4, 2015
# Author : Christopher Torng
#
# Updated by: Tuan Ta
# Date      : June 25, 2018
#

from doit_utils import *

#-------------------------------------------------------------------------
# Config
#-------------------------------------------------------------------------

DOIT_CONFIG = {'reporter' : MyReporter, 'verbose' : 2}

from workflow_link_apps import *

#...........................................................
# Sim workflow
#...........................................................

#from workflow_sim_io_4c import *
from workflow_sim_lane  import *