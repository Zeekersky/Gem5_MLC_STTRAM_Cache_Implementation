#!/usr/bin/env python

# Copyright (c) 2018, Cornell University
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
#
# Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following
# disclaimer in the documentation and/or other materials provided
# with the distribution.
#
# Neither the name of Cornell University nor the names of its
# contributors may be used to endorse or promote products derived
# from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# Authors: Tuan Ta
#
# run-app.py is a helper script to quickly run a simulation.
#

import os
import sys
import argparse
import subprocess
import multiprocessing
import math

import clusterjob
from clusterjob import *

#-------------------------------------------------------------------------
# utility function to run a process
#-------------------------------------------------------------------------
def execute(cmd):
  try:
    return subprocess.check_output(cmd, shell=True)
  except subprocess.CalledProcessError, err:
    print "ERROR: " + err.output

#-------------------------------------------------------------------------
# submit(cmd): takes a command and submits a job to execute it on cluster
# cmd is passed as a list of arguments
#-------------------------------------------------------------------------
def submit(cmd,
           _jobname = 'gem5-run',
           _queue = 'batch',
           _time = '00:05:00',
           _nnodes = 1,
           _nthreads = 1,
           _mem = 100):

  jobscript = JobScript(' '.join(cmd),
                        backend = 'pbs',
                        jobname = _jobname,
                        queue   = _queue,
                        time    = _time,
                        nodes   = _nnodes,
                        threads = _nthreads,
                        mem     = _mem,
                        stdout  = _jobname + '.out',
                        stderr  = _jobname + '.err')
  jobscript.submit()
  sys.exit(0)

#-------------------------------------------------------------------------
# utility function to calculate the number of mesh rows
#-------------------------------------------------------------------------

def get_mesh_rows( num_cpus ):
  mesh_rows = int(math.floor(math.sqrt(int(num_cpus))))
  if mesh_rows % 2 == 1:
    mesh_rows -= 1
    if (mesh_rows <= 0):
      mesh_rows = 1

  return str(mesh_rows)

#-------------------------------------------------------------------------
# Input options
#-------------------------------------------------------------------------

# general options
parser = argparse.ArgumentParser(description='run gem5 simulation')
parser.add_argument('--arch',
                    help = 'target architecture',
                    default = 'RISCV')
parser.add_argument('--config',
                    help = 'configurations [example, brg-io]',
                    default = 'example')
parser.add_argument('--debug-flags',
                    help = 'gem5 debug flags')
parser.add_argument('--debug-start',
                    help = 'start printing debug info from Tick?',
                    type = int,
                    default = 0)
parser.add_argument('--debug-end',
                    help = 'stop printing debug info from Tick?',
                    type = int,
                    default = 0)
parser.add_argument('--max-tick',
                    help = 'maximum simulation tick',
                    type = int,
                    default = 0)
parser.add_argument('--num-cpus',
                    help = 'number of CPUs',
                    type = int,
                    default = 1)
parser.add_argument('--nthreads-per-cpu',
                    help = 'number SMT threads per CPU',
                    type = int,
                    default = 1)
parser.add_argument('--vmt',
                    action = 'store_true',
                    help = 'use VMT mode')
parser.add_argument('--binary',
                    required = True,
                    help = 'input program')
parser.add_argument('--cpu-model',
                    help = 'CPU model [AtomicSimpleCPU, TimingSimpleCPU, '\
                           'MinorCPU, DerivO3CPU]',
                    default = 'AtomicSimpleCPU')
parser.add_argument('--bin-args',
                    help = 'command line args for the program')
parser.add_argument('--gdb',
                    help = 'turn on GDB?',
                    action = 'store_true')
parser.add_argument('--valgrind',
                    help = 'turn on valgrind?',
                    action = 'store_true')
parser.add_argument('--qsub',
                    help = 'submit the job to BRG cluster?',
                    action = 'store_true')
parser.add_argument('--no-ruby',
                    help = 'Not use Ruby memory?',
                    action = 'store_true')
parser.add_argument('--topology',
                    help = 'Ruby network topology',
                    default = 'Crossbar')
parser.add_argument('--l2cache',
                    help = 'Create L2 cache?',
                    action = 'store_true')
parser.add_argument('--out-dir',
                    help = 'test output directory',
                    default = './m5out')
parser.add_argument('--l1i-size',
                    help = 'L1I size',
                    default='32kB')
parser.add_argument('--l1d-size',
                    help = 'L1D size',
                    default='32kB')
parser.add_argument('--l1i-assoc',
                    help = 'L1I size',
                    default='2')
parser.add_argument('--l1d-assoc',
                    help = 'L1D size',
                    default='2')
parser.add_argument('--l2-size',
                    help = 'L2 size',
                    default='256kB')
parser.add_argument('--mem-size',
                    help = 'Memory size',
                    default='4GB')
parser.add_argument('--activity-trace',
                    help = 'Use CPU activity trace',
                    action = 'store_true')
parser.add_argument('--debug',
                    help = 'Use gem5.debug',
                    action = 'store_true')
