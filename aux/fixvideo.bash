#!/bin/bash
# convert regular video file to an "ip-camera-like" stream
ffmpeg -i $1 -c:v h264 -r 10 -preset ultrafast -profile:v baseline -bsf h264_mp4toannexb -x264-params keyint=10:min-keyint=10 -an outfile.mkv
