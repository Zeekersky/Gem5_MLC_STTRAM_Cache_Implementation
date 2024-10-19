#! /usr/bin/env python
#============================================================================
# verify_groups
#============================================================================
# This is a dictionary that categorizes applications according to how
# they verify.
#
# These are the groups:
#
# - 'maven' : maven-app-misc apps that use '--verify' app option
# - 'pbbs'  : pbbs apps that dump output files and then use checker scripts
#
# When verify is on, the sim commands are adjusted to verify according
# to the verification group's style. The verification group's specific
# method to print the pass/fail message for the group is used to print a
# line to the summary file.
#
# Any app that is not in verify_groups will not be verified and will
# have an "N/A" status in the summary.
#
# Date   : August 4, 2015
# Author : Christopher Torng
#

verify_groups = {

    # maven-app-misc

    'maven' : [
      'ubmark-vvadd',
      ],

}
