#!/bin/bash
##record from an IP camera
# ffmpeg -i rtsp://username:password@your_ip -c:v copy -an outfile.mkv
ffmpeg -i $1 -c:v copy -an outfile.mkv
