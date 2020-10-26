#!/bin/bash
docker build . -f Dockerfile.latest -t valkka:ubuntu18-latest
docker tag valkka:ubuntu18-latest elsampsa/valkka:ubuntu18-latest
# push elsampsa/valkka:ubuntu18-latest
