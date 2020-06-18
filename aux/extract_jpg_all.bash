#!/bin/bash
if [ "$#" -ne 1 ]; then
    echo
    echo "usage: extract.bash input.mkv"
    echo
    exit
fi
# ffmpeg -i $1 -s -ss 00:00:03 -t 00:00:08 
ffmpeg -y -i $1 -qscale:v 2 img%03d.jpg 
