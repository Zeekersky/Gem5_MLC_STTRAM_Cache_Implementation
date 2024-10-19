#============================================================================
# workflow_sweep_mesh_bottom
#============================================================================

import os
from commons import *
from doit_utils import generate_sim_task
from sweep_config import *

def range_positve(start, stop=None, step=None):
    if stop == None:
        stop = start + 0.0
        start = 0.0
    if step == None:
        step = 1.0
    while start < stop:
        yield start
        start += step

def task_sweep_mesh_bottom():

  topology   = "MeshDirL2Bottom_XY"

  use_cluster = True

  # generate sims
  
  tasks      = []
  task_names = []

  for injection_rate in range_positve(inj_start, inj_end, inj_step):
      sim_task, sim_name = generate_sim_task(topology, num_cpus, injection_rate, sim_cycles, use_cluster, ["build-gem5-opt"])
      tasks.append(sim_task)
      task_names.append(sim_name)
      yield sim_task

  yield { "basename" : "sim-sweep-mesh-bottom",
          "actions"  : None,
          "task_dep" : task_names,
        }
