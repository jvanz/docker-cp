#!/usr/bin/env python3

import argparse
import re
import os
import docker
import io
import tarfile
import tempfile

def copy_from_container(container, src, dest, buffer_size):
    """Method to copy file from container to local filesystem"""
    tar_name = None
    with tempfile.NamedTemporaryFile(buffering=buffer_size, prefix="dockercp", delete=False) as f:
        tar_name = f.name
        archive = container.get_archive(src)
        buff = io.BufferedRWPair(archive[0], f, buffer_size)
        while True:
            if buff.write(buff.read()) == 0:
                break
        buff.flush()
    with tarfile.open(tar_name) as tar:
        tar.extractall(path=dest)
    os.remove(tar_name)

def copy_to_container(container, src, dest, bufsize):
    """Method to copy file from local file system into container"""
    # it's necessary create a tar file with src file/directory
    archive = None
    with tempfile.NamedTemporaryFile(buffering=bufsize, prefix="dockercp", delete=False) as fp:
        with tarfile.open(mode="w:bz2",fileobj=fp, bufsize=bufsize) as tar:
            tar.add(src, arcname=os.path.basename(src))
        archive = fp.name
    # send the tar to the container
    if archive is not None:
        result = False
        with open(archive, "rb") as fp:
            result = container.put_archive(dest, io.BufferedReader(fp, buffer_size=bufsize))
        os.remove(archive)
        return result
    return False

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
