#!/usr/bin/env python
#=========================================================================
# run-batch.py
#=========================================================================
# Run gem5 in batch. Need to provide a CSV configuration file, specifying
# options of each simulation, as the input.
#
# Author : Moyang Wang
# Date   : April 20, 2018
#

import os
import sys
import argparse
import subprocess
import multiprocessing
import clusterjob
import math
import pandas as pd
from time import localtime, strftime

from clusterjob import *

#-------------------------------------------------------------------------
# Script configs
#-------------------------------------------------------------------------

script_path = os.path.dirname(os.path.realpath(__file__))
gem5_path   = os.path.abspath(os.path.join(script_path, '..'))
verbose     = False

#-------------------------------------------------------------------------
# Shorthand
#-------------------------------------------------------------------------

abspath = os.path.abspath
dirname = os.path.dirname

#-------------------------------------------------------------------------
# Utility functions
#-------------------------------------------------------------------------

def get_mesh_rows( num_cpus ):
  mesh_rows = int(math.floor(math.sqrt(int(num_cpus))))
  if mesh_rows % 2 == 1:
    mesh_rows -= 1
    if (mesh_rows <= 0):
      mesh_rows = 1

  return str(mesh_rows)

#-------------------------------------------------------------------------
# run/execute functions
#-------------------------------------------------------------------------

# submit(cmd): takes a command and submits a job to execute it on cluster
# cmd is passed as a list of arguments

def submit(cmd,
           _jobname = 'gem5-run',
           _queue = 'batch',
           _time = '99:00:00',
           _nnodes = 1,
           _nthreads = 1,
           _mem = 8000,
           _outdir = 'qsub-out'):

  if not os.path.exists( _outdir ):
    os.mkdir( _outdir )

  jobscript = JobScript(' '.join(cmd),
                        backend = 'pbs',
                        jobname = _jobname,
                        queue   = _queue,
                        time    = _time,
                        nodes   = _nnodes,
                        threads = _nthreads,
                        mem     = _mem,
                        stdout  = _outdir + '/' + _jobname + '.out',
                        stderr  = _outdir + '/' + _jobname + '.err')
  jobscript.submit()


# execute

def execute(cmd):
  try:
    return subprocess.check_output(cmd, shell=True)
  except subprocess.CalledProcessError, err:
    print "ERROR: " + err.output


# run(cmd): takes a command and executes it natively cmd is passed as a
# list of arguments

def run(cmd):
  sys.exit(os.system(' '.join(cmd)))

#-------------------------------------------------------------------------
# CSV parsing
#-------------------------------------------------------------------------

