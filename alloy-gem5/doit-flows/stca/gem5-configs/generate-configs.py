#!/usr/bin/env python

#==============================================================================
# generate-configs.py
#==============================================================================
# Generate gem5 configs file in json format
#
# Author: Tuan Ta
# Date  : 2019-04-04

import json
import os

#------------------------------------------------------------------------------
# Global configs dictionary. Each config has a unique name.
#------------------------------------------------------------------------------

config_dict = {}

#------------------------------------------------------------------------------
# common configs
#------------------------------------------------------------------------------

common_configs =  {
                      "--caches"      : "",
                      "--mem-size"    : "4GB"
                  }

#------------------------------------------------------------------------------
# 4 x 1-thread in-order core (io-4c-1t)
#------------------------------------------------------------------------------

config = {
            "--num-cpus"            : "4",
            "--nthreads-per-cpu"    : "1",
            "--l1i_size"            : "32kB",
            "--l1i_assoc"           : "4",
            "--l1i_mshrs"           : "4",
            "--l1d_size"            : "32kB",
            "--l1d_assoc"           : "4",
            "--l1d_mshrs"           : "4",
            "--l2cache"             : "",
            "--l2_size"             : "256kB",
         }

config.update(common_configs)
config_dict['io-4c-1t'] = config

#------------------------------------------------------------------------------
# 1 x 4-thread in-order smt core (io-1c-4t-***)
#     with different cache configs (1x, 2x, 4x)
#------------------------------------------------------------------------------

base_config = {
                  "--num-cpus"            : "1",
                  "--nthreads-per-cpu"    : "4",
                  "--l1i_mshrs"           : "4",
                  "--l1d_mshrs"           : "4",
                  "--l2cache"             : "",
                  "--l2_size"             : "256kB",
              }

cache_configs = {
                    "1xc" : ( "32kB",  "4" ),
                    "2xc" : ( "64kB",  "4" ),
                    "4xc" : ( "128kB", "4" ),
                }

for c in cache_configs:
  config = base_config.copy()
  config["--l1i_size"]  = cache_configs[c][0]
  config["--l1i_assoc"] = cache_configs[c][1]
  config["--l1d_size"]  = cache_configs[c][0]
  config["--l1d_assoc"] = cache_configs[c][1]
  config.update(common_configs)
  config_dict["io-1c-4t-{}".format(c)] = config

#------------------------------------------------------------------------------
# dump config_dict into json file
#------------------------------------------------------------------------------

dir_path = os.path.dirname(os.path.realpath(__file__))
with open("{}/configs.json".format(dir_path), "w") as out_file:
  json.dump( config_dict, out_file, sort_keys = True, indent = 4 )
