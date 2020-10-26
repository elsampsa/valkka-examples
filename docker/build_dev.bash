#!/bin/bash
docker build . -f Dockerfile.dev -t valkka:ubuntu18-dev
docker tag valkka:ubuntu18-dev elsampsa/valkka:ubuntu18-dev
# push elsampsa/valkka:ubuntu18-dev
