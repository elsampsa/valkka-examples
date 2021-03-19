#!/bin/bash
## WARNING: if build fails, use --no-cache
export ver="1.2.0"
sed -r -i "s/ENV ver\=.*/ENV ver\=\"$ver\"/g" Dockerfile.src
docker build . -f Dockerfile.src -t valkka:ubuntu18-src-$ver $@
docker tag valkka:ubuntu18-src-$ver elsampsa/valkka:ubuntu18-src-$ver
