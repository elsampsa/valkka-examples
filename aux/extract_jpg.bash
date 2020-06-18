#!/bin/bash
if [ "$#" -ne 3 ]; then
    echo
    echo "usage: extract.bash input.mkv 00:00:03 00:00:08"
    echo
    exit
fi
# ffmpeg -i $1 -ss 00:00:03 -t 00:00:08 
ffmpeg -y -i $1 -ss $2 -t $3 -qscale:v 2 img%03d.jpg 
