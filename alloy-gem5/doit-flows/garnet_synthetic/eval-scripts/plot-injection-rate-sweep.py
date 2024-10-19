#!/usr/bin/env python
from __future__ import print_function

import matplotlib.pyplot as plt
import numpy as np
import os
import argparse
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from sweep_config import *

#--------------------------------------------------------------------------
# configs
#--------------------------------------------------------------------------

topologies = [ "MeshDirL2Bottom_XY",
               "MeshDirL2Diagonal_XY"
             ]

colors = [ "#006D2C",
           "#31A354",
           "#74C476",
           "#9C661F",
           "#FF4040",
           "#DEB887",
           "#00EEEE",
           "#9932CC",
           "#FCE6C9",
           "#7FFF00",
          ]

stat_name = "system.ruby.network.average_packet_latency"

#--------------------------------------------------------------------------
# utils
#--------------------------------------------------------------------------

def get_stats(stats_file, stat_name):
    with open(stats_file, 'r') as f:
        for line in f:
            if line.startswith(stat_name):
                line = line.strip()
                l = line.split('#')[0].split()
                if len(l) == 2:
                    return float(l[1])
    return 0.0

def range_positve(start, stop=None, step=None):
    if stop == None:
        stop = start + 0.0
        start = 0.0
    if step == None:
        step = 1.0
    while start < stop:
        yield start
        start += step

#--------------------------------------------------------------------------
# plots
#--------------------------------------------------------------------------

parser = argparse.ArgumentParser(description="Create network traffic plot")
parser.add_argument('-i', '--input-dir', help="Input simout directory", default="./simout")
parser.add_argument('-o', '--output-file', help="Output plot name", default="injection-rate-sweep.pdf")
args = parser.parse_args()

plt.title("Network Injection Rate Sweep")
plt.xlabel("Injection Rate")
plt.ylabel(stat_name.split('.')[-1])

for idx, topology in enumerate(topologies):
    x = []
    y = []
    for injection_rate in range_positve(inj_start, inj_end, inj_step):
        task_name = "-".join([topology, str(num_cpus), "inj", str(injection_rate)])
        stats_file = os.path.join(args.input_dir, task_name, "stats.txt")
        val = 0
        if os.path.isfile(stats_file):
            val = get_stats(stats_file, stat_name)
        else:
            print("{} does not exist".format(stats_file))
        
        x.append(injection_rate)
        y.append(val)
    
    y = list(map(lambda x : x if x != 0 else None, y)) # filter out zero values
    plt.plot(x, y, color=colors[idx], marker='.', label=topology)

plt.legend()
plt.savefig(args.output_file)

