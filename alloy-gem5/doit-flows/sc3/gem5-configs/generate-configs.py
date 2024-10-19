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
# { config_name : configs }

config_dict = {}

#------------------------------------------------------------------------------
# base_configs: dictionary of unchanged parameters
#------------------------------------------------------------------------------

base_configs = {
    "--num-cpus"          : "64",
    "--ruby"              : "",
    "--l1i_size"          : "16kB",
    "--l1d_size"          : "16kB",
    "--l2_size"           : "256kB",
    "--mem-size"          : "4GB",
    "--num-l2caches"      : "8",
    "--num-dirs"          : "8",
    "--topology"          : "MeshDirL2Bottom_XY",
    "--mesh-rows"         : "8",
    "--network"           : "garnet2.0",
    "--link-latency"      : "2",
    "--buffer-size"       : "0",
    "--brg-fast-forward"  : "",
  }

config_dict[ "*" ] = base_configs

#------------------------------------------------------------------------------
# dump config_dict into json file
#------------------------------------------------------------------------------

dir_path = os.path.dirname(os.path.realpath(__file__))
with open("{}/configs.json".format(dir_path), "w") as out_file:
  json.dump( config_dict, out_file, sort_keys = True, indent = 4 )
