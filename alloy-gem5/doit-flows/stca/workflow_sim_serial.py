#============================================================================
# workflow_sim_serial
#============================================================================
#
# Date    : 19/04/08
# Author  : Tuan Ta
#

import os
from commons import *
from doit_utils import generate_sim_task

def task_sim_serial():

  # gem5 config file

  gem5_config_file = curdir + "/gem5-configs/serial-configs.json"

  # app_file

  app_path = "/home/qtt2/cornell-brg/apps/alloy-apps/gem5_links"
  app_file = app_path + "/ligra_apps.py"

  sim_list = generate_sim_task( gem5_config_file, app_file, app_path )

  for sim in sim_list:
    yield sim