def parse_csv( csv_file, output_root_dir, args ):

  cmd_list = []

  # default values
  experiment   = 'default'
  num_cpus     = None
  gem5_bin     = 'RISCV/gem5.opt'
  ruby         = True
  l1i_size     = '4kB'
  l1d_size     = '4kB'
  l2_size      = '512kB'
  topology     = 'Crossbar'
  link_latency = '2'
  binary_path  = ''
  binary       = None
  index        = ''
  bin_args     = None
  config       = 'configs/brg/sc3.py'
  cpu_model    = 'TimingSimpleCPU'
  mem_size     = '4GB'
  buffer_size  = '0'
  debug_flags  = ''
  debug_start  = '0'
  num_l2caches = '4'
  num_dirs     = '4'
  mesh_rows    = '1'
  mesh_columns = None

  activity_trace = False
  fast_forward = False
  active_messages = False

  df = pd.read_csv( csv_file )
  df = df.fillna('')
  df = df.applymap(str)

  outdf = df

  for i, row in df.iterrows():

    # For heterogenous system
    num_main_cpus = None
    num_tiny_cpus = None

    if ( 'experiment' in df.keys() ) and row['experiment']:
      experiment = row['experiment']
    if ( 'num-main-cpus' in df.keys() ) and row['num-main-cpus']:
      num_main_cpus = str(int(float(row['num-main-cpus'])))
    if ( 'num-tiny-cpus' in df.keys() ) and row['num-tiny-cpus']:
      num_tiny_cpus = str(int(float(row['num-tiny-cpus'])))
    if ( 'num-cpus' in df.keys() ) and row['num-cpus']:
      num_cpus = str(int(float(row['num-cpus'])))
    if ( 'gem5-bin' in df.keys() ) and row['gem5-bin']:
      gem5_bin = row['gem5-bin']
    if ( 'ruby' in df.keys() ) and row['ruby']:
      ruby = True
    if ( 'l1i-size' in df.keys() ) and row['l1i-size']:
      l1i_size = row['l1i-size']
    if ( 'l1d-size' in df.keys() ) and row['l1d-size']:
      l1d_size = row['l1d-size']
    if ( 'l2-size' in df.keys() ) and row['l2-size']:
      l2_size = row['l2-size']
    if ( 'topology' in df.keys() ) and row['topology']:
      topology = row['topology']
    if ( 'mesh-rows' in df.keys() ) and row['mesh-rows']:
      mesh_rows = row['mesh-rows']
    if ( 'mesh-columns' in df.keys() ) and row['mesh-columns']:
      mesh_columns = row['mesh-columns']
    if ( 'binary-path' in df.keys() ) and row['binary-path']:
      binary_path = row['binary-path']
    if ( 'binary' in df.keys() ) and row['binary']:
      binary = row['binary']
    if ( 'bin-args' in df.keys() ) and row['bin-args']:
      bin_args = row['bin-args']
    if ( 'index' in df.keys() ):
      index = row['index']
    if ( 'config' in df.keys() ) and row['config']:
      config = row['config']
    if ( 'cpu-model' in df.keys() ) and row['cpu-model']:
      cpu_model = row['cpu-model']
    if ( 'link-latency' in df.keys() ) and row['link-latency']:
      link_latency = row['link-latency']
    if ( 'mem-size' in df.keys() ) and row['mem-size']:
      mem_size = row['mem-size']
    if ( 'debug-start' in df.keys() ) and row['debug-start']:
      debug_start = row['debug-start']
    if ( 'buffer-size' in df.keys() ) and row['buffer-size']:
      buffer_size = str(int(float(row['buffer-size'])))
    if ( 'debug-flags' in df.keys() ) and row['debug-flags']:
      if row['debug-flags'] == 'no':
        debug_flags = ''
      else:
        debug_flags = row['debug-flags']
    if ( 'activity-trace' in df.keys() ) and row['activity-trace']:
      if row['activity-trace'] == 'yes':
        activity_trace = True
      elif row['activity-trace'] == 'no':
        activity_trace = False
    if ( 'active-messages' in df.keys() ) and row['active-messages']:
      if row['active-messages'] == 'yes':
        active_messages = True
      elif row['active-messages'] == 'no':
        active_messages = False
    if ( 'fast-forward' in df.keys() ) and row['fast-forward']:
      if row['fast-forward'] == 'no':
        fast_forward = False
      elif row['fast-forward'] == 'yes':
        fast_forward = True

    if num_cpus == None:
      if num_main_cpus and num_tiny_cpus:
        num_cpus = str( int(num_main_cpus) + int(num_tiny_cpus) )
      else:
        num_cpus = '1'
    if num_main_cpus == None:
      num_main_cpus = num_cpus
    if num_tiny_cpus == None:
      num_tiny_cpus = '0'

    assert(int(num_main_cpus) + int(num_tiny_cpus) == int(num_cpus))

    binary = os.path.join( binary_path, binary )

    if not os.path.isfile(binary):
      # if binary path is relative to gem5_path...
      binary = os.path.join( gem5_path, binary )

    # convert to absolute paths
    binary   = abspath( binary )
    gem5_bin = abspath( os.path.join( gem5_path, gem5_bin ) )
    config   = abspath( os.path.join( gem5_path, config ) )

    if not args.dry:
      # sanity check
      if not os.path.isfile( binary ):
        print "Invalid binary: " + binary
        exit(1)
      if not os.path.isfile( gem5_bin ):
        print "Invalid gem5: " + gem5_bin
        exit(1)
      if not os.path.isfile( config ):
        print "Invalid config: " + config
        exit(1)

    binary_path, binary_name = os.path.split( binary )
    if index:
      dir_name = binary_name + '-' + str( int(float(index)) )
    else:
      dir_name = binary_name
    dir_name = os.path.join( dir_name, experiment, str(num_cpus) )

    outdir = abspath( os.path.join( output_root_dir, dir_name ) )

    # create output dir if not exist
    if not args.dry:
      if not os.path.exists( outdir ):
        execute( "mkdir -p %s" % outdir )
        assert( os.path.exists( outdir ) )

    # write output dir for an app to the output dataframe
    outdf.at[index, 'outdir'] = outdir

    # gem5 command

    # general options
    cmd = [gem5_bin,
           '--debug-flags=' + debug_flags if debug_flags else '',
           ('--debug-start ' + debug_start) if int(float(debug_start)) > 0 else '',
           '--outdir=' + outdir,
           '--redirect-stdout',
           '--redirect-stderr',
           '--stdout-file=%s/%s.out' % (outdir, binary_name),
           '--stderr-file=%s/%s.err' % (outdir, binary_name),
           '--listener-mode=off',
           '--quiet',
           config,
           '--cpu-type=' + cpu_model,
           '--mem-size=' + mem_size,
           '-n ' + num_cpus,
           '-c ' + binary,
    ]

    if fast_forward:
      cmd += ['--brg-fast-forward']
    if bin_args:
      cmd += ['-o', '"' + bin_args + '"']
    if activity_trace:
      cmd += ['--activity-trace']
    if active_messages:
      cmd += ['--active-message-network']

    # ruby options
    if ruby:
      # topology-specific options
      if topology == 'MeshDirCorners_XY':
        num_dirs     = '4'
        if l2_size:
          num_l2caches = num_cpus
        mesh_rows    = get_mesh_rows(num_cpus)
        cmd += ['--mesh-rows', str(mesh_rows)]
      elif topology == 'MeshDirL2Corners_XY':
        num_dirs     = '4'
        if l2_size:
          num_l2caches = '4'
        mesh_rows    = get_mesh_rows(num_cpus)
        cmd += ['--mesh-rows', str(mesh_rows)]
      elif topology == 'BigTinyMesh':
        num_dirs = '4'
        cmd += ['--mesh-rows', str(mesh_rows),
                '--mesh-columns', str(mesh_columns)]
        cmd += ['--num-main-cpus ' + num_main_cpus,
                '--num-tiny-cpus ' + num_tiny_cpus]
      elif topology == 'Mesh_XY':
        num_dirs     = num_cpus
        if l2_size:
          num_l2caches = num_cpus
        mesh_rows    = get_mesh_rows(num_cpus)
        cmd += ['--mesh-rows', str(mesh_rows)]
      elif topology == 'Crossbar':
        # currently configure crossbar the same way as MeshDirCorners_XY
        num_dirs     = '4'
        if l2_size:
          num_l2caches = num_cpus

      cmd += ['--ruby',
              '--topology', topology,
              '--network=garnet2.0',
              '--num-dirs', num_dirs,
              '--link-latency', str( int(float(link_latency)) ),
              '--buffer-size', buffer_size,
      ]

      if num_l2caches and l2_size:
        cmd += ['--num-l2caches', num_l2caches,
                '--l2_size', l2_size,
        ]

    # classic memory options
    else:
      cmd += ['--caches']
      if l2_size:
        cmd += ['--l2cache',
                '--l2_size', l2_size,
        ]

    if l1i_size:
      cmd += ['--l1i_size', l1i_size]
    if l1d_size:
      cmd += ['--l1d_size', l1d_size]

    if verbose:
      print 'gem5 command created:'
      print '  % ' + ' '.join(cmd)
      print ''

    cmd_list.append(cmd)

  return cmd_list, outdf


