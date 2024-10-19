#============================================================================
# workflow_sim_nope
#============================================================================
# Simulate baseline NOPE
#
# Date    : 19/08/10
# Author  : Tuan Ta

import os
from commons import *
from doit_utils import generate_sim_task

def task_sim_big_tiny_denovo():

  # gem5 sim parameter file

  gem5_config_file = curdir + "/gem5-configs/configs-big-tiny.json"

  sim_list      = []
  sim_name_list = []

  app_path = appdir + "/" + "gem5_links"

  # List of all app config files. Each config file is for one benchmark suite

  suite_json_list = [ app_path + '/cilk5_apps.json',
                      app_path + '/ligra_apps.json',
                    ]

  for suite_json in suite_json_list:

    sims, sim_names = generate_sim_task( sim_name         = "big-tiny-denovo",
                                         gem5_build_name  = "RISCV_Big_Tiny_DeNovo",
                                         config_file      = gem5_config_file,
                                         app_file         = suite_json,
                                         app_path         = app_path,
                                         app_groups       = [ "small" ],
                                         inputs_per_group = 1,
                                         app_runtimes     = [ "applrts_sc3" ],
                                         use_cluster      = True,
                                         task_dep         = ["build-gem5-big-tiny-denovo"])

    sim_list      = sim_list + sims
    sim_name_list = sim_name_list + sim_names

  # generate sims

  for sim in sim_list:
    yield sim

  yield { "basename" : "sim-big-tiny-denovo",
          "actions"  : None,
          "task_dep" : sim_name_list,
        }
