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
    ppn      = 1,
    filename = base_filename + ".pbs",
    stdout   = "pbbs.out",
    stderr   = "pbbs.err",
    time     = "24:00:00",
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

def generate_sim_task(config_file, app_file, app_path, app_group = [ "tiny" ]):

  # read in gem5 config file

  config_dict = []

  with open(config_file) as f:
    config_dict = commentjson.load(f)

  # read in app file

  app_dict = []

  with open(app_file) as f:
    app_dict = commentjson.load(f)

  # list of sim dictionaries

  sim_list = []

  for config in config_dict:
    for app in app_dict:
      for group in app_group:

        gem5_config = config_dict[ config ]
        app_params  = app_dict[ app ][ group ]

        config_file = "/".join( [ topdir, "configs", "brg", "brg_io_configs.py" ] )

        idx = 0
        for app_param in app_params:

          task_name = "-".join( [ "sim", config, app, group, str( idx ) ] )
          out_dir   = "{}/{}".format(simout, task_name)

          cmd = [ gem5_bin,
                  "--outdir", out_dir,
                  "--redirect-stdout",
                  "--redirect-stderr",
                  "--stdout-file={}/stdout".format(out_dir),
                  "--stderr-file={}/stderr".format(out_dir),
                  config_file ]

          for p in gem5_config:
            cmd.append( str( p ) + " " + str( gem5_config[ p ] ) )

          cmd.append( "-c {}/{}".format(app_path, app) )
          cmd.append( "-o \"{}\"".format(app_param)    )

          # flatten cmd

          cmd = " ".join( cmd )

          # build task dict

          taskdict = {  "basename"  : task_name,
                        "actions"   : [ "mkdir -p {}".format(simout),
                                        "mkdir -p {}".format(out_dir),
                                        ( submit_job, [ cmd, task_name, out_dir ] )
                                      ],
                        "targets"   : [ out_dir + "/stdout", out_dir + "/stderr" ],
                        "task_dep"  : [ "build-gem5" ],
                        "clean"     : [ "rm -rf {}".format(out_dir) ]
                     }

          sim_list.append( taskdict )

          idx += 1

  return sim_list

