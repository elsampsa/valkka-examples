#!/bin/bash

# # choose your python flavor
# exe="python"
exe="python3"

# # list here your example snippets
codes="*.py" 

for i in $codes
do
    echo $i
    $exe pyeval.py $i > $i"_"
done
