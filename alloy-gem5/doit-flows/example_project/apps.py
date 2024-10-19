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

from doit_gem5_utils import input_dir, ref_dir

#----------------------------------------------------------------------------
# PBBS apps
# This list should be automatically generated in PBBS app suite
#----------------------------------------------------------------------------

pbbs_app_dict = \
{
    "pbbs-bfs-deterministicBFS-riscv-cilk": {
        "medium": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_1000000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_1000000",
            " " + input_dir + "-pbbs/3Dgrid_J_1500000"
        ],
        "small": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_150000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_150000",
            " " + input_dir + "-pbbs/3Dgrid_J_200000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_10000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_10000",
            " " + input_dir + "-pbbs/3Dgrid_J_20000"
        ]
    },
    "pbbs-bfs-deterministicBFS-riscv-omp": {
        "medium": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_1000000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_1000000",
            " " + input_dir + "-pbbs/3Dgrid_J_1500000"
        ],
        "small": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_150000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_150000",
            " " + input_dir + "-pbbs/3Dgrid_J_200000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_10000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_10000",
            " " + input_dir + "-pbbs/3Dgrid_J_20000"
        ]
    },
    "pbbs-bfs-ndBFS-riscv-cilk": {
        "medium": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_1000000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_1000000",
            " " + input_dir + "-pbbs/3Dgrid_J_1500000"
        ],
        "small": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_150000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_150000",
            " " + input_dir + "-pbbs/3Dgrid_J_200000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_10000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_10000",
            " " + input_dir + "-pbbs/3Dgrid_J_20000"
        ]
    },
    "pbbs-bfs-ndBFS-riscv-omp": {
        "medium": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_1000000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_1000000",
            " " + input_dir + "-pbbs/3Dgrid_J_1500000"
        ],
        "small": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_150000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_150000",
            " " + input_dir + "-pbbs/3Dgrid_J_200000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_10000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_10000",
            " " + input_dir + "-pbbs/3Dgrid_J_20000"
        ]
    },
    "pbbs-bfs-serialBFS-riscv-serial": {
        "medium": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_1000000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_1000000",
            " " + input_dir + "-pbbs/3Dgrid_J_1500000"
        ],
        "small": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_150000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_150000",
            " " + input_dir + "-pbbs/3Dgrid_J_200000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_10000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_10000",
            " " + input_dir + "-pbbs/3Dgrid_J_20000"
        ]
    },
    "pbbs-csort-quickSort-riscv-cilk": {
        "medium": [
            " " + input_dir + "-pbbs/randomSeq_100000_double",
            " " + input_dir + "-pbbs/exptSeq_100000_double",
            " " + input_dir + "-pbbs/almostSortedSeq_100000_double",
            " " + input_dir + "-pbbs/trigramSeq_700000"
        ],
        "pydgin-enough": [
            " " + input_dir + "-pbbs/randomSeq_1000000_double",
            " " + input_dir + "-pbbs/exptSeq_1000000_double",
            " " + input_dir + "-pbbs/almostSortedSeq_1000000_double",
            " " + input_dir + "-pbbs/trigramSeq_10M"
        ],
        "small": [
            " " + input_dir + "-pbbs/randomSeq_10000_double",
            " " + input_dir + "-pbbs/exptSeq_10000_double",
            " " + input_dir + "-pbbs/almostSortedSeq_10000_double",
            " " + input_dir + "-pbbs/trigramSeq_50000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randomSeq_1000_double",
            " " + input_dir + "-pbbs/exptSeq_1000_double",
            " " + input_dir + "-pbbs/almostSortedSeq_1000_double",
            " " + input_dir + "-pbbs/trigramSeq_7000"
        ]
    },
    "pbbs-csort-sampleSort-riscv-cilk": {
        "medium": [
            " " + input_dir + "-pbbs/randomSeq_100000_double",
            " " + input_dir + "-pbbs/exptSeq_100000_double",
            " " + input_dir + "-pbbs/almostSortedSeq_100000_double",
            " " + input_dir + "-pbbs/trigramSeq_700000"
        ],
        "pydgin-enough": [
            " " + input_dir + "-pbbs/randomSeq_1000000_double",
            " " + input_dir + "-pbbs/exptSeq_1000000_double",
            " " + input_dir + "-pbbs/almostSortedSeq_1000000_double",
            " " + input_dir + "-pbbs/trigramSeq_10M"
        ],
        "small": [
            " " + input_dir + "-pbbs/randomSeq_10000_double",
            " " + input_dir + "-pbbs/exptSeq_10000_double",
            " " + input_dir + "-pbbs/almostSortedSeq_10000_double",
            " " + input_dir + "-pbbs/trigramSeq_50000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randomSeq_1000_double",
            " " + input_dir + "-pbbs/exptSeq_1000_double",
            " " + input_dir + "-pbbs/almostSortedSeq_1000_double",
            " " + input_dir + "-pbbs/trigramSeq_7000"
        ]
    },
    "pbbs-csort-sampleSort-riscv-omp": {
        "medium": [
            " " + input_dir + "-pbbs/randomSeq_100000_double",
            " " + input_dir + "-pbbs/exptSeq_100000_double",
            " " + input_dir + "-pbbs/almostSortedSeq_100000_double",
            " " + input_dir + "-pbbs/trigramSeq_700000"
        ],
        "pydgin-enough": [
            " " + input_dir + "-pbbs/randomSeq_1000000_double",
            " " + input_dir + "-pbbs/exptSeq_1000000_double",
            " " + input_dir + "-pbbs/almostSortedSeq_1000000_double",
            " " + input_dir + "-pbbs/trigramSeq_10M"
        ],
        "small": [
            " " + input_dir + "-pbbs/randomSeq_10000_double",
            " " + input_dir + "-pbbs/exptSeq_10000_double",
            " " + input_dir + "-pbbs/almostSortedSeq_10000_double",
            " " + input_dir + "-pbbs/trigramSeq_50000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randomSeq_1000_double",
            " " + input_dir + "-pbbs/exptSeq_1000_double",
            " " + input_dir + "-pbbs/almostSortedSeq_1000_double",
            " " + input_dir + "-pbbs/trigramSeq_7000"
        ]
    },
    "pbbs-csort-serialSort-riscv-serial": {
        "medium": [
            " " + input_dir + "-pbbs/randomSeq_100000_double",
            " " + input_dir + "-pbbs/exptSeq_100000_double",
            " " + input_dir + "-pbbs/almostSortedSeq_100000_double",
            " " + input_dir + "-pbbs/trigramSeq_700000"
        ],
        "small": [
            " " + input_dir + "-pbbs/randomSeq_10000_double",
            " " + input_dir + "-pbbs/exptSeq_10000_double",
            " " + input_dir + "-pbbs/almostSortedSeq_10000_double",
            " " + input_dir + "-pbbs/trigramSeq_50000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randomSeq_1000_double",
            " " + input_dir + "-pbbs/exptSeq_1000_double",
            " " + input_dir + "-pbbs/almostSortedSeq_1000_double",
            " " + input_dir + "-pbbs/trigramSeq_7000"
        ]
    },
    "pbbs-dict-deterministicHash-riscv-cilk": {
        "medium": [
            " " + input_dir + "-pbbs/randomSeq_8000000_int",
            " " + input_dir + "-pbbs/randomSeq_10M_100K_int",
            " " + input_dir + "-pbbs/exptSeq_10M_int",
            " " + input_dir + "-pbbs/trigramSeq_5000000",
            " " + input_dir + "-pbbs/trigramSeq_5000000_pair_int"
        ],
        "pydgin-enough": [
            " " + input_dir + "-pbbs/randomSeq_10M_int",
            " " + input_dir + "-pbbs/trigramSeq_10M",
            " " + input_dir + "-pbbs/trigramSeq_10M_pair_int"
        ],
        "small": [
            " " + input_dir + "-pbbs/randomSeq_800000_int",
            " " + input_dir + "-pbbs/randomSeq_800000_100K_int",
            " " + input_dir + "-pbbs/exptSeq_1000000_int",
            " " + input_dir + "-pbbs/trigramSeq_600000",
            " " + input_dir + "-pbbs/trigramSeq_600000_pair_int"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randomSeq_100000_int",
            " " + input_dir + "-pbbs/randomSeq_100000_100K_int",
            " " + input_dir + "-pbbs/exptSeq_100000_int",
            " " + input_dir + "-pbbs/trigramSeq_100000",
            " " + input_dir + "-pbbs/trigramSeq_50000_pair_int"
        ]
    },
    "pbbs-dict-deterministicHash-riscv-omp": {
        "medium": [
            " " + input_dir + "-pbbs/randomSeq_8000000_int",
            " " + input_dir + "-pbbs/randomSeq_10M_100K_int",
            " " + input_dir + "-pbbs/exptSeq_10M_int",
            " " + input_dir + "-pbbs/trigramSeq_5000000",
            " " + input_dir + "-pbbs/trigramSeq_5000000_pair_int"
        ],
        "pydgin-enough": [
            " " + input_dir + "-pbbs/randomSeq_10M_int",
            " " + input_dir + "-pbbs/trigramSeq_10M",
            " " + input_dir + "-pbbs/trigramSeq_10M_pair_int"
        ],
        "small": [
            " " + input_dir + "-pbbs/randomSeq_800000_int",
            " " + input_dir + "-pbbs/randomSeq_800000_100K_int",
            " " + input_dir + "-pbbs/exptSeq_1000000_int",
            " " + input_dir + "-pbbs/trigramSeq_600000",
            " " + input_dir + "-pbbs/trigramSeq_600000_pair_int"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randomSeq_100000_int",
            " " + input_dir + "-pbbs/randomSeq_100000_100K_int",
            " " + input_dir + "-pbbs/exptSeq_100000_int",
            " " + input_dir + "-pbbs/trigramSeq_100000",
            " " + input_dir + "-pbbs/trigramSeq_50000_pair_int"
        ]
    },
    "pbbs-dict-serialHash-riscv-serial": {
        "medium": [
            " " + input_dir + "-pbbs/randomSeq_8000000_int",
            " " + input_dir + "-pbbs/randomSeq_10M_100K_int",
            " " + input_dir + "-pbbs/exptSeq_10M_int",
            " " + input_dir + "-pbbs/trigramSeq_5000000",
            " " + input_dir + "-pbbs/trigramSeq_5000000_pair_int"
        ],
        "small": [
            " " + input_dir + "-pbbs/randomSeq_800000_int",
            " " + input_dir + "-pbbs/randomSeq_800000_100K_int",
            " " + input_dir + "-pbbs/exptSeq_1000000_int",
            " " + input_dir + "-pbbs/trigramSeq_600000",
            " " + input_dir + "-pbbs/trigramSeq_600000_pair_int"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randomSeq_100000_int",
            " " + input_dir + "-pbbs/randomSeq_100000_100K_int",
            " " + input_dir + "-pbbs/exptSeq_100000_int",
            " " + input_dir + "-pbbs/trigramSeq_100000",
            " " + input_dir + "-pbbs/trigramSeq_50000_pair_int"
        ]
    },
    "pbbs-dr-incrementalRefine-riscv-cilk": {
        "medium": [
            " " + input_dir + "-pbbs/2DkuzminDelaunay_1468",
            " " + input_dir + "-pbbs/2DinCubeDelaunay_2566"
        ]
    },
    "pbbs-dr-incrementalRefine-riscv-omp": {
        "medium": [
            " " + input_dir + "-pbbs/2DkuzminDelaunay_1468",
            " " + input_dir + "-pbbs/2DinCubeDelaunay_2566"
        ]
    },
    "pbbs-dr-serialRefine-riscv-serial": {
        "medium": [
            " " + input_dir + "-pbbs/2DkuzminDelaunay_1468",
            " " + input_dir + "-pbbs/2DinCubeDelaunay_2566"
        ]
    },
    "pbbs-dt-incrementalDelaunay-riscv-cilk": {
        "medium": [
            " " + input_dir + "-pbbs/2DinCube_5000",
            " " + input_dir + "-pbbs/2Dkuzmin_3000"
        ],
        "small": [
            " " + input_dir + "-pbbs/2DinCube_300",
            " " + input_dir + "-pbbs/2Dkuzmin_300"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/2DinCube_50",
            " " + input_dir + "-pbbs/2Dkuzmin_50"
        ]
    },
    "pbbs-dt-incrementalDelaunay-riscv-omp": {
        "medium": [
            " " + input_dir + "-pbbs/2DinCube_5000",
            " " + input_dir + "-pbbs/2Dkuzmin_3000"
        ],
        "small": [
            " " + input_dir + "-pbbs/2DinCube_300",
            " " + input_dir + "-pbbs/2Dkuzmin_300"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/2DinCube_50",
            " " + input_dir + "-pbbs/2Dkuzmin_50"
        ]
    },
    "pbbs-dt-serialDelaunay-riscv-serial": {
        "medium": [
            " " + input_dir + "-pbbs/2DinCube_5000",
            " " + input_dir + "-pbbs/2Dkuzmin_3000"
        ],
        "small": [
            " " + input_dir + "-pbbs/2DinCube_300",
            " " + input_dir + "-pbbs/2Dkuzmin_300"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/2DinCube_50",
            " " + input_dir + "-pbbs/2Dkuzmin_50"
        ]
    },
    "pbbs-hull-quickHull-riscv-cilk": {
        "medium": [
            " " + input_dir + "-pbbs/2DinSphere_40000",
            " " + input_dir + "-pbbs/2DonSphere_7000",
            " " + input_dir + "-pbbs/2Dkuzmin_50000"
        ],
        "pydgin-max": [
            " " + input_dir + "-pbbs/2DinSphere_400000",
            " " + input_dir + "-pbbs/2DonSphere_70000",
            " " + input_dir + "-pbbs/2Dkuzmin_500000"
        ],
        "small": [
            " " + input_dir + "-pbbs/2DinSphere_3500",
            " " + input_dir + "-pbbs/2DonSphere_800",
            " " + input_dir + "-pbbs/2Dkuzmin_100000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/2DinSphere_500",
            " " + input_dir + "-pbbs/2DonSphere_70",
            " " + input_dir + "-pbbs/2Dkuzmin_500"
        ]
    },
    "pbbs-hull-serialHull-riscv-serial": {
        "medium": [
            " " + input_dir + "-pbbs/2DinSphere_40000",
            " " + input_dir + "-pbbs/2DonSphere_7000",
            " " + input_dir + "-pbbs/2Dkuzmin_50000"
        ],
        "small": [
            " " + input_dir + "-pbbs/2DinSphere_3500",
            " " + input_dir + "-pbbs/2DonSphere_800",
            " " + input_dir + "-pbbs/2Dkuzmin_100000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/2DinSphere_500",
            " " + input_dir + "-pbbs/2DonSphere_70",
            " " + input_dir + "-pbbs/2Dkuzmin_500"
        ]
    },
    "pbbs-isort-blockRadixSort-riscv-cilk": {
        "medium": [
            " " + input_dir + "-pbbs/randomSeq_4000000_int",
            " " + input_dir + "-pbbs/exptSeq_2500000_int",
            " " + input_dir + "-pbbs/randomSeq_3000000_int_pair_int"
        ],
        "small": [
            " " + input_dir + "-pbbs/randomSeq_400000_int",
            " " + input_dir + "-pbbs/randomSeq_1000000_256_int_pair_int",
            " " + input_dir + "-pbbs/exptSeq_250000_int",
            " " + input_dir + "-pbbs/randomSeq_400000_int_pair_int"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randomSeq_40000_int",
            " " + input_dir + "-pbbs/randomSeq_100000_256_int_pair_int",
            " " + input_dir + "-pbbs/exptSeq_25000_int",
            " " + input_dir + "-pbbs/randomSeq_50000_int_pair_int"
        ]
    },
    "pbbs-isort-blockRadixSort-riscv-omp": {
        "medium": [
            " " + input_dir + "-pbbs/randomSeq_4000000_int",
            " " + input_dir + "-pbbs/exptSeq_2500000_int",
            " " + input_dir + "-pbbs/randomSeq_3000000_int_pair_int"
        ],
        "small": [
            " " + input_dir + "-pbbs/randomSeq_400000_int",
            " " + input_dir + "-pbbs/randomSeq_1000000_256_int_pair_int",
            " " + input_dir + "-pbbs/exptSeq_250000_int",
            " " + input_dir + "-pbbs/randomSeq_400000_int_pair_int"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randomSeq_40000_int",
            " " + input_dir + "-pbbs/randomSeq_100000_256_int_pair_int",
            " " + input_dir + "-pbbs/exptSeq_25000_int",
            " " + input_dir + "-pbbs/randomSeq_50000_int_pair_int"
        ]
    },
    "pbbs-isort-serialRadixSort-riscv-serial": {
        "medium": [
            " " + input_dir + "-pbbs/randomSeq_4000000_int",
            " " + input_dir + "-pbbs/exptSeq_2500000_int",
            " " + input_dir + "-pbbs/randomSeq_3000000_int_pair_int"
        ],
        "small": [
            " " + input_dir + "-pbbs/randomSeq_400000_int",
            " " + input_dir + "-pbbs/randomSeq_1000000_256_int_pair_int",
            " " + input_dir + "-pbbs/exptSeq_250000_int",
            " " + input_dir + "-pbbs/randomSeq_400000_int_pair_int"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randomSeq_40000_int",
            " " + input_dir + "-pbbs/randomSeq_100000_256_int_pair_int",
            " " + input_dir + "-pbbs/exptSeq_25000_int",
            " " + input_dir + "-pbbs/randomSeq_50000_int_pair_int"
        ]
    },
    "pbbs-knn-octTree2Neighbors-riscv-cilk": {
        "medium": [
            "-d 2 -k 1 " + input_dir + "-pbbs/2DinCube_50000",
            "-d 2 -k 1 " + input_dir + "-pbbs/2Dkuzmin_4000",
            "-d 3 -k 1 " + input_dir + "-pbbs/3DinCube_2500",
            "-d 3 -k 1 " + input_dir + "-pbbs/3DonSphere_3000",
            "-d 3 -k 10 " + input_dir + "-pbbs/3Dplummer_600"
        ],
        "pydgin-enough": [
            "-d 2 -k 1 " + input_dir + "-pbbs/2DinCube_50000",
            "-d 2 -k 1 " + input_dir + "-pbbs/2Dkuzmin_40000",
            "-d 3 -k 1 " + input_dir + "-pbbs/3DinCube_25000",
            "-d 3 -k 1 " + input_dir + "-pbbs/3DonSphere_30000",
            "-d 3 -k 10 " + input_dir + "-pbbs/3Dplummer_6000"
        ],
        "small": [
            "-d 2 -k 1 " + input_dir + "-pbbs/2DinCube_5000",
            "-d 2 -k 1 " + input_dir + "-pbbs/2Dkuzmin_400",
            "-d 3 -k 1 " + input_dir + "-pbbs/3DinCube_400",
            "-d 3 -k 1 " + input_dir + "-pbbs/3DonSphere_400",
            "-d 3 -k 10 " + input_dir + "-pbbs/3Dplummer_100"
        ],
        "tiny": [
            "-d 2 -k 1 " + input_dir + "-pbbs/2DinCube_100",
            "-d 2 -k 1 " + input_dir + "-pbbs/2Dkuzmin_50",
            "-d 3 -k 1 " + input_dir + "-pbbs/3DinCube_50",
            "-d 3 -k 1 " + input_dir + "-pbbs/3DonSphere_50",
            "-d 3 -k 10 " + input_dir + "-pbbs/3Dplummer_30"
        ]
    },
    "pbbs-knn-serialNeighbors-riscv-serial": {
        "medium": [
            "-d 2 -k 1 " + input_dir + "-pbbs/2DinCube_50000",
            "-d 2 -k 1 " + input_dir + "-pbbs/2Dkuzmin_4000",
            "-d 3 -k 1 " + input_dir + "-pbbs/3DinCube_2500",
            "-d 3 -k 1 " + input_dir + "-pbbs/3DonSphere_3000",
            "-d 3 -k 10 " + input_dir + "-pbbs/3Dplummer_600"
        ],
        "small": [
            "-d 2 -k 1 " + input_dir + "-pbbs/2DinCube_5000",
            "-d 2 -k 1 " + input_dir + "-pbbs/2Dkuzmin_400",
            "-d 3 -k 1 " + input_dir + "-pbbs/3DinCube_400",
            "-d 3 -k 1 " + input_dir + "-pbbs/3DonSphere_400",
            "-d 3 -k 10 " + input_dir + "-pbbs/3Dplummer_100"
        ],
        "tiny": [
            "-d 2 -k 1 " + input_dir + "-pbbs/2DinCube_100",
            "-d 2 -k 1 " + input_dir + "-pbbs/2Dkuzmin_50",
            "-d 3 -k 1 " + input_dir + "-pbbs/3DinCube_50",
            "-d 3 -k 1 " + input_dir + "-pbbs/3DonSphere_50",
            "-d 3 -k 10 " + input_dir + "-pbbs/3Dplummer_30"
        ]
    },
    "pbbs-mis-incrementalMIS-riscv-cilk": {
        "medium": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_400000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_350000",
            " " + input_dir + "-pbbs/3Dgrid_J_600000"
        ],
        "small": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_50000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_35000",
            " " + input_dir + "-pbbs/3Dgrid_J_100000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_5000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_5000",
            " " + input_dir + "-pbbs/3Dgrid_J_10000"
        ]
    },
    "pbbs-mis-incrementalMIS-riscv-omp": {
        "medium": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_400000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_350000",
            " " + input_dir + "-pbbs/3Dgrid_J_600000"
        ],
        "small": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_50000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_35000",
            " " + input_dir + "-pbbs/3Dgrid_J_100000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_5000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_5000",
            " " + input_dir + "-pbbs/3Dgrid_J_10000"
        ]
    },
    "pbbs-mis-luby-riscv-cilk": {
        "medium": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_400000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_350000",
            " " + input_dir + "-pbbs/3Dgrid_J_600000"
        ],
        "pydgin-max": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_900000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_700000",
            " " + input_dir + "-pbbs/3Dgrid_J_1000000"
        ],
        "small": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_50000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_35000",
            " " + input_dir + "-pbbs/3Dgrid_J_100000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_5000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_5000",
            " " + input_dir + "-pbbs/3Dgrid_J_10000"
        ]
    },
    "pbbs-mis-luby-riscv-omp": {
        "medium": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_400000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_350000",
            " " + input_dir + "-pbbs/3Dgrid_J_600000"
        ],
        "pydgin-max": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_900000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_700000",
            " " + input_dir + "-pbbs/3Dgrid_J_1000000"
        ],
        "small": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_50000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_35000",
            " " + input_dir + "-pbbs/3Dgrid_J_100000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_5000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_5000",
            " " + input_dir + "-pbbs/3Dgrid_J_10000"
        ]
    },
    "pbbs-mis-ndMIS-riscv-cilk": {
        "medium": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_400000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_350000",
            " " + input_dir + "-pbbs/3Dgrid_J_600000"
        ],
        "small": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_50000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_35000",
            " " + input_dir + "-pbbs/3Dgrid_J_100000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_5000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_5000",
            " " + input_dir + "-pbbs/3Dgrid_J_10000"
        ]
    },
    "pbbs-mis-ndMIS-riscv-omp": {
        "medium": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_400000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_350000",
            " " + input_dir + "-pbbs/3Dgrid_J_600000"
        ],
        "small": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_50000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_35000",
            " " + input_dir + "-pbbs/3Dgrid_J_100000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_5000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_5000",
            " " + input_dir + "-pbbs/3Dgrid_J_10000"
        ]
    },
    "pbbs-mis-serialMIS-riscv-serial": {
        "medium": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_400000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_350000",
            " " + input_dir + "-pbbs/3Dgrid_J_600000"
        ],
        "small": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_50000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_35000",
            " " + input_dir + "-pbbs/3Dgrid_J_100000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randLocalGraph_J_5_5000",
            " " + input_dir + "-pbbs/rMatGraph_J_5_5000",
            " " + input_dir + "-pbbs/3Dgrid_J_10000"
        ]
    },
    "pbbs-mm-ndMatching-riscv-cilk": {
        "medium": [
            " " + input_dir + "-pbbs/randLocalGraph_E_5_2000000",
            " " + input_dir + "-pbbs/rMatGraph_E_5_2000000",
            " " + input_dir + "-pbbs/2Dgrid_E_5000000"
        ],
        "small": [
            " " + input_dir + "-pbbs/randLocalGraph_E_5_400000",
            " " + input_dir + "-pbbs/rMatGraph_E_5_300000",
            " " + input_dir + "-pbbs/2Dgrid_E_700000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randLocalGraph_E_5_20000",
            " " + input_dir + "-pbbs/rMatGraph_E_5_20000",
            " " + input_dir + "-pbbs/2Dgrid_E_50000"
        ]
    },
    "pbbs-mm-ndMatching-riscv-omp": {
        "medium": [
            " " + input_dir + "-pbbs/randLocalGraph_E_5_2000000",
            " " + input_dir + "-pbbs/rMatGraph_E_5_2000000",
            " " + input_dir + "-pbbs/2Dgrid_E_5000000"
        ],
        "small": [
            " " + input_dir + "-pbbs/randLocalGraph_E_5_400000",
            " " + input_dir + "-pbbs/rMatGraph_E_5_300000",
            " " + input_dir + "-pbbs/2Dgrid_E_700000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randLocalGraph_E_5_20000",
            " " + input_dir + "-pbbs/rMatGraph_E_5_20000",
            " " + input_dir + "-pbbs/2Dgrid_E_50000"
        ]
    },
    "pbbs-mm-serialMatching-riscv-serial": {
        "medium": [
            " " + input_dir + "-pbbs/randLocalGraph_E_5_2000000",
            " " + input_dir + "-pbbs/rMatGraph_E_5_2000000",
            " " + input_dir + "-pbbs/2Dgrid_E_5000000"
        ],
        "small": [
            " " + input_dir + "-pbbs/randLocalGraph_E_5_400000",
            " " + input_dir + "-pbbs/rMatGraph_E_5_300000",
            " " + input_dir + "-pbbs/2Dgrid_E_700000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randLocalGraph_E_5_20000",
            " " + input_dir + "-pbbs/rMatGraph_E_5_20000",
            " " + input_dir + "-pbbs/2Dgrid_E_50000"
        ]
    },
    "pbbs-mst-parallelKruskal-riscv-cilk": {
        "medium": [
            " " + input_dir + "-pbbs/randLocalGraph_WE_5_30000",
            " " + input_dir + "-pbbs/rMatGraph_WE_5_25000",
            " " + input_dir + "-pbbs/2Dgrid_WE_50000"
        ],
        "pydgin-max": [
            " " + input_dir + "-pbbs/randLocalGraph_WE_5_500000",
            " " + input_dir + "-pbbs/rMatGraph_WE_5_500000",
            " " + input_dir + "-pbbs/2Dgrid_WE_500000"
        ],
        "small": [
            " " + input_dir + "-pbbs/randLocalGraph_WE_5_3500",
            " " + input_dir + "-pbbs/rMatGraph_WE_5_2500",
            " " + input_dir + "-pbbs/2Dgrid_WE_5000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randLocalGraph_WE_5_500",
            " " + input_dir + "-pbbs/rMatGraph_WE_5_500",
            " " + input_dir + "-pbbs/2Dgrid_WE_500"
        ]
    },
    "pbbs-mst-parallelKruskal-riscv-omp": {
        "medium": [
            " " + input_dir + "-pbbs/randLocalGraph_WE_5_30000",
            " " + input_dir + "-pbbs/rMatGraph_WE_5_25000",
            " " + input_dir + "-pbbs/2Dgrid_WE_50000"
        ],
        "pydgin-max": [
            " " + input_dir + "-pbbs/randLocalGraph_WE_5_500000",
            " " + input_dir + "-pbbs/rMatGraph_WE_5_500000",
            " " + input_dir + "-pbbs/2Dgrid_WE_500000"
        ],
        "small": [
            " " + input_dir + "-pbbs/randLocalGraph_WE_5_3500",
            " " + input_dir + "-pbbs/rMatGraph_WE_5_2500",
            " " + input_dir + "-pbbs/2Dgrid_WE_5000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randLocalGraph_WE_5_500",
            " " + input_dir + "-pbbs/rMatGraph_WE_5_500",
            " " + input_dir + "-pbbs/2Dgrid_WE_500"
        ]
    },
    "pbbs-mst-serialMST-riscv-serial": {
        "medium": [
            " " + input_dir + "-pbbs/randLocalGraph_WE_5_30000",
            " " + input_dir + "-pbbs/rMatGraph_WE_5_25000",
            " " + input_dir + "-pbbs/2Dgrid_WE_50000"
        ],
        "small": [
            " " + input_dir + "-pbbs/randLocalGraph_WE_5_3500",
            " " + input_dir + "-pbbs/rMatGraph_WE_5_2500",
            " " + input_dir + "-pbbs/2Dgrid_WE_5000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randLocalGraph_WE_5_500",
            " " + input_dir + "-pbbs/rMatGraph_WE_5_500",
            " " + input_dir + "-pbbs/2Dgrid_WE_500"
        ]
    },
    "pbbs-nbody-parallelBarnesHut-riscv-cilk": {
        "medium": [
            " " + input_dir + "-pbbs/3DonSphere_180",
            " " + input_dir + "-pbbs/3DinCube_180",
            " " + input_dir + "-pbbs/3Dplummer_180"
        ],
        "pydgin-enough": [
            " " + input_dir + "-pbbs/3DonSphere_1000",
            " " + input_dir + "-pbbs/3DinCube_1000",
            " " + input_dir + "-pbbs/3Dplummer_1000"
        ],
        "small": [
            " " + input_dir + "-pbbs/3DonSphere_80",
            " " + input_dir + "-pbbs/3DinCube_80",
            " " + input_dir + "-pbbs/3Dplummer_70"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/3DonSphere_20",
            " " + input_dir + "-pbbs/3DinCube_20",
            " " + input_dir + "-pbbs/3Dplummer_15"
        ]
    },
    "pbbs-nbody-parallelBarnesHut-riscv-omp": {
        "medium": [
            " " + input_dir + "-pbbs/3DonSphere_180",
            " " + input_dir + "-pbbs/3DinCube_180",
            " " + input_dir + "-pbbs/3Dplummer_180"
        ],
        "pydgin-enough": [
            " " + input_dir + "-pbbs/3DonSphere_1000",
            " " + input_dir + "-pbbs/3DinCube_1000",
            " " + input_dir + "-pbbs/3Dplummer_1000"
        ],
        "small": [
            " " + input_dir + "-pbbs/3DonSphere_80",
            " " + input_dir + "-pbbs/3DinCube_80",
            " " + input_dir + "-pbbs/3Dplummer_70"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/3DonSphere_20",
            " " + input_dir + "-pbbs/3DinCube_20",
            " " + input_dir + "-pbbs/3Dplummer_15"
        ]
    },
    "pbbs-nbody-serialBarnesHut-riscv-serial": {
        "medium": [
            " " + input_dir + "-pbbs/3DonSphere_180",
            " " + input_dir + "-pbbs/3DinCube_180",
            " " + input_dir + "-pbbs/3Dplummer_180"
        ],
        "pydgin-enough": [
            " " + input_dir + "-pbbs/3DonSphere_1000",
            " " + input_dir + "-pbbs/3DinCube_1000",
            " " + input_dir + "-pbbs/3Dplummer_1000"
        ],
        "small": [
            " " + input_dir + "-pbbs/3DonSphere_80",
            " " + input_dir + "-pbbs/3DinCube_80",
            " " + input_dir + "-pbbs/3Dplummer_70"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/3DonSphere_20",
            " " + input_dir + "-pbbs/3DinCube_20",
            " " + input_dir + "-pbbs/3Dplummer_15"
        ]
    },
    "pbbs-rdups-deterministicHash-riscv-cilk": {
        "medium": [
            " " + input_dir + "-pbbs/randomSeq_4000000_int",
            " " + input_dir + "-pbbs/randomSeq_4000000_100K_int",
            " " + input_dir + "-pbbs/exptSeq_3500000_int",
            " " + input_dir + "-pbbs/trigramSeq_3000000",
            " " + input_dir + "-pbbs/trigramSeq_3000000_pair_int"
        ],
        "small": [
            " " + input_dir + "-pbbs/randomSeq_400000_int",
            " " + input_dir + "-pbbs/randomSeq_400000_100K_int",
            " " + input_dir + "-pbbs/exptSeq_350000_int",
            " " + input_dir + "-pbbs/trigramSeq_300000",
            " " + input_dir + "-pbbs/trigramSeq_300000_pair_int"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randomSeq_50000_int",
            " " + input_dir + "-pbbs/randomSeq_50000_100K_int",
            " " + input_dir + "-pbbs/exptSeq_35000_int",
            " " + input_dir + "-pbbs/trigramSeq_30000",
            " " + input_dir + "-pbbs/trigramSeq_30000_pair_int"
        ]
    },
    "pbbs-rdups-deterministicHash-riscv-omp": {
        "medium": [
            " " + input_dir + "-pbbs/randomSeq_4000000_int",
            " " + input_dir + "-pbbs/randomSeq_4000000_100K_int",
            " " + input_dir + "-pbbs/exptSeq_3500000_int",
            " " + input_dir + "-pbbs/trigramSeq_3000000",
            " " + input_dir + "-pbbs/trigramSeq_3000000_pair_int"
        ],
        "small": [
            " " + input_dir + "-pbbs/randomSeq_400000_int",
            " " + input_dir + "-pbbs/randomSeq_400000_100K_int",
            " " + input_dir + "-pbbs/exptSeq_350000_int",
            " " + input_dir + "-pbbs/trigramSeq_300000",
            " " + input_dir + "-pbbs/trigramSeq_300000_pair_int"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randomSeq_50000_int",
            " " + input_dir + "-pbbs/randomSeq_50000_100K_int",
            " " + input_dir + "-pbbs/exptSeq_35000_int",
            " " + input_dir + "-pbbs/trigramSeq_30000",
            " " + input_dir + "-pbbs/trigramSeq_30000_pair_int"
        ]
    },
    "pbbs-rdups-serialHash-riscv-serial": {
        "medium": [
            " " + input_dir + "-pbbs/randomSeq_4000000_int",
            " " + input_dir + "-pbbs/randomSeq_4000000_100K_int",
            " " + input_dir + "-pbbs/exptSeq_3500000_int",
            " " + input_dir + "-pbbs/trigramSeq_3000000",
            " " + input_dir + "-pbbs/trigramSeq_3000000_pair_int"
        ],
        "small": [
            " " + input_dir + "-pbbs/randomSeq_400000_int",
            " " + input_dir + "-pbbs/randomSeq_400000_100K_int",
            " " + input_dir + "-pbbs/exptSeq_350000_int",
            " " + input_dir + "-pbbs/trigramSeq_300000",
            " " + input_dir + "-pbbs/trigramSeq_300000_pair_int"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randomSeq_50000_int",
            " " + input_dir + "-pbbs/randomSeq_50000_100K_int",
            " " + input_dir + "-pbbs/exptSeq_35000_int",
            " " + input_dir + "-pbbs/trigramSeq_30000",
            " " + input_dir + "-pbbs/trigramSeq_30000_pair_int"
        ]
    },
    "pbbs-sa-parallelRange-riscv-cilk": {
        "medium": [
            " " + input_dir + "-pbbs/trigramString_200000"
        ],
        "small": [
            " " + input_dir + "-pbbs/trigramString_120000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/trigramString_20000"
        ]
    },
    "pbbs-sa-parallelRange-riscv-omp": {
        "medium": [
            " " + input_dir + "-pbbs/trigramString_200000"
        ],
        "small": [
            " " + input_dir + "-pbbs/trigramString_120000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/trigramString_20000"
        ]
    },
    "pbbs-sa-serialKS-riscv-serial": {
        "medium": [
            " " + input_dir + "-pbbs/trigramString_200000"
        ],
        "small": [
            " " + input_dir + "-pbbs/trigramString_120000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/trigramString_20000"
        ]
    },
    "pbbs-st-incrementalST-riscv-cilk": {
        "medium": [
            " " + input_dir + "-pbbs/randLocalGraph_E_5_1000000",
            " " + input_dir + "-pbbs/rMatGraph_E_5_1000000",
            " " + input_dir + "-pbbs/2Dgrid_E_2000000"
        ],
        "pydgin-max": [
            " " + input_dir + "-pbbs/randLocalGraph_E_5_2000000",
            " " + input_dir + "-pbbs/rMatGraph_E_5_2000000",
            " " + input_dir + "-pbbs/2Dgrid_E_4000000"
        ],
        "small": [
            " " + input_dir + "-pbbs/randLocalGraph_E_5_100000",
            " " + input_dir + "-pbbs/rMatGraph_E_5_100000",
            " " + input_dir + "-pbbs/2Dgrid_E_200000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randLocalGraph_E_5_10000",
            " " + input_dir + "-pbbs/rMatGraph_E_5_10000",
            " " + input_dir + "-pbbs/2Dgrid_E_20000"
        ]
    },
    "pbbs-st-incrementalST-riscv-omp": {
        "medium": [
            " " + input_dir + "-pbbs/randLocalGraph_E_5_1000000",
            " " + input_dir + "-pbbs/rMatGraph_E_5_1000000",
            " " + input_dir + "-pbbs/2Dgrid_E_2000000"
        ],
        "pydgin-max": [
            " " + input_dir + "-pbbs/randLocalGraph_E_5_2000000",
            " " + input_dir + "-pbbs/rMatGraph_E_5_2000000",
            " " + input_dir + "-pbbs/2Dgrid_E_4000000"
        ],
        "small": [
            " " + input_dir + "-pbbs/randLocalGraph_E_5_100000",
            " " + input_dir + "-pbbs/rMatGraph_E_5_100000",
            " " + input_dir + "-pbbs/2Dgrid_E_200000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randLocalGraph_E_5_10000",
            " " + input_dir + "-pbbs/rMatGraph_E_5_10000",
            " " + input_dir + "-pbbs/2Dgrid_E_20000"
        ]
    },
    "pbbs-st-ndST-riscv-cilk": {
        "medium": [
            " " + input_dir + "-pbbs/randLocalGraph_E_5_1000000",
            " " + input_dir + "-pbbs/rMatGraph_E_5_1000000"
        ],
        "small": [
            " " + input_dir + "-pbbs/randLocalGraph_E_5_100000",
            " " + input_dir + "-pbbs/rMatGraph_E_5_100000",
            " " + input_dir + "-pbbs/2Dgrid_E_200000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randLocalGraph_E_5_10000",
            " " + input_dir + "-pbbs/rMatGraph_E_5_10000",
            " " + input_dir + "-pbbs/2Dgrid_E_20000"
        ]
    },
    "pbbs-st-ndST-riscv-omp": {
        "medium": [
            " " + input_dir + "-pbbs/randLocalGraph_E_5_1000000",
            " " + input_dir + "-pbbs/rMatGraph_E_5_1000000"
        ],
        "small": [
            " " + input_dir + "-pbbs/randLocalGraph_E_5_100000",
            " " + input_dir + "-pbbs/rMatGraph_E_5_100000",
            " " + input_dir + "-pbbs/2Dgrid_E_200000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randLocalGraph_E_5_10000",
            " " + input_dir + "-pbbs/rMatGraph_E_5_10000",
            " " + input_dir + "-pbbs/2Dgrid_E_20000"
        ]
    },
    "pbbs-st-serialST-riscv-serial": {
        "medium": [
            " " + input_dir + "-pbbs/randLocalGraph_E_5_1000000",
            " " + input_dir + "-pbbs/rMatGraph_E_5_1000000",
            " " + input_dir + "-pbbs/2Dgrid_E_2000000"
        ],
        "small": [
            " " + input_dir + "-pbbs/randLocalGraph_E_5_100000",
            " " + input_dir + "-pbbs/rMatGraph_E_5_100000",
            " " + input_dir + "-pbbs/2Dgrid_E_200000"
        ],
        "tiny": [
            " " + input_dir + "-pbbs/randLocalGraph_E_5_10000",
            " " + input_dir + "-pbbs/rMatGraph_E_5_10000",
            " " + input_dir + "-pbbs/2Dgrid_E_20000"
        ]
    }
}