#-------------------------------------------------------------------------
# Command-line options
#-------------------------------------------------------------------------

parser = argparse.ArgumentParser( description='Run gem5 simulation in batch' )
parser.add_argument( '-i', '--input',
                     help = 'Input CSV config file',
                     default = './run-batch-example.csv' )
parser.add_argument( '-o', '--output',
                     help = 'Output directory' )
parser.add_argument( '-v', '--verbose',
                     help = 'Verbose mode',
                     action = 'store_true' )
parser.add_argument( '-t', '--timestamp',
                     help = 'Add a timestamp to output directory name',
                     action = 'store_true' )
parser.add_argument( '-d', '--dry',
                     help = 'Dry run',
                     action = 'store_true' )
parser.add_argument('--qsub',
                    help = 'submit the job to BRG cluster?',
                    action = 'store_true')
parser.add_argument('--timeout',
                    help = 'per-job timeout value in seconds',
                    type = int,
                    default = -1)
args = parser.parse_args()

#-------------------------------------------------------------------------
# Main script
#-------------------------------------------------------------------------

verbose = args.verbose
if args.dry:
  verbose = True

if not os.path.isfile( args.input ):
  print "Invalid input configuration file: " + args.input
  exit(1)

input_csv = abspath( args.input )
csv_path, csv_name = os.path.split(input_csv)
csv_name = os.path.splitext(csv_name)[0]

if args.output:
  output_root = args.output
else:
  output_root = csv_name
  if args.timestamp:
    output_root += '-' + strftime("%Y-%m-%d-%H-%M", localtime())

if not args.dry:
  if not os.path.exists( output_root ):
    os.mkdir( output_root )

cmd_list, outdf = parse_csv( args.input, output_root, args )

if args.dry:
  print""
  print "Dry run finished"
  exit(0)

# create processes to run gem5

jobs = []
for i in xrange( len(cmd_list) ):
  job_name = csv_name + '-' + str(i)
  if args.qsub:
    jobs.append(multiprocessing.Process(name   = job_name,
                                        target = submit,
                                        args   = (cmd_list[i], job_name)))
  else:
    jobs.append(multiprocessing.Process(name   = job_name,
                                        target = run,
                                        args   = (cmd_list[i], )))

# running gem5

for job in jobs:
  job.start()

# wait for all jobs to complete

for job in jobs:
  if args.timeout > 0:
    job.join(args.timeout)
  else:
    job.join()

# output summary

# outdf.to_csv( os.path.join( output_root, csv_name+'-output.csv') )

