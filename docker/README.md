# Docker testing

## Synopsis

Python media streaming framework [libValkka](https://elsampsa.github.io/valkka-examples/_build/html/index.html) for Ubuntu.  Includes a cpu version of [darknet python bindings](https://github.com/elsampsa/darknet-python).  

## Build

Build docker images with:
```
./build_image.bash TAG
```

TAGs are:
```
ubuntu18-armv8-src      from github latest source code
ubuntu18-dev            from locally created .deb package (personal hacky builds)
ubuntu18-src            from github source code, certain version number
                        give version number "MAJOR.MINOR.PATCH" as second argument to the script
ubuntu20-src            like previous, but for ubuntu20
```

NOTE: The final docker image TAG is, for example: valkka:ubuntu18-src-MAJOR.MINOR.PATCH

Finally, push to dockerhub with:
```
./push.bash ubuntu18-src-MAJOR.MINOR.PATCH
```

NOTE: there is a legacy "latest" version in dockerhub.. don't know how to remote it!  Don't use it.

## Docker Shared Memory

**WARNING** : libValkka relies heavily on shared memory, so remember to set enough of that.  See for example [this stack overflow question](https://stackoverflow.com/questions/30210362/how-to-increase-the-size-of-the-dev-shm-in-docker-container):

If you're running docker-compose, add this line to your libValkka microservice definition:
```
shm_size: '2gb'
```

If you run docker "manually", this might work:
```
docker run -it --shm-size=2gb ETC
```

## TODO

Would make more sense to have one docker image for building and another with just the package installed (without the build env installs)
