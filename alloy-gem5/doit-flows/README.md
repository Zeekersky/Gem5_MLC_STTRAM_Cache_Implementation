gem5 doit workflow (v2)
=======================

Tuan Ta
June 25, 2018

## What is doit?

doit is a task management and automation tool. For more information, check
this out: http://pydoit.org/

For medium to large simulation run, we adopt doit as a tool to manage
concurrent simulation jobs effectively. This simulation workflow was initially
created by Chris Torng in BRG's deprecated gem5-mcpat. His note is a good
reference to get started with doit:
https://github.com/cornell-brg/wiki/blob/master/ctorng/2016-1026-n-l-app-gem5-tutorial.md#building-gem5-and-running-simulations

## brg_exp file structure

- README.md

- example_project/

  + This is a small example project showing how to use the tool to run a
    couple of short simulations. PLEASE DO NOT REMOVE THIS DIRECTORY. If you
    need to use the tool in your own project, please make a copy of this
    example project as your own project and modify your project directory. If
    you want to improve the workflow, please make sure that your changes in
    the example_project directory are general.

  + example_project/apps.py: list of apps
  + example_project/app_paths.py: list of paths to apps
  + example_project/dodo.py: list of simulation workflows/tasks
  + example_project/doit_gem5_utils.py: utility functions for simulation task
    creation
  + example_project/doit_utils.py: general doit utility functions
  + example_project/workflow_build_gem5.py: workflow to build gem5 binary
  + example_project/workflow_link_apps.py: workflow to make symbolic links of
    app binaries in example_project/links
  + example_project/workflow_sim_io_4c.py: an example simulation workflow to
    simulate a 4-core in-order CPU system

- [your-own-project-directory]/

  + copy and paste example_project here

