## Synopsis

Python media streaming framework [libValkka](https://elsampsa.github.io/valkka-examples/_build/html/index.html) for Ubuntu.  Includes a cpu version of [darknet python bindings](https://github.com/elsampsa/darknet-python).  

## Docker images

- "dev" images are built using my personal latest / hacky builds
- "src" build is built based on the source code from the latest [master branch](https://github.com/elsampsa/valkka-core) commit.
- "latest" is not up-to-date and should not be used (can't remove it from dockerhub.. eh)


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

## PPA repo

You may also install with apt-get from [this ppa repo](https://launchpad.net/~sampsa-riikonen/+archive/ubuntu/valkka/+packages).

 
