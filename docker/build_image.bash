#!/bin/bash
if [ $# -lt 1 ]; then
  echo "Give TAG name (pls see README.md)"
  exit
fi

if [ "$1" == "ubuntu18-armv8-src" ]
then
    ## WARNING: if build fails, use --no-cache
    docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
    name=$1
    extra=$2
    cp -f /usr/bin/qemu-arm-static .
elif [ "$1" == "ubuntu18-dev" ]
then
    ## NOTE: gets a deb package from a local dev directory
    rm *.deb
    cp -f /home/sampsa/C/valkka_builds/build_dev/Valkka-*-Linux.deb .
    name=$1
    extra=$2
elif [ "$1" == "ubuntu18-src" ]
then
    if [ $# -lt 2 ]; then
        echo "needs MAJOR.MINOR.PATCH"
        exit 2
    fi
    ver=$2
    name=$1"-"$2 # final image name will be ubuntu18-src-MAJOR.MINOR.PATCH
    extra=$3
    sed -r -i "s/ENV ver\=.*/ENV ver\=\"$ver\"/g" Dockerfile.$1
elif [ "$1" == "ubuntu20-src" ]
then
    if [ $# -lt 2 ]; then
        echo "needs MAJOR.MINOR.PATCH"
        exit 2
    fi
    ver=$2
    name=$1"-"$2 # final image name will be ubuntu20-src-MAJOR.MINOR.PATCH
    extra=$3
    sed -r -i "s/ENV ver\=.*/ENV ver\=\"$ver\"/g" Dockerfile.$1
else
    echo "unknow tag!"
    exit 2
fi

# $extra can be, say, --no-cache
echo "NAME WILL BE "$name
echo "EXTRA OPTIONS FOR DOCKER BUILD: "$extra
echo "PRESS ENTER TO CONTINUE"
read -r
docker build . -f Dockerfile.$1 -t valkka:$name $extra
docker tag valkka:$name elsampsa/valkka:$name
