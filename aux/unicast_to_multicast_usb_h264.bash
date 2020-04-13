#!/bin/bash
# # Make a copy of this script and edit for your particular case

form="udp://"
target="224.1.168.91:50000" # multicast comes from here
src=$1

## h264 capable webcam:
# ffmpeg -y -c:v h264 -i /dev/video2 -c:v copy -an kokkelis.mkv
## bitmap one:
# ffmpeg -i /dev/video0 -c:v h264 -an kokkelis.mkv

com="ffmpeg -c:v h264 -i "$src" -fflags +genpts -c:v copy -an -map 0:0 -f rtp "$form""$target
$com

