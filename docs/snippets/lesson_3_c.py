#<hide>
"""
filtergraph:

Streaming part                                                                           
(LiveThread:livethread)---+
                          |
Decoding part             |
(AVThread:avthread) <<----+    
 |
 |       Presentation part
 +--->> (OpenGLThread:glthread)
"""
#</hide>
#<hide>
import time
from valkka.valkka_core import *
#</hide>
"""<rtf>
Let's consider decoding the H264 streams from multiple RTSP cameras.  For that, we'll be needing several decoding AVThreads.  Let's take another look at the filtergraph:

::

  Streaming part                                                                           
  (LiveThread:livethread)---+
                            |
  Decoding part             |   [This part of the filtergraph should be replicated]
  (AVThread:avthread) <<----+    
  |
  |       Presentation part
  +--->> (OpenGLThread:glthread)


LiveThread and OpenGLThread can deal with several simultaneous media streams, while for decoding, we need one thread per decoder.  Take a look at the `library architecture page <https://elsampsa.github.io/valkka-core/html/process_chart.html>`_

It's a good idea to encapsulate the decoding part into its own class.  This class takes as an input, the framefilter where it writes the decoded frames and as an input, the stream rtsp address:
<rtf>"""
class LiveStream:
  
  def __init__(self, gl_in_filter, address, slot):
    self.gl_in_filter =gl_in_filter
    
    self.address      =address
    self.slot         =slot
    
    # decoding part
    self.avthread        =AVThread("avthread", self.gl_in_filter)
    self.av_in_filter    =self.avthread.getFrameFilter()

    # define connection to camera
    self.ctx =LiveConnectionContext(LiveConnectionType_rtsp, self.address, self.slot, self.av_in_filter)

    self.avthread.startCall()
    self.avthread.decodingOnCall()


  def __del__(self):
    self.avthread.decodingOffCall()
    self.avthread.stopCall()
    
"""<rtf>
Construct the filtergraph from end-to-beginning:
<rtf>"""
# presentation part
glthread        =OpenGLThread ("glthread")
gl_in_filter    =glthread.getFrameFilter()

# streaming part
livethread      =LiveThread("livethread")

# start threads
glthread.startCall()
livethread.startCall()

"""<rtf>
Instantiate LiveStreams.  This will also start the AVThreads.  Frames from the first camera are tagged with slot number 1, while frames from the second camera are tagged with slot number 2:
<rtf>"""
stream1 = LiveStream(gl_in_filter, "rtsp://admin:nordic12345@192.168.1.41", 1) # slot 1  
stream2 = LiveStream(gl_in_filter, "rtsp://admin:nordic12345@192.168.1.42", 2) # slot 2

"""<rtf>
Register streams to LiveThread and start playing them:
<rtf>"""
livethread.registerStreamCall(stream1.ctx)
livethread.playStreamCall(stream1.ctx)

livethread.registerStreamCall(stream2.ctx)
livethread.playStreamCall(stream2.ctx)

"""<rtf>
Create x windows, and map slot numbers to certain x windows:
<rtf>"""
# stream1 uses slot 1
window_id1 =glthread.createWindow()
glthread.newRenderGroupCall(window_id1)
context_id1 =glthread.newRenderContextCall(1, window_id1, 0)

# stream2 uses slot 2
window_id2 =glthread.createWindow()
glthread.newRenderGroupCall(window_id2)
context_id2 =glthread.newRenderContextCall(2, window_id2, 0)

"""<rtf>
Render video for a while, stop threads and exit:
<rtf>"""
time.sleep(10)

glthread.delRenderContextCall(context_id1)
glthread.delRenderGroupCall(window_id1)

glthread.delRenderContextCall(context_id2)
glthread.delRenderGroupCall(window_id2)

# stop threads
livethread.stopCall()
glthread.stopCall()

print("bye")

"""<rtf>
There are many ways to organize threads, render contexes (slot to x window mappings) and complex filtergraphs into classes.  It's all quite flexible and left for the API user.

One could even opt for an architecture, where there is a LiveThread and OpenGLThread for each individual stream (however, this is not recommended).

The level 2 API provides ready-made filtergraph classes for different purposes (similar to class LiveStream constructed here).
<rtf>"""
