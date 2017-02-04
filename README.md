docker-cp
=========

The docker-cp.py is a python3 script which work like `docker cp` command. It's
allow copy file/directories from/to containers. The user can specify the buffer
size used during the operation of read/write data from Docker daemon or the local
filesystem.

To see how to use the script execute: `docker-cp.py -h`

### Dependencies

To install all dependencies: `pip install -r requirements.txt`

### Exaples:


Copy from container:

```
$ docker run -d --name fedora fedora:25 sleep
$ ./docker-cp.py fedora:/etc/fedora-release .
$ cat fedora-release
Fedora release 25 (Twenty Five)
```

Copy to container:

```
$ docker run -d --name fedora fedora:25 sleep
$ echo "Dummy file" > dummy
$ ./docker-cp.py ./dummy fedora:/
```


