#<hide>
"""
filtergraph:

(LiveThread:livethread) --> {InfoFrameFilter:info_filter) -->> (LiveThread:livethread2) 

"""
#</hide>
"""<rtf>

In this lesson, we are receiving frames from an IP camera using LiveThread and recast those frames to a multicast address using another LiveThread. The filterchain looks like this:

:: 

  (LiveThread:livethread) --> {InfoFrameFilter:info_filter) -->> (LiveThread:livethread2) 
  
Let's start by importing Valkka:
<rtf>"""
import time
from valkka.valkka_core import *

"""<rtf>
Live555's default output packet buffer size might be too small, so let's make it bigger before instantiating any LiveThreads:
<rtf>"""
setLiveOutPacketBuffermaxSize(95000)

"""<rtf>
Construct the filtergraph from end-to-beginning:
<rtf>"""
livethread2    =LiveThread("livethread2")
live_in_filter =livethread2.getFrameFilter()
info_filter    =InfoFrameFilter("info_filter",live_in_filter)
livethread     =LiveThread("livethread")

"""<rtf>
Start threads
<rtf>"""
livethread2.startCall()
livethread. startCall()

"""<rtf>
Define stream source: incoming frames from IP camera 192.168.1.41 are tagged with slot number "2" and they are written to "info_filter":
<rtf>"""
ctx     =LiveConnectionContext(LiveConnectionType_rtsp, "rtsp://admin:nordic12345@192.168.1.41", 2, info_filter)

"""<rtf>
Define stream sink: all outgoing frames with slot number "2" are sent to port 50000:
<rtf>"""
out_ctx =LiveOutboundContext(LiveConnectionType_sdp, "224.1.168.91", 2, 50000)

"""<rtf>
Start playing:
<rtf>"""
livethread2.registerOutboundCall(out_ctx)
livethread. registerStreamCall(ctx)
livethread. playStreamCall(ctx)

"""<rtf>
Stream and recast to multicast for a while:
<rtf>"""
time.sleep(60)

livethread. stopStreamCall(ctx)
livethread. deregisterStreamCall(ctx)
livethread2.deregisterOutboundCall(out_ctx)

"""<rtf>
Stop threads in beginning-to-end order
<rtf>"""
livethread. stopCall();
livethread2.stopCall();

print("bye")

#<hide>
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
#</hide>