# SERIAL
pbbs_app_list_serial = [
  'pbbs-bfs-serialBFS-riscv-serial',
  'pbbs-csort-serialSort-riscv-serial',
  'pbbs-dict-serialHash-riscv-serial',
  'pbbs-dr-serialRefine-riscv-serial',
  'pbbs-dt-serialDelaunay-riscv-serial',
  'pbbs-hull-serialHull-riscv-serial',
  'pbbs-isort-serialRadixSort-riscv-serial',
  'pbbs-knn-serialNeighbors-riscv-serial',
  'pbbs-mis-serialMIS-riscv-serial',
  'pbbs-mm-serialMatching-riscv-serial',
  'pbbs-mst-serialMST-riscv-serial',
  'pbbs-nbody-serialBarnesHut-riscv-serial',
  'pbbs-rdups-serialHash-riscv-serial',
  'pbbs-sa-serialKS-riscv-serial',
  'pbbs-st-serialST-riscv-serial',
]


# OPENMP
pbbs_app_list_omp = [
  'pbbs-bfs-deterministicBFS-riscv-omp',
  'pbbs-bfs-ndBFS-riscv-omp',
# FIXME memory corruption in tiny data set
#  'pbbs-csort-sampleSort-riscv-omp',
  'pbbs-dict-deterministicHash-riscv-omp',
  'pbbs-dr-incrementalRefine-riscv-omp',
  'pbbs-dt-incrementalDelaunay-riscv-omp',
  'pbbs-isort-blockRadixSort-riscv-omp',
  'pbbs-mis-incrementalMIS-riscv-omp',
  'pbbs-mis-luby-riscv-omp',
# FIXME it hangs with some tiny inputs
#  'pbbs-mis-ndMIS-riscv-omp',
  'pbbs-mm-ndMatching-riscv-omp',
  'pbbs-mst-parallelKruskal-riscv-omp',
  'pbbs-nbody-parallelBarnesHut-riscv-omp',
  'pbbs-rdups-deterministicHash-riscv-omp',
  'pbbs-sa-parallelRange-riscv-omp',
  'pbbs-st-incrementalST-riscv-omp',
  'pbbs-st-ndST-riscv-omp',
]


