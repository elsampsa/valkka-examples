#!/bin/bash
if [ $# -ne 1 ]; then
  echo "Give port number"
  exit
fi
sed -r "s/m\=video 50000 RTP\/AVP 96/m\=video "$1" RTP\/AVP 96/g" multicast.sdp > multicast_tmp.sdp
ffplay multicast_tmp.sdp

