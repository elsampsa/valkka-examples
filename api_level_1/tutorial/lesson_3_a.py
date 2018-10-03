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
from valkka.core import *
#</hide>
"""<rtf>
Let's consider the following filtergraph with streaming, decoding and presentation:

::

  Streaming part                                                                           
  (LiveThread:livethread)---+
                            |
  Decoding part             |
  (AVThread:avthread) <<----+    
  |
  |       Presentation part
  +--->> (OpenGLThread:glthread)
  
  
Compared to the previous lesson, we're continuying the filterchain from AVThread to OpenGLThread.  OpenGLThread is responsible for sending the frames to designated x windows.

.. note:: OpenGLThread uses OpenGL texture streaming.  YUV interpolation to RGB is done on the GPU, using the shader language.
    
Start constructing the filterchain from end-to-beginning:
<rtf>"""
# presentation part
glthread        =OpenGLThread ("glthread")
gl_in_filter    =glthread.getFrameFilter()


"""<rtf>
We requested a framefilter from the OpenGLThread.  It is passed to the AVThread:
<rtf>"""
# decoding part
avthread        =AVThread("avthread",gl_in_filter)
av_in_filter    =avthread.getFrameFilter()

# streaming part
livethread      =LiveThread("livethread")

"""<rtf>
Define the connection to the IP camera as usual, with **slot number** "1":

.. _connection:
<rtf>"""
ctx =LiveConnectionContext(LiveConnectionType_rtsp, "rtsp://admin:nordic12345@192.168.1.41", 1, av_in_filter)

"""<rtf>
Start all threads, start decoding, and register the live stream.  Starting the threads should be done in end-to-beginning order (in the same order we constructed the filterchain).
<rtf>"""
glthread.startCall()
avthread.startCall()
livethread.startCall()

# start decoding
avthread.decodingOnCall()

livethread.registerStreamCall(ctx)
livethread.playStreamCall(ctx)

"""<rtf>
Now comes the new bit.  First, we create a new X window on the screen:
<rtf>"""
window_id =glthread.createWindow()

"""<rtf>
We could also use the window id of an existing X window.
  
Next, we create a new "render group" to the OpenGLThread.  Render group is a place where we can render bitmaps - in this case it's just the X window.
<rtf>"""
glthread.newRenderGroupCall(window_id)

"""<rtf>
We still need a "render context".  Render context is a mapping from a frame source (in this case, the IP camera) to a certain render group (X window) on the screen:
<rtf>"""
context_id=glthread.newRenderContextCall(1,window_id,0) # slot, render group, z

"""<rtf>
The first argument to newRenderContextCall is the **slot number**.  We defined the slot number for the IP camera when we used the :ref:`LiveConnectionContext <connection>`.

Now, each time a frame with slot number "1" arrives to OpenGLThread it will be rendered to render group "window_id".

Stream for a while, and finally, close all threads:
<rtf>"""
time.sleep(10)

glthread.delRenderContextCall(context_id)
glthread.delRenderGroupCall(window_id)

# stop decoding
avthread.decodingOffCall()

"""<rtf>
Close threads.  Stop threads in beginning-to-end order (i.e., following the filtergraph from left to right).
<rtf>"""
livethread.stopCall()
avthread.stopCall()
glthread.stopCall()

print("bye")
