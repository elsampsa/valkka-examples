#!/bin/bash
rm *.deb
cp -f /home/sampsa/C/valkka_builds/build_dev/Valkka-*-Linux.deb .
docker build . -f Dockerfile.dev -t valkka:ubuntu18-dev
docker tag valkka:ubuntu18-dev elsampsa/valkka:ubuntu18-dev
# push elsampsa/valkka:ubuntu18-dev