# CILK
pbbs_app_list_cilk = [
  'pbbs-bfs-deterministicBFS-riscv-cilk',
  'pbbs-bfs-ndBFS-riscv-cilk',
  'pbbs-csort-quickSort-riscv-cilk',
# FIXME memory corruption in tiny data set
#  'pbbs-csort-sampleSort-riscv-cilk',
  'pbbs-dict-deterministicHash-riscv-cilk',
  'pbbs-dr-incrementalRefine-riscv-cilk',
  'pbbs-dt-incrementalDelaunay-riscv-cilk',
  'pbbs-hull-quickHull-riscv-cilk',
  'pbbs-isort-blockRadixSort-riscv-cilk',
  'pbbs-knn-octTree2Neighbors-riscv-cilk',
  'pbbs-mis-incrementalMIS-riscv-cilk',
  'pbbs-mis-luby-riscv-cilk',
# FIXME it hangs with some tiny inputs
#  'pbbs-mis-ndMIS-riscv-cilk',
  'pbbs-mm-ndMatching-riscv-cilk',
  'pbbs-mst-parallelKruskal-riscv-cilk',
  'pbbs-nbody-parallelBarnesHut-riscv-cilk',
  'pbbs-rdups-deterministicHash-riscv-cilk',
  'pbbs-sa-parallelRange-riscv-cilk',
  'pbbs-st-incrementalST-riscv-cilk',
# FIXME it hangs with tiny and tiny-1 in MinorCPU
#  'pbbs-st-ndST-riscv-cilk',
]

