import time
from valkka.valkka_core import *
"""
(LiveThread:livethread) --> {InfoFrameFilter:info_filter) --> {FifoFrameFilter:fifo_filter} --> [LiveFifo:live_fifo] -->> (LiveThread:livethread2) 
"""

# TODO: clean up at cpp level

livethread  =LiveThread("livethread")
livethread2 =LiveThread("livethread2",20) # reserve stack for incoming frames
live_fifo   =livethread2.getFifo()

fifo_filter =FifoFrameFilter("in_live_filter",live_fifo)
info_filter =InfoFrameFilter("info_filter",fifo_filter)

livethread. startCall()
livethread2.startCall()

out_ctx =LiveOutboundContext(LiveConnectionType_sdp, "224.1.168.91", 2, 50000)
ctx     =LiveConnectionContext(LiveConnectionType_rtsp, "rtsp://admin:nordic12345@192.168.1.41", 2, info_filter)

livethread2.registerOutboundCall(out_ctx)
livethread. registerStreamCall(ctx)
livethread. playStreamCall(ctx)

time.sleep(120)

livethread. stopStreamCall(ctx)
livethread. deregisterStreamCall(ctx)
livethread2.deregisterOutbound(out_ctx)

livethread. stopCall();
livethread2.stopCall();

print("bye")

"""
create a file "multicast.sdp" with the following lines:

v=0
o=- 0 0 IN IP4 127.0.0.1
s=No Name
c=IN IP4 224.1.168.91
t=0 0
a=tool:libavformat 56.36.100
m=video 50000 RTP/AVP 96
a=rtpmap:96 H264/90000
a=fmtp:96 packetization-mode=1
a=control:streamid=0

Then you can test that the stream is multicasted with:

ffplay multicast.sdp
"""
