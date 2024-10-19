#============================================================================
# workflow_sim_mesi (used for granularity study)
#============================================================================
# Simulate baseline MESI with different grain size
#
# Date    : 19/08/10
# Author  : Tuan Ta

import os
from commons import *
from doit_utils import generate_sim_task

def task_sim_mesi_granularity_sweep():

  # gem5 sim parameter file

  gem5_config_file = curdir + "/gem5-configs/configs.json"

  sim_list      = []
  sim_name_list = []

  app_path = appdir + "/" + "gem5_links"

  # List of all app config files. Each config file is for one benchmark suite

  suite_json_list = [
                      #app_path + '/cilk5_apps.json',
                      app_path + '/ligra_apps.json',
                    ]

  for suite_json in suite_json_list:

#    sims, sim_names = generate_sim_task( sim_name         = "mesi-gsweep_tc",
#                                         gem5_build_name  = "RISCV_MESI_Two_Level",
#                                         config_file      = gem5_config_file,
#                                         app_file         = suite_json,
#                                         app_path         = app_path,
#                                         app_groups       = [ "tiny", "small" ],
#                                         inputs_per_group = None,
#                                         app_runtimes     = [ "applrts" ],
#                                         use_cluster      = True,
#                                         task_dep         = ["build-gem5-mesi"])
#    sim_list      = sim_list + sims
#    sim_name_list = sim_name_list + sim_names

    sims, sim_names = generate_sim_task( sim_name         = "denovo-gsweep_tc",
                                         gem5_build_name  = "RISCV_DeNovo_Two_Level",
                                         config_file      = gem5_config_file,
                                         app_file         = suite_json,
                                         app_path         = app_path,
                                         app_groups       = [ "tiny", "small" ],
                                         inputs_per_group = None,
                                         app_runtimes     = [ "applrts_sc3" ],
                                         use_cluster      = True,
                                         task_dep         = ["build-gem5-denovo"])
    sim_list      = sim_list + sims
    sim_name_list = sim_name_list + sim_names

    sims, sim_names = generate_sim_task( sim_name         = "nope-gsweep_tc",
                                         gem5_build_name  = "RISCV_NOPE_Two_Level",
                                         config_file      = gem5_config_file,
                                         app_file         = suite_json,
                                         app_path         = app_path,
                                         app_groups       = [ "tiny", "small" ],
                                         inputs_per_group = None,
                                         app_runtimes     = [ "applrts_sc3" ],
                                         use_cluster      = True,
                                         task_dep         = ["build-gem5-nope"])
    sim_list      = sim_list + sims
    sim_name_list = sim_name_list + sim_names


  # generate sims

  for sim in sim_list:
    yield sim

  yield { "basename" : "sim-gsweep_tc",
          "actions"  : None,
          "task_dep" : sim_name_list,
        }