#----------------------------------------------------------------------------
# Ligra apps
#----------------------------------------------------------------------------

ligra_app_dict = \
{
    "ligra-bc-riscv-cilk": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-bc-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-bc-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-bc-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-bc-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-bc-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-bc-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-bc-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-bc-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-bc-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-bc-riscv-omp": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-bc-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-bc-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-bc-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-bc-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-bc-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-bc-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-bc-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-bc-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-bc-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-bc-riscv-serial": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-bc-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-bc-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-bc-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-bc-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-bc-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-bc-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-bc-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-bc-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-bc-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-bf-riscv-cilk": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-bf-rMatGraph_WJ_1000000-ref -i " + input_dir + "-ligra/rMatGraph_WJ_1000000",
            " -v " + ref_dir + "-ligra/ligra-bf-randLocalGraph_WJ_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_WJ_1000000",
            " -v " + ref_dir + "-ligra/ligra-bf-3Dgrid_WJ_1500000-ref -i " + input_dir + "-ligra/3Dgrid_WJ_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-bf-rMatGraph_WJ_150000-ref -i " + input_dir + "-ligra/rMatGraph_WJ_150000",
            " -v " + ref_dir + "-ligra/ligra-bf-randLocalGraph_WJ_150000-ref -i " + input_dir + "-ligra/randLocalGraph_WJ_150000",
            " -v " + ref_dir + "-ligra/ligra-bf-3Dgrid_WJ_200000-ref -i " + input_dir + "-ligra/3Dgrid_WJ_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-bf-rMatGraph_WJ_10000-ref -i " + input_dir + "-ligra/rMatGraph_WJ_10000",
            " -v " + ref_dir + "-ligra/ligra-bf-randLocalGraph_WJ_10000-ref -i " + input_dir + "-ligra/randLocalGraph_WJ_10000",
            " -v " + ref_dir + "-ligra/ligra-bf-3Dgrid_WJ_20000-ref -i " + input_dir + "-ligra/3Dgrid_WJ_20000"
        ]
    },
    "ligra-bf-riscv-omp": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-bf-rMatGraph_WJ_1000000-ref -i " + input_dir + "-ligra/rMatGraph_WJ_1000000",
            " -v " + ref_dir + "-ligra/ligra-bf-randLocalGraph_WJ_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_WJ_1000000",
            " -v " + ref_dir + "-ligra/ligra-bf-3Dgrid_WJ_1500000-ref -i " + input_dir + "-ligra/3Dgrid_WJ_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-bf-rMatGraph_WJ_150000-ref -i " + input_dir + "-ligra/rMatGraph_WJ_150000",
            " -v " + ref_dir + "-ligra/ligra-bf-randLocalGraph_WJ_150000-ref -i " + input_dir + "-ligra/randLocalGraph_WJ_150000",
            " -v " + ref_dir + "-ligra/ligra-bf-3Dgrid_WJ_200000-ref -i " + input_dir + "-ligra/3Dgrid_WJ_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-bf-rMatGraph_WJ_10000-ref -i " + input_dir + "-ligra/rMatGraph_WJ_10000",
            " -v " + ref_dir + "-ligra/ligra-bf-randLocalGraph_WJ_10000-ref -i " + input_dir + "-ligra/randLocalGraph_WJ_10000",
            " -v " + ref_dir + "-ligra/ligra-bf-3Dgrid_WJ_20000-ref -i " + input_dir + "-ligra/3Dgrid_WJ_20000"
        ]
    },
    "ligra-bf-riscv-serial": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-bf-rMatGraph_WJ_1000000-ref -i " + input_dir + "-ligra/rMatGraph_WJ_1000000",
            " -v " + ref_dir + "-ligra/ligra-bf-randLocalGraph_WJ_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_WJ_1000000",
            " -v " + ref_dir + "-ligra/ligra-bf-3Dgrid_WJ_1500000-ref -i " + input_dir + "-ligra/3Dgrid_WJ_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-bf-rMatGraph_WJ_150000-ref -i " + input_dir + "-ligra/rMatGraph_WJ_150000",
            " -v " + ref_dir + "-ligra/ligra-bf-randLocalGraph_WJ_150000-ref -i " + input_dir + "-ligra/randLocalGraph_WJ_150000",
            " -v " + ref_dir + "-ligra/ligra-bf-3Dgrid_WJ_200000-ref -i " + input_dir + "-ligra/3Dgrid_WJ_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-bf-rMatGraph_WJ_10000-ref -i " + input_dir + "-ligra/rMatGraph_WJ_10000",
            " -v " + ref_dir + "-ligra/ligra-bf-randLocalGraph_WJ_10000-ref -i " + input_dir + "-ligra/randLocalGraph_WJ_10000",
            " -v " + ref_dir + "-ligra/ligra-bf-3Dgrid_WJ_20000-ref -i " + input_dir + "-ligra/3Dgrid_WJ_20000"
        ]
    },
    "ligra-bfs-riscv-cilk": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-bfs-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-bfs-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-bfs-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-bfs-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-bfs-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-bfs-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-bfs-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-bfs-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-bfs-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-bfs-riscv-omp": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-bfs-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-bfs-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-bfs-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-bfs-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-bfs-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-bfs-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-bfs-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-bfs-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-bfs-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-bfs-riscv-serial": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-bfs-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-bfs-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-bfs-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-bfs-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-bfs-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-bfs-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-bfs-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-bfs-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-bfs-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-bfsbv-riscv-cilk": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-bfsbv-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-bfsbv-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-bfsbv-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-bfsbv-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-bfsbv-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-bfsbv-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-bfsbv-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-bfsbv-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-bfsbv-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-bfsbv-riscv-omp": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-bfsbv-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-bfsbv-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-bfsbv-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-bfsbv-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-bfsbv-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-bfsbv-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-bfsbv-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-bfsbv-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-bfsbv-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-bfsbv-riscv-serial": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-bfsbv-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-bfsbv-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-bfsbv-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-bfsbv-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-bfsbv-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-bfsbv-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-bfsbv-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-bfsbv-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-bfsbv-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-bfscc-riscv-cilk": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-bfscc-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-bfscc-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-bfscc-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-bfscc-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-bfscc-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-bfscc-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-bfscc-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-bfscc-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-bfscc-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-bfscc-riscv-omp": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-bfscc-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-bfscc-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-bfscc-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-bfscc-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-bfscc-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-bfscc-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-bfscc-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-bfscc-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-bfscc-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-bfscc-riscv-serial": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-bfscc-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-bfscc-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-bfscc-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-bfscc-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-bfscc-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-bfscc-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-bfscc-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-bfscc-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-bfscc-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-cc-riscv-cilk": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-cc-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-cc-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-cc-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-cc-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-cc-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-cc-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-cc-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-cc-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-cc-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-cc-riscv-omp": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-cc-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-cc-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-cc-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-cc-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-cc-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-cc-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-cc-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-cc-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-cc-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-cc-riscv-serial": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-cc-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-cc-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-cc-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-cc-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-cc-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-cc-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-cc-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-cc-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-cc-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-cf-riscv-cilk": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-cf-rMatGraph_WJ_1000000-ref -i " + input_dir + "-ligra/rMatGraph_WJ_1000000",
            " -v " + ref_dir + "-ligra/ligra-cf-randLocalGraph_WJ_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_WJ_1000000",
            " -v " + ref_dir + "-ligra/ligra-cf-3Dgrid_WJ_1500000-ref -i " + input_dir + "-ligra/3Dgrid_WJ_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-cf-rMatGraph_WJ_150000-ref -i " + input_dir + "-ligra/rMatGraph_WJ_150000",
            " -v " + ref_dir + "-ligra/ligra-cf-randLocalGraph_WJ_150000-ref -i " + input_dir + "-ligra/randLocalGraph_WJ_150000",
            " -v " + ref_dir + "-ligra/ligra-cf-3Dgrid_WJ_200000-ref -i " + input_dir + "-ligra/3Dgrid_WJ_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-cf-rMatGraph_WJ_10000-ref -i " + input_dir + "-ligra/rMatGraph_WJ_10000",
            " -v " + ref_dir + "-ligra/ligra-cf-randLocalGraph_WJ_10000-ref -i " + input_dir + "-ligra/randLocalGraph_WJ_10000",
            " -v " + ref_dir + "-ligra/ligra-cf-3Dgrid_WJ_20000-ref -i " + input_dir + "-ligra/3Dgrid_WJ_20000"
        ]
    },
    "ligra-cf-riscv-omp": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-cf-rMatGraph_WJ_1000000-ref -i " + input_dir + "-ligra/rMatGraph_WJ_1000000",
            " -v " + ref_dir + "-ligra/ligra-cf-randLocalGraph_WJ_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_WJ_1000000",
            " -v " + ref_dir + "-ligra/ligra-cf-3Dgrid_WJ_1500000-ref -i " + input_dir + "-ligra/3Dgrid_WJ_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-cf-rMatGraph_WJ_150000-ref -i " + input_dir + "-ligra/rMatGraph_WJ_150000",
            " -v " + ref_dir + "-ligra/ligra-cf-randLocalGraph_WJ_150000-ref -i " + input_dir + "-ligra/randLocalGraph_WJ_150000",
            " -v " + ref_dir + "-ligra/ligra-cf-3Dgrid_WJ_200000-ref -i " + input_dir + "-ligra/3Dgrid_WJ_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-cf-rMatGraph_WJ_10000-ref -i " + input_dir + "-ligra/rMatGraph_WJ_10000",
            " -v " + ref_dir + "-ligra/ligra-cf-randLocalGraph_WJ_10000-ref -i " + input_dir + "-ligra/randLocalGraph_WJ_10000",
            " -v " + ref_dir + "-ligra/ligra-cf-3Dgrid_WJ_20000-ref -i " + input_dir + "-ligra/3Dgrid_WJ_20000"
        ]
    },
    "ligra-cf-riscv-serial": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-cf-rMatGraph_WJ_1000000-ref -i " + input_dir + "-ligra/rMatGraph_WJ_1000000",
            " -v " + ref_dir + "-ligra/ligra-cf-randLocalGraph_WJ_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_WJ_1000000",
            " -v " + ref_dir + "-ligra/ligra-cf-3Dgrid_WJ_1500000-ref -i " + input_dir + "-ligra/3Dgrid_WJ_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-cf-rMatGraph_WJ_150000-ref -i " + input_dir + "-ligra/rMatGraph_WJ_150000",
            " -v " + ref_dir + "-ligra/ligra-cf-randLocalGraph_WJ_150000-ref -i " + input_dir + "-ligra/randLocalGraph_WJ_150000",
            " -v " + ref_dir + "-ligra/ligra-cf-3Dgrid_WJ_200000-ref -i " + input_dir + "-ligra/3Dgrid_WJ_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-cf-rMatGraph_WJ_10000-ref -i " + input_dir + "-ligra/rMatGraph_WJ_10000",
            " -v " + ref_dir + "-ligra/ligra-cf-randLocalGraph_WJ_10000-ref -i " + input_dir + "-ligra/randLocalGraph_WJ_10000",
            " -v " + ref_dir + "-ligra/ligra-cf-3Dgrid_WJ_20000-ref -i " + input_dir + "-ligra/3Dgrid_WJ_20000"
        ]
    },
    "ligra-kcore-riscv-cilk": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-kcore-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-kcore-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-kcore-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-kcore-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-kcore-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-kcore-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-kcore-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-kcore-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-kcore-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-kcore-riscv-omp": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-kcore-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-kcore-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-kcore-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-kcore-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-kcore-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-kcore-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-kcore-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-kcore-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-kcore-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-kcore-riscv-serial": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-kcore-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-kcore-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-kcore-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-kcore-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-kcore-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-kcore-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-kcore-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-kcore-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-kcore-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-mis-riscv-cilk": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-mis-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-mis-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-mis-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-mis-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-mis-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-mis-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-mis-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-mis-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-mis-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-mis-riscv-omp": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-mis-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-mis-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-mis-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-mis-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-mis-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-mis-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-mis-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-mis-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-mis-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-mis-riscv-serial": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-mis-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-mis-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-mis-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-mis-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-mis-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-mis-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-mis-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-mis-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-mis-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-pr-riscv-cilk": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-pr-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-pr-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-pr-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-pr-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-pr-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-pr-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-pr-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-pr-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-pr-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-pr-riscv-omp": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-pr-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-pr-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-pr-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-pr-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-pr-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-pr-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-pr-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-pr-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-pr-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-pr-riscv-serial": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-pr-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-pr-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-pr-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-pr-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-pr-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-pr-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-pr-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-pr-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-pr-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-prd-riscv-cilk": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-prd-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-prd-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-prd-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-prd-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-prd-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-prd-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-prd-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-prd-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-prd-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-prd-riscv-omp": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-prd-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-prd-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-prd-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-prd-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-prd-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-prd-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-prd-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-prd-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-prd-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-prd-riscv-serial": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-prd-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-prd-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-prd-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-prd-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-prd-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-prd-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-prd-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-prd-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-prd-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-radii-riscv-cilk": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-radii-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-radii-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-radii-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-radii-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-radii-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-radii-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-radii-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-radii-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-radii-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-radii-riscv-omp": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-radii-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-radii-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-radii-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-radii-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-radii-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-radii-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-radii-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-radii-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-radii-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-radii-riscv-serial": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-radii-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-radii-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-radii-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-radii-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-radii-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-radii-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-radii-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-radii-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-radii-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-tc-riscv-cilk": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-tc-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-tc-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-tc-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-tc-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-tc-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-tc-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-tc-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-tc-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-tc-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-tc-riscv-omp": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-tc-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-tc-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-tc-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-tc-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-tc-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-tc-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-tc-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-tc-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-tc-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    },
    "ligra-tc-riscv-serial": {
        "medium": [
            " -v " + ref_dir + "-ligra/ligra-tc-rMatGraph_J_1000000-ref -i " + input_dir + "-ligra/rMatGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-tc-randLocalGraph_J_1000000-ref -i " + input_dir + "-ligra/randLocalGraph_J_1000000",
            " -v " + ref_dir + "-ligra/ligra-tc-3Dgrid_J_1500000-ref -i " + input_dir + "-ligra/3Dgrid_J_1500000"
        ],
        "small": [
            " -v " + ref_dir + "-ligra/ligra-tc-rMatGraph_J_150000-ref -i " + input_dir + "-ligra/rMatGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-tc-randLocalGraph_J_150000-ref -i " + input_dir + "-ligra/randLocalGraph_J_150000",
            " -v " + ref_dir + "-ligra/ligra-tc-3Dgrid_J_200000-ref -i " + input_dir + "-ligra/3Dgrid_J_200000"
        ],
        "tiny": [
            " -v " + ref_dir + "-ligra/ligra-tc-rMatGraph_J_10000-ref -i " + input_dir + "-ligra/rMatGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-tc-randLocalGraph_J_10000-ref -i " + input_dir + "-ligra/randLocalGraph_J_10000",
            " -v " + ref_dir + "-ligra/ligra-tc-3Dgrid_J_20000-ref -i " + input_dir + "-ligra/3Dgrid_J_20000"
        ]
    }
}

