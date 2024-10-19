#============================================================================
# doit_utils
#============================================================================
# Useful functions and constructs for all doit automation files.
#
# Date   : 2019/04/08
# Author : Tuan Ta
#

import os
import commentjson
import subprocess
import math
from commons import *

#----------------------------------------------------------------------------
# Utility Functions
#----------------------------------------------------------------------------

def get_files_in_dir( path ):
  """Returns a list of all files in the given directory"""
  file_list = []
  for root, subfolders, files in os.walk( path ):
    for f in files:
      file_list.append( os.path.join( root, f ) )
  return file_list

#------------------------------------------------------------------------------
# Generate sim task
#------------------------------------------------------------------------------

def generate_sim_task(topology,
                      num_cpus,
                      injection_rate,
                      sim_cycles,
                      use_cluster       = True,
                      task_dep          = None ):

  task_name = "-".join([topology, str(num_cpus), "inj", str(injection_rate)])
  out_dir   = "{}/{}".format(simout, task_name)
  cmd = [ "/".join([topdir, "build", "NULL", "gem5.opt"] ),
          "--outdir", out_dir,
          "--redirect-stdout",
          "--redirect-stderr",
          "--stdout-file={}/stdout".format(out_dir),
          "--stderr-file={}/stderr".format(out_dir),
          "--listener-mode=off",
          "/".join([topdir, "configs", "example", "garnet_synth_traffic.py"]),
        ]
  
  cmd += [ "--num-cpus={}".format(num_cpus),
           "--network=garnet2.0",
           "--topology={}".format(topology),
           "--sim-cycles={}".format(sim_cycles),
           "--synthetic=uniform_random",
           "--injectionrate={}".format(injection_rate)
         ]

  if topology.startswith("MeshDirL2"):
    cmd += [ "--mesh-rows={}".format(int(math.sqrt(num_cpus))),
             "--num-dirs={}".format(int(math.sqrt(num_cpus))),
           ]
  elif topology.startswith("Mesh"):
    cmd += [ "--mesh-rows={}".format(int(math.sqrt(num_cpus))),
             "--num-dirs={}".format(num_cpus),
           ]
  else:
    cmd += [ "--num-dirs={}".format(num_cpus) ]

  # flatten cmd
  cmd = " ".join( cmd )

  # build task dict

  if use_cluster:
    job_func = (submit_job, [ cmd, task_name, out_dir])
  else:
    job_func = cmd

  taskdict = { "basename"  : task_name,
               "actions"   : [ "mkdir -p {}".format(simout),
                               "mkdir -p {}".format(out_dir),
                               job_func
                             ],
               "targets"   : [out_dir + "/stdout", out_dir + "/stderr"],
               "task_dep"  : task_dep,
               "clean"     : [ "rm -rf {}".format(out_dir) ]
              }

  return taskdict, task_name
