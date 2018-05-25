#!/bin/bash
if [ $# -ne 1 ]; then
  echo "Give number of streams (assuming ports start from 50000)"
  exit
fi

last=$(echo "scale=1;50000+("$1"-1)*4" | bc)
for (( c=50000; c<=$last; c=c+4 ))
do
  echo $c
  sed -r "s/m\=video 50000 RTP\/AVP 96/m\=video "$c" RTP\/AVP 96/g" multicast.sdp > multicast_tmp.sdp
  cat multicast_tmp.sdp
  echo
  echo
  ffplay multicast_tmp.sdp &
  sleep 1
done

