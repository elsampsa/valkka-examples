#!/bin/bash
## sudo apt-get install smem
## at htop press key 'H' => see only processes, not threads
## https://www.selenic.com/smem/
## https://www.golinuxcloud.com/check-memory-usage-per-process-linux/
if [ $# -ne 1 ]; then
  echo "Give interval in seconds"
  exit
fi
sleeptime=$1
while true
do 
    # cat /proc/$1/smaps | grep -i pss |  awk '{Total+=$2} END {print Total/1024" MB"}'
    smem -P "loop" -c "pid command pss"
    echo
    sleep $sleeptime
done
