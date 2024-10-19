# single tile
# 4 lanes without L0-I buffers

system_config = {
# cpu options
    "--cpu-type"          : "MinorCPU",
    "--num-cpus"          : 1,
# cpu lane options
    "--lane-group-size"   : 4,
# general cache options
    "--cacheline_size"    : 32,
# l2 options
    "--l2cache"           : True,
    "--l2_size"           : "128kB",
    "--l2_assoc"          : 8,
# l1-d options
    "--l1d_size"          : "32kB",
    "--l1d_assoc"         : 2,
# l1-i options
    "--l1i_size"          : "32kB",
    "--l1i_assoc"         : 2,
# l0-i options
    "--l0i"               : False,
    "--l0i-size"          : 1,            # in number of cache lines
}
