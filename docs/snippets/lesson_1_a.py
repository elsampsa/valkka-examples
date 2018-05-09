#<hide>
"""
filtergraph:

(LiveThread:livethread) --> {InfoFrameFilter:live_out_filter}
"""
#</hide>
"""<rtf>
Import the valkka level 1 API:
<rtf>"""
import time
from valkka.valkka_core import *

"""<rtf>
Create a starting point for a FrameFilter chain:
<rtf>"""
live_out_filter =InfoFrameFilter("live_out_filter")

"""<rtf>
This is the "entry point" where we receive all the frames.  

InfoFrameFilter does nothing fancy - it just prints out the frames it receives.  

However, as you will learn during this tutorial, FrameFilters can do a lot of stuff.  You can chain them together.  They can be used to fork and copy the stream into complex graphs,  etc.
  
Next we need a thread that feeds the frames into our FrameFilter, so we instantiate a LiveThread:
<rtf>"""
livethread =LiveThread("livethread")

"""<rtf>
We also need a context describing the connection to an IP camera:
<rtf>"""
ctx =LiveConnectionContext(LiveConnectionType_rtsp, "rtsp://admin:nordic12345@192.168.1.41", 1, live_out_filter)

"""<rtf>
The first parameter defines the device type, which in this case is an IP camera using the rtsp protocol.  Note that we include the "entry point" live_out_filter.  The integer parameter "1" is the slot number - it will be discussed in detail later on in this tutorial.

Finally, we can start streaming frames from the IP camera:
<rtf>"""
livethread.startCall()
livethread.registerStreamCall(ctx)
livethread.playStreamCall(ctx)
time.sleep(5)
livethread.stopCall()
print("bye")

"""<rtf>
The output looks like this:

::

  InfoFrameFilter: live_out_filter start dump>> 
  InfoFrameFilter: FRAME   : <SetupFrame: timestamp=1525870891068 subsession_index=0 slot=1 / media_type=0 codec_id=27>
  InfoFrameFilter: PAYLOAD : []
  InfoFrameFilter: timediff: 0
  InfoFrameFilter: live_out_filter <<end dump   
  InfoFrameFilter: live_out_filter start dump>> 
  InfoFrameFilter: FRAME   : <BasicFrame: timestamp=1525870891068 subsession_index=0 slot=1 / payload size=45 / H264: slice_type=7>
  InfoFrameFilter: PAYLOAD : [0 0 0 1 103 100 0 42 173 132 1 12 32 8 97 0 67 8 2 24 ]
  InfoFrameFilter: timediff: 0
  InfoFrameFilter: live_out_filter <<end dump   
  InfoFrameFilter: live_out_filter start dump>> 
  InfoFrameFilter: FRAME   : <BasicFrame: timestamp=1525870891068 subsession_index=0 slot=1 / payload size=9 / H264: slice_type=8>
  InfoFrameFilter: PAYLOAD : [0 0 0 1 104 238 49 178 27 ]
  InfoFrameFilter: timediff: -1
  InfoFrameFilter: live_out_filter <<end dump  
  ...
  ...

InfoFrameFilter simply prints the frame type and first few bytes of it's payload (if there is any).

The first frame we get is a setup frame.  This is a key feature of Valkka: the stream of frames that flows from source to the final sink, consists, not only of payload (say, H264 or PCMU), but of frames that are used to inform the system about the stream type, codec, etc.

.. note:: The code itself (LiveThread, InfoFrameFilter) runs in c++, while the connections are programmed here, at the python level
<rtf>"""
