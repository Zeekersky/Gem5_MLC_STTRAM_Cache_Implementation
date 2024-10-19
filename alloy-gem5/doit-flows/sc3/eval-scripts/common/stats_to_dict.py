#!/usr/bin/env python
#==============================================================================
# stats_to_dict.py
#==============================================================================
# Convert gem5 stats.txt to a python dict

from __future__ import print_function

import argparse
import os
import json

def to_float_or_int(x):
    try:
        a = float(x)
        b = int(x)
        if a != b:
            return a
        else:
            return b
    except ValueError:
        return x

def add_entry(d, key_list, val):
    c = d
    for k in key_list[0:-1]:
        if k not in c:
            c[k] = {}
        c = c[k]
    c[key_list[-1]] = val
    return d

def stats_to_dict(stats_file):
    results = {}

    with open(stats_file, 'r') as f:
        for line in f:
            line = line.strip()
            l = line.split('#')[0].split()
            if len(l) != 2:
                continue
            keys = l[0]
            key_list = keys.split('.')
            val  = l[1]
            val = to_float_or_int(val)
            results = add_entry(results, key_list, val)
    return results

# standalone mode, dump into a json file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert gem5 stats.txt to a Python dict")
    parser.add_argument('-i', '--input-file', help="Input stats.txt")
    parser.add_argument('-o', '--output-file', help="Output JSON")
    args = parser.parse_args()

    d = {}

    if os.path.isfile(args.input_file):
        d = stats_to_dict(args.input_file)
    else:
        print("Input stats.txt does not exist")
        exit(1)

    if args.output_file:
        with open(args.output_file, "w") as f:
            json.dump(d, f, sort_keys=True, indent=4)
    else:
        print(json.dumps(d, sort_keys=True, indent=4))