parser.add_argument('--redirect-outputs',
                    help = 'Redirect stdout and stderr to files',
                    action = 'store_true')
parser.add_argument('--use-min-pc',
                    help = 'Use min-pc scheme to reconverge threads',
                    action = 'store_true')
parser.add_argument('--brg-fast-forward',
                    help = 'Turn on BRG fast forward mode',
                    action = 'store_true')
parser.add_argument('--active-message-network',
                    help = 'Enable ULI network',
                    action = 'store_true')

args = parser.parse_args()

# convert all paths to absolute paths
args.binary = os.path.abspath(args.binary) if args.binary else ''
if args.bin_args != None:
  if os.path.exists(args.bin_args):
    args.bin_args = os.path.abspath(args.bin_args)
args.out_dir = os.path.abspath(args.out_dir)

#-------------------------------------------------------------------------
# gem5 variables
#-------------------------------------------------------------------------
debugging_mode = args.gdb or args.valgrind

file_path = os.path.abspath(__file__)
gem5_dir = '/'.join(file_path.split('/')[:-1])

gem5_bin = os.path.join(gem5_dir, 'build', args.arch,
                        'gem5.debug' if debugging_mode or args.debug
                                     else 'gem5.opt')
debug_flags = '--debug-flags=' + args.debug_flags \
                                  if args.debug_flags is not None else ''

config = os.path.join(gem5_dir, 'configs', 'brg', 'sc3.py')

#-------------------------------------------------------------------------
# make a job command
#-------------------------------------------------------------------------
cmd = []
cmd.append(gem5_bin)

# turn off gdb ports
cmd.append('--listener-mode=off')

if args.debug_flags != None:
  cmd.append('--debug-flags=' + args.debug_flags)

if args.debug_flags == 'O3PipeView':
  cmd.append('--debug-file=trace.out')

cmd = cmd + ['--debug-start', str(args.debug_start)]
if args.debug_end > 0:
  cmd = cmd + ['--debug-end', str(args.debug_end)]

if args.redirect_outputs:
  cmd = cmd + [ '--redirect-stdout',
                '--redirect-stderr',
                '--stdout-file={}/stdout'.format(args.out_dir),
                '--stderr-file={}/stderr'.format(args.out_dir) ]

cmd = cmd + ['--outdir', args.out_dir,
             '--listener-mode=off',
             config,
             '--cpu-type', args.cpu_model,
             '-n', str(args.num_cpus),
             '-c', args.binary,
             '--caches' if args.no_ruby else '--ruby',
             '--mem-size=' + args.mem_size,
             '--l1i_size', args.l1i_size,
             '--l1d_size', args.l1d_size,
             '--l1i_assoc', args.l1i_assoc,
             '--l1d_assoc', args.l1d_assoc,
            ]

if args.config == 'brg-io':
  cmd = cmd + ['--nthreads-per-cpu', str(args.nthreads_per_cpu),]

if args.vmt:
  cmd = cmd + ['--vmt']

if args.no_ruby:
  if args.l2cache:
    cmd = cmd + ['--l2cache']
else:
  cmd = cmd + ['--topology', args.topology]

  if args.l2cache:
    cmd = cmd + ['--l2_size', args.l2_size,
                 '--num-l2caches', str(args.num_cpus)]

  # Mesh topology
  if args.topology == 'Mesh_XY':
    cmd = cmd + ['--mesh-rows', get_mesh_rows(args.num_cpus),
                 '--num-dirs', str(args.num_cpus)
    ]
  # MeshDirCorners topology
  elif args.topology == 'MeshDirCorners_XY':
    cmd = cmd + ['--mesh-rows', get_mesh_rows(args.num_cpus),
                 '--num-dirs', '4'
    ]

if args.max_tick != None:
  cmd.append('--abs-max-tick=' + str(args.max_tick))

if args.bin_args != None:
  cmd = cmd + ['-o', args.bin_args]

if args.activity_trace:
  cmd = cmd + ['--activity-trace']

if args.use_min_pc:
  cmd = cmd + ['--use-min-pc']

if args.brg_fast_forward:
  cmd = cmd + ['--brg-fast-forward']

if args.active_message_network:
  cmd = cmd + ['--active-message-network']

if args.gdb:
  cmd = ['gdb', '--args'] + cmd
elif args.valgrind:
  cmd = ['valgrind',
         '--leak-check=full',
         '--track-origins=yes',
         '--keep-stacktraces=alloc-and-free',
         '--log-file=./valgrind.log'] + cmd

# execute cmd
output = subprocess.call(cmd)
print "Done! output = " + str(output)

if args.debug_flags == 'O3PipeView':
  pipeview_bin = os.path.join(gem5_dir, 'util', 'o3-pipeview.py')
  pipeview_input = os.path.join(gem5_dir, 'm5out', 'trace.out')
  cmd = [pipeview_bin,
         '-c', '500',
         '-o', 'pipeview.out',
         '--color', pipeview_input]
  output = subprocess.call(cmd)
