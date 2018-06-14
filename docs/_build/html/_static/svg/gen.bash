#!/bin/bash
files="*.svg"
for f in $files
do
    convert -background none $f -resize 300x300 tmp.png
    convert -background none -gravity center -extent 300x300 tmp.png $f.png
done
