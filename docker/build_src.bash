#!/bin/bash
## WARNING: if build fails, use --no-cache
docker build . -f Dockerfile.src -t valkka:ubuntu18-src
docker tag valkka:ubuntu18-src elsampsa/valkka:ubuntu18-src
# push elsampsa/valkka:ubuntu18-src

