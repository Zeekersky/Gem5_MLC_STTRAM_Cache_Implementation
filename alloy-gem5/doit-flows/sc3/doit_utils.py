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

#----------------------------------------------------------------------------
# Submit tasks to cluster
#----------------------------------------------------------------------------

def submit_job( cmd, name, folder ):
  base_filename = folder + '/' + name

  with open( base_filename + ".sh", "w" ) as out:
    out.write( "#!/bin/bash\n")
    out.write( cmd + ';\n' )
  import clusterjob
  jobscript = clusterjob.JobScript(
    body     = "source " + base_filename + ".sh",
    jobname  = name,
    backend  = 'pbs',
    queue    = 'batch',
    threads  = 1,
    ppn      = 3,
    filename = base_filename + ".pbs",
    stdout   = "pbbs.out",
    stderr   = "pbbs.err",
    time     = "72:00:00",
  )
  jobscript.submit()

#------------------------------------------------------------------------------
# Generate sim task
#------------------------------------------------------------------------------
#
# A simulation task consists of all combinations of a given gem5 config list
# and app list.
#
# gem5 config list (config_dict) is in a format like this
#     { config-name : { gem5-param-name : value } }
#
# app list (app_dict) is in a format like this
#     { app-name : { app-group : [ app-param-0, app-param-1, ... ] } }
#
# This function returns a list of doit task dicts

def generate_sim_task(sim_name,
                      gem5_build_name,
                      config_file,
                      app_file,
                      app_path,
                      app_groups        = [ "tiny" ],
                      app_runtimes      = [ "serial" ],
                      inputs_per_group  = None, # by default, select all inputs
                      use_cluster       = True,
                      task_dep          = None ):

  # read in gem5 config file

  config_dict = []

  with open(config_file) as f:
    config_dict = commentjson.load(f)

  # read in app file

  app_dict = []

  with open(app_file) as f:
    app_dict = commentjson.load(f)

  # list of sim dictionaries
  sim_list  = []
  sim_names = []

  for config in config_dict:
    for app in app_dict:
      for group in app_groups:

        # extract runtime from app
        app_runtime = app.split("-")[-1]

        if app_runtime not in app_runtimes:
          continue

        gem5_config = config_dict[ config ]
        app_params  = app_dict[ app ][ group ]

        if inputs_per_group is None:
          inputs_per_group = len(app_params)

        idx = 0
        for app_param in app_params[ 0 : inputs_per_group ]:

          task_name = "-".join( [ sim_name, config, app, group, str( idx ) ] )
          out_dir   = "{}/{}".format(simout, task_name)

          cmd = [ "/".join( [ topdir, "build", gem5_build_name, "gem5.opt" ] ),
                  "--outdir", out_dir,
                  "--redirect-stdout",
                  "--redirect-stderr",
                  "--stdout-file={}/stdout".format(out_dir),
                  "--stderr-file={}/stderr".format(out_dir),
                  "--listener-mode=off",
                  "/".join( [ topdir, "configs", "brg", "sc3.py" ] ),
                ]

          for p in gem5_config:
            cmd.append( str( p ) + " " + str( gem5_config[ p ] ) )

          cmd.append( "-c {}/{}".format(app_path, app) )
          cmd.append( "-o \"{}\"".format(app_param)    )

          # flatten cmd

          cmd = " ".join( cmd )

          # build task dict

          if use_cluster:
            job_func = ( submit_job, [ cmd, task_name, out_dir ] )
          else:
            job_func = cmd

          taskdict = {  "basename"  : task_name,
                        "actions"   : [ "mkdir -p {}".format(simout),
                                        "mkdir -p {}".format(out_dir),
                                        job_func
                                      ],
                        "targets"   : [ out_dir + "/stdout", out_dir + "/stderr" ],
                        "task_dep"  : task_dep,
                        "clean"     : [ "rm -rf {}".format(out_dir) ]
                     }

          sim_list.append( taskdict )
          sim_names.append( task_name )

          idx += 1

  return sim_list, sim_names

