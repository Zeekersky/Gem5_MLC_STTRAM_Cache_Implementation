#! /usr/bin/env python
#============================================================================
# apps
#============================================================================
# This file is meant to be included in sim workflows.
#
# This file defines the app_list and app_dict:
#
# - app_list: this is the list of apps that will be simulated
# - app_dict: this dictionary contains app options for each simulation group
#
# Here is an example entry for 'bfs' in app_dict:
#
#   'bfs'                 : { 'mt'     : [ '--impl mt --warmup' ],
#                             'mtpull' : [ '--impl mtpull --warmup', ],
#                             'scalar' : [ '--impl scalar --warmup', ] },
#
# This entry describes three groups ('mt', 'mtpull', 'scalar') that
# make it easy to sim entire groups at once in a sim workflow. For
# example, "simdict['app_group'] = ['scalar']" will sim the scalar
# versions of all apps.
#
# Within each group is a list of application options. In this example,
# each app group has only one set of options. If there were multiple,
# each sim would be uniquely labeled (automatically) so that build
# directory names do not conflict.

from doit_gem5_utils import appdir, appinputdir

#----------------------------------------------------------------------------
# Application List
#----------------------------------------------------------------------------

# Use app_list to specify which of the apps in app_dict to actually sim

app_list = [
              'ubmark-vvadd',
           ]

#----------------------------------------------------------------------------
# Application Dictionary
#----------------------------------------------------------------------------

# Use app_list to specify which of the apps in app_dict to actually sim

app_dict = {
              'ubmark-vvadd'    : {
                                    'tiny'    : [ '--impl omp_static --warmup --size   256' ],
                                    'small'   : [ '--impl omp_static --warmup --size  1024' ],
                                    'medium2' : [ '--impl omp_static --warmup --size  8192' ],
                                    'medium4' : [ '--impl omp_static --warmup --size 16384' ],
                                    'medium8' : [ '--impl omp_static --warmup --size 32768' ],
                                  },
           }

