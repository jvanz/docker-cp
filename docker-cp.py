#!/usr/bin/env python3

import argparse
import re

path_regex = r"(?:(?P<container>\w+):)?(?P<path>(?:\.|(?:\w+|/|-)+))"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Copy files from/to Docker containers")
    parser.add_argument("-b", "--buffer-size", dest="buffer_size", type=int,
            default=128,
            help="Specify the buffer size (bytes) used to copy the to/from the container")
    parser.add_argument("src", type=str, help="Source file should be copied")
    parser.add_argument("dest", type=str, help="Destination where the file should be copy")
    args = parser.parse_args()
    print(args)
    # let's validate the paths
    if not re.match(path_regex, args.src) or not re.match(path_regex, args.dest):
        parser.print_help()
        quit(-1)