# SERIAL
ligra_app_list_serial = [
  'ligra-bc-riscv-serial',
  'ligra-bf-riscv-serial',
  'ligra-bfs-riscv-serial',
  'ligra-bfsbv-riscv-serial',
  'ligra-bfscc-riscv-serial',
  'ligra-cc-riscv-serial',
  'ligra-cf-riscv-serial',
  'ligra-kcore-riscv-serial',
  'ligra-mis-riscv-serial',
  'ligra-pr-riscv-serial',
  'ligra-prd-riscv-serial',
  'ligra-radii-riscv-serial',
  'ligra-tc-riscv-serial',
]


# OPENMP
ligra_app_list_omp = [
  'ligra-bc-riscv-omp',
  'ligra-bf-riscv-omp',
  'ligra-bfs-riscv-omp',
  'ligra-bfsbv-riscv-omp',
  'ligra-bfscc-riscv-omp',
  'ligra-cc-riscv-omp',
  'ligra-cf-riscv-omp',
  'ligra-kcore-riscv-omp',
  'ligra-mis-riscv-omp',
  'ligra-pr-riscv-omp',
  'ligra-prd-riscv-omp',
  'ligra-radii-riscv-omp',
  'ligra-tc-riscv-omp',
]


# CILK
ligra_app_list_cilk = [
  'ligra-bc-riscv-cilk',
  'ligra-bf-riscv-cilk',
  'ligra-bfs-riscv-cilk',
  'ligra-bfsbv-riscv-cilk',
  'ligra-bfscc-riscv-cilk',
  'ligra-cc-riscv-cilk',
  'ligra-cf-riscv-cilk',
  'ligra-kcore-riscv-cilk',
  'ligra-mis-riscv-cilk',
  'ligra-pr-riscv-cilk',
  'ligra-prd-riscv-cilk',
  'ligra-radii-riscv-cilk',
  'ligra-tc-riscv-cilk',
]


#----------------------------------------------------------------------------
# TODO ubmark apps
#----------------------------------------------------------------------------

#----------------------------------------------------------------------------
# App selection for gem5 simulation
#----------------------------------------------------------------------------

#app_list = pbbs_app_list_serial + pbbs_app_list_omp + pbbs_app_list_cilk
#app_dict = pbbs_app_dict

app_list = ligra_app_list_serial + ligra_app_list_omp + ligra_app_list_cilk
app_dict = ligra_app_dict
