#============================================================================
# workflow_sim_nope_am
#============================================================================
# Simulate baseline SC3 with active message
#
# Date    : 19/08/10
# Author  : Tuan Ta

import os
from commons import *
from doit_utils import generate_sim_task

def task_sim_nope_am_tbiw():

  # gem5 sim parameter file

  gem5_config_file = curdir + "/gem5-configs/configs-am.json"

  sim_list      = []
  sim_name_list = []

  app_path = appdir + "/" + "gem5_links"

  # List of all app config files. Each config file is for one benchmark suite

  suite_json_list = [ app_path + '/cilk5_apps.json',
                      app_path + '/ligra_apps.json',
                    ]

  for suite_json in suite_json_list:

    sims, sim_names = generate_sim_task( sim_name         = "nope-am-tbiw",
                                         gem5_build_name  = "RISCV_NOPE_Two_Level",
                                         config_file      = gem5_config_file,
                                         app_file         = suite_json,
                                         app_path         = app_path,
                                         app_groups       = [ "small" ],
                                         inputs_per_group = 1,
                                         app_runtimes     = [ "applrts_sc3_am_level" ],
                                         use_cluster      = True,
                                         task_dep         = [ "build-gem5-nope" ] )

    sim_list      = sim_list + sims
    sim_name_list = sim_name_list + sim_names

  # generate sims

  for sim in sim_list:
    yield sim

  yield { "basename" : "sim-nope-am-tbiw",
          "actions"  : None,
          "task_dep" : sim_name_list,
        }
