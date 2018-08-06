#!/bin/bash
echo
echo "starting shmem server side in the background"
echo
echo "next, start one-by-one:"
echo 
echo "python3 lesson_4_a_client.py"
echo "python3 lesson_4_a_client_api2.py"
echo "python3 lesson_4_a_client_opencv.py"
echo
echo "finally, do \"killall -9 python3\""
echo
rm -f test.out
python3 lesson_4_a.py &>>test.out &
