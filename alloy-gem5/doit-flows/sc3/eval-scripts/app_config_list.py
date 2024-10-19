#-------------------------------------------------------------------------
# List of apps
#-------------------------------------------------------------------------

app_list_cilk = [
  "cilk5-cs",
  "cilk5-lu",
  "cilk5-mm",
  "cilk5-mt",
  "cilk5-nq",
]

app_list_ligra = [
  "ligra-bc",
  "ligra-bf",
  "ligra-bfs",
  "ligra-bfsbv",
  "ligra-cc",
  "ligra-mis",
  "ligra-radii",
  "ligra-tc",
]

app_list = app_list_cilk + app_list_ligra

#-------------------------------------------------------------------------
# Short names of configurations
#-------------------------------------------------------------------------

config_list_serial = [
  'IOx1',
]

config_list_o3 = [
  'O3x1',
  'O3x4',
  'O3x8',
]

config_list_big_tiny = [
  'MESI',                 # 'MESI',
  'HCC-dnv',              # 'H-DeNovo',
  'HCC-gwt',              # 'H-GPUWT',
  'HCC-gwb',              # 'H-GPUWB',
  'HCC-DTS-dnv',          # 'H-DeNovo-DTS',
  'HCC-DTS-gwt',          # 'H-GPUWT-DTS',
  'HCC-DTS-gwb',          # 'H-GPUWB-DTS',
]

config_list_tiny = [
  'tiny-mesi-64',
  'tiny-denovo-64',
  'tiny-nope-64',
  # 'tiny-gpuwt-64',
  'tiny-denovo+uli-64',
  'tiny-nope+uli-64',
  # 'tiny-gpuwt+uli-64',
  # 'tiny-nope+uli+tbiw-64',
]

config_list_all = config_list_serial + config_list_o3 + config_list_big_tiny + config_list_tiny

#-------------------------------------------------------------------------
# Dictionaries
#-------------------------------------------------------------------------

# short name -> [config name, runtime name]
dir_name_dict = {
  'IOx1'                  : ['serial',             'serial'              ],
  'O3x1'                  : ['o3',                 'serial'              ],
  'O3x4'                  : ['o3',                 'applrts'             ],
  'O3x8'                  : ['o3x8',               'applrts'             ],
  'MESI'                     : ['big-tiny-mesi',      'applrts'             ],
  'HCC-dnv'                    : ['big-tiny-denovo',    'applrts_sc3'         ],
  'HCC-gwb'                    : ['big-tiny-nope',      'applrts_sc3'         ],
  'HCC-gwt'                    : ['big-tiny-gpuwt',     'applrts_sc3'         ],
  'HCC-DTS-dnv'                  : ['big-tiny-denovo-am', 'applrts_sc3_am'      ],
  'HCC-DTS-gwb'                  : ['big-tiny-nope-am',   'applrts_sc3_am'      ],
  'HCC-DTS-gwt'                  : ['big-tiny-gpuwt-am',  'applrts_sc3_am'      ],
  'tiny-mesi-64'          : ['mesi',               'applrts'             ],
  'tiny-denovo-64'        : ['denovo',             'applrts_sc3'         ],
  'tiny-nope-64'          : ['nope',               'applrts_sc3'         ],
  'tiny-gpuwt-64'         : ['gpuwt',              'applrts_sc3'         ],
  'tiny-denovo+uli-64'    : ['denovo-am',          'applrts_sc3_am'      ],
  'tiny-nope+uli-64'      : ['nope-am',            'applrts_sc3_am'      ],
  'tiny-gpuwt+uli-64'     : ['gpuwt-am',           'applrts_sc3_am'      ],
  'tiny-nope+uli+tbiw-64' : ['nope-am-tbiw',       'applrts_sc3_am_level'],
}

# short name -> number of cores
num_cores_dict = {
  'IOx1'                  : 1,
  'O3x1'                  : 1,
  'O3x4'                  : 4,
  'O3x8'                  : 8,
  'MESI'                  : 64,
  'HCC-dnv'               : 64,
  'HCC-gwt'               : 64,
  'HCC-gwb'               : 64,
  'HCC-DTS-dnv'           : 64,
  'HCC-DTS-gwt'           : 64,
  'HCC-DTS-gwb'           : 64,
  'tiny-mesi-64'          : 64,
  'tiny-denovo-64'        : 64,
  'tiny-nope-64'          : 64,
  'tiny-denovo+uli-64'    : 64,
  'tiny-nope+uli-64'      : 64,
  'tiny-nope+uli+tbiw-64' : 64,
}

dataset = "small-0"

