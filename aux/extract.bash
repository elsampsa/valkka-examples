#!/bin/bash
if [ "$#" -ne 3 ]; then
    echo
    echo "usage: extract.bash input.mkv 00:00:03 00:00:08"
    echo
    exit
fi
# ffmpeg -i $1 -s -ss 00:00:03 -t 00:00:08 
ffmpeg -y -i $1 -ss $2 -t $3 -an -c:v copy output.mkv 
