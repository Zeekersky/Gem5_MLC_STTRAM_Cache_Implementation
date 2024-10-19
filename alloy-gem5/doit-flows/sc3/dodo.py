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
# workflow_build_gem5
#-------------------------------------------------------------------------

from workflow_build_gem5 import *

#-------------------------------------------------------------------------
# workflow_sim
#-------------------------------------------------------------------------

from workflow_sim_serial import *

from workflow_sim_mesi import *
from workflow_sim_denovo import *
from workflow_sim_nope import *
from workflow_sim_gpuwt import *
from workflow_sim_denovo_am import *
from workflow_sim_nope_am import *
from workflow_sim_gpuwt_am import *

from workflow_sim_nope_am_tbiw import *

from workflow_sim_big_tiny_mesi import *
from workflow_sim_big_tiny_nope import *
from workflow_sim_big_tiny_denovo import *
from workflow_sim_big_tiny_gpuwt import *
from workflow_sim_big_tiny_nope_am import *
from workflow_sim_big_tiny_denovo_am import *
from workflow_sim_big_tiny_gpuwt_am import *
from workflow_sim_o3 import *

# from workflow_sim_mesi_scalar import *
# from workflow_sim_mesi_sc3 import *

from workflow_sim_mesi_granularity_sweep import *
from workflow_sim_sweep_tc import *
