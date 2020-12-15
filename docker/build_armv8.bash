#!/bin/bash
## WARNING: if build fails, use --no-cache
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
# cp -f /usr/bin/qemu-arm-static .
docker build . -f Dockerfile.armv8 -t valkka:ubuntu18-armv8-src $@
docker tag valkka:ubuntu18-armv8-src elsampsa/valkka:ubuntu18-armv8-src
