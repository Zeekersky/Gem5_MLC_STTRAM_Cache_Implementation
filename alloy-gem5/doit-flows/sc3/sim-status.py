#!/usr/bin/env python
#==============================================================================
# sim-status.py
#==============================================================================
# View status of all simulations
#
# Author  : Tuan Ta
# Date    : 19/04/09

import os

simout_dir = os.path.abspath("./simout")

sim_list = os.listdir(simout_dir)

completed_sim_list    = []
failed_sim_list       = []
incomplete_sim_list   = []
not_started_sim_list  = []

for sim in sim_list:
  stdout_file = "/".join( [ simout_dir, sim, "stdout" ] )

  if not os.path.isfile(stdout_file):
    not_started_sim_list.append(sim)
    continue

  with open(stdout_file, 'r') as f:

    has_exit_code = False

    for line in f.readlines():
      if "Exit code" in line:
        has_exit_code = True
        code = line.split(" ")[-1]

    if not has_exit_code:
      incomplete_sim_list.append(sim)
      continue

    if code == "0\n":
      completed_sim_list.append(sim)
    else:
      failed_sim_list.append(sim)

print "-----------------------------------------"
print "Completed sims: {}".format(len(completed_sim_list))
for sim in completed_sim_list:
  print sim

print "-----------------------------------------"
print "Failed sims: {}".format(len(failed_sim_list))

for sim in failed_sim_list:
  print sim

print "-----------------------------------------"
print "Incomplete sims: {}".format(len(incomplete_sim_list))

for sim in incomplete_sim_list:
  print sim

print "-----------------------------------------"
print "Not started sims: {}".format(len(not_started_sim_list))

for sim in not_started_sim_list:
  print sim
