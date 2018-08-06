#!/bin/bash
#
# This is no place for debugging ..
# .. just for checking if something bad happens
#

# API level 1

# the shmem examples (lesson_4_*.py) are interactive
lis="lesson_1_a lesson_1_b lesson_1_c lesson_2_a lesson_3_a lesson_3_b lesson_3_c lesson_5_a lesson_5_b lesson_6_a lesson_7_a lesson_8_a"

rm -f test.out

for l in $lis
do
  echo $l
  echo $l &>> test.out
  python3 $l.py &>> test.out
done


