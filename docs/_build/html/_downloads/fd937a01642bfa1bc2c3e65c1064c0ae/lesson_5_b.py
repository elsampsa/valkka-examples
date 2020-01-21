#<hide>
"""
filtergraph:

(LiveThread:livethread) --> {InfoFrameFilter:info_filter) -->> (LiveThread:livethread2) 

"""
#</hide>
"""<rtf>
In this lesson, we establish an on-demand RTSP server at the localhost.

Stream is read from an IP camera and then re-streamed (shared) to a local RTSP server that serves at port 8554.  While this snippet is running, you can test the RTSP server with:

:: 

  ffplay rtsp://127.0.0.1:8554/stream1


Let's start by importing Valkka:
<rtf>"""
import time
from valkka.core import *

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
*Before* starting the threads, establish an RTSP server on livethread2 at port 8554:
<rtf>"""
livethread2.setRTSPServer(8554);

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
Define stream sink: all outgoing frames with slot number "2" are sent to the RTSP server, with substream id "stream1":
<rtf>"""
out_ctx =LiveOutboundContext(LiveConnectionType_rtsp, "stream1", 2, 0)

"""<rtf>
Start playing:
<rtf>"""
livethread2.registerOutboundCall(out_ctx)
livethread. registerStreamCall(ctx)
livethread. playStreamCall(ctx)

"""<rtf>
Stream and recast to the RTSP server for a while:
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
