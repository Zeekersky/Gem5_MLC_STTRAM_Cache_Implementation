#!/usr/bin/env python
#==============================================================================
# Check submitted job status
#==============================================================================
#
# Author: Tuan Ta
# Date  : 19/09/13

import os
import sys
import argparse
import subprocess
import multiprocessing
import json
import xmltodict
import datetime

#-------------------------------------------------------------------------
# utility function to run a process
#-------------------------------------------------------------------------

def execute(cmd):
  try:
    return subprocess.check_output(cmd, shell=True)
  except subprocess.CalledProcessError, err:
    print "ERROR: " + err.output

#-------------------------------------------------------------------------
# Options
#-------------------------------------------------------------------------

parser = argparse.ArgumentParser(description='run gem5 simulation')
parser.add_argument( '--list-all',
                     help = 'List all jobs',
                     action = 'store_true' )
parser.add_argument( '--kill-job',
                     help = 'Kill all jobs whose names contain the target',
                     default = "" )
args = parser.parse_args()

xml_file = "{}/tmp/jobs.xml".format( os.path.expanduser("~") )

# generate XML file
execute( "qstat -x > {}".format( xml_file ) )

# load xml file
with open( xml_file, 'r' ) as f:
  xmlString = f.read()

job_list = xmltodict.parse( xmlString )[ "Data" ][ "Job" ]

#
# --list-all
#
if args.list_all:
  num_running_jobs = 0
  for job in job_list:
    if ( job[ "job_state" ] != "R" ):
      continue

    print '{:<12} {:<50} {:<3} {:<12} {:<10} {:<10}'.format( \
        job[ "Job_Id" ].split('.')[0],
        job[ "Job_Name" ],
        job[ "job_state" ],
        job[ "exec_host" ].split('.')[0],
        job[ "resources_used" ][ "walltime" ],
        job[ "resources_used" ][ "vmem" ]
      )
    num_running_jobs += 1
  print 'Total: {} running jobs'.format( num_running_jobs )

#
# --kill-job job-name
#
elif args.kill_job != "":
  for job in job_list:
    if args.kill_job in job[ "Job_Name" ]:
      execute( "qdel {}".format( job[ "Job_Id" ] ) )

#jsonString = json.dumps( xmltodict.parse( xmlString ), indent = 4 )
#
#with open( "jobs.json", "w" ) as f:
#  f.write( jsonString )
