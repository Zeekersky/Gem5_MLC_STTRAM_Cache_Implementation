#! /usr/bin/env python
#============================================================================
# commons.py
#============================================================================
# Doit tasks to build the gem5 simulator.
#
# Author    : Tuan Ta
# Date      : Mar 8, 2019
#

import os
import clusterjob

#------------------------------------------------------------------------------
# Global vars
#------------------------------------------------------------------------------

# Paths

topdir = os.path.abspath("../..") # Top level gem5 dir
curdir = os.path.abspath("./")    # Current evaluation dir

# gem5 build target

gem5_target = "opt"

# gem5 binary and config file

gem5_bin = "{}/build/RISCV/gem5.{}".format(topdir, gem5_target)
gem5_config = "{}/configs/brg/brg_io_configs.py".format(topdir)

# sim output directory

simout = "{}/simout".format(curdir)

#----------------------------------------------------------------------------
# Submit tasks to cluster
#----------------------------------------------------------------------------

def submit_job( cmd, name, folder ):
  base_filename = folder + '/' + name

  with open( base_filename + ".sh", "w" ) as out:
    out.write( "#!/bin/bash\n")
    out.write( cmd + ';\n' )

  jobscript = \
      clusterjob.JobScript( body     = "source " + base_filename + ".sh",
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

  # submit the job to cluster
  jobscript.submit()