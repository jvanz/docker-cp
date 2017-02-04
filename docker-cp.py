#!/usr/bin/env python3

import argparse
import os
import docker
import tarfile
from io import BufferedRWPair, BufferedReader, DEFAULT_BUFFER_SIZE
from tempfile import NamedTemporaryFile
from re import compile

pathre = compile(r"^(?:(?P<container>\w+):)?(?P<path>\.?(?:/?[\w\-_\.]+)+/?)$")

def copy_from_container(container, src, dest, buffer_size):
    """Method to copy file from container to local filesystem"""
    tar_name = None
    with NamedTemporaryFile(buffering=buffer_size, prefix="dockercp", delete=False) as f:
        tar_name = f.name
        archive = container.get_archive(src)
        buff = BufferedRWPair(archive[0], f, buffer_size)
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
    with NamedTemporaryFile(buffering=bufsize, prefix="dockercp", delete=False) as fp:
        with tarfile.open(mode="w:bz2",fileobj=fp, bufsize=bufsize) as tar:
            tar.add(src, arcname=os.path.basename(src))
        archive = fp.name
    # send the tar to the container
    if archive is not None:
        result = False
        with open(archive, "rb") as fp:
            result = container.put_archive(dest, BufferedReader(fp, buffer_size=bufsize))
        os.remove(archive)
        return result
    return False

def leave(code, msg):
    """Print the msg and quit the program"""
    print(msg)
    print("Use the -h options to see how the usage help")
    quit(code)

if __name__ == "__main__":
    # First we validate all the command line arguments
    parser = argparse.ArgumentParser(description="Copy files from/to Docker containers")
    parser.add_argument("-b", "--buffer-size", dest="buffer_size", type=int,
            default=DEFAULT_BUFFER_SIZE,
            help="Specify the buffer size (bytes) used to copy the to/from the container")
    parser.add_argument("src", type=str, help="Source file should be copied")
    parser.add_argument("dest", type=str, help="Destination where the file should be copy")
    args = parser.parse_args()

    # let's validate the paths
    if not pathre.fullmatch(args.src) or not pathre.fullmatch(args.dest):
        leave(-1, "Invalid paths.")
    if pathre.match(args.src).group("container") is None and pathre.match(args.dest).group("container") is None:
        # at least one of the path should be in the container
        leave(-1, "At least one of the path should be in a container.")
    if pathre.match(args.src).group("container") is not None and pathre.match(args.dest).group("container") is not None:
        # it's not allawed copy between containers
        leave(-1, "It's not allowed copy between containers.")

    # connect with docker daemon
    client = docker.from_env()
    if not client.ping():
        leave(-1, "It's not possible to connect to the Docker host. Check if the Docker daemon is running.")
