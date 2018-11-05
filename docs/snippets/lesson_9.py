"""<rtf>
First, business as usual (and like in tutorial example 3)
<rtf>"""
import time
from valkka.core import *
glthread        =OpenGLThread ("glthread")
gl_in_filter    =glthread.getFrameFilter()

avthread        =AVThread("avthread",gl_in_filter)
av_in_filter    =avthread.getFrameFilter()

livethread      =LiveThread("livethread")

ctx =LiveConnectionContext(LiveConnectionType_rtsp, "rtsp://admin:nordic12345@192.168.1.41", 1, av_in_filter)

glthread.startCall()
avthread.startCall()
livethread.startCall()

avthread.decodingOnCall()

livethread.registerStreamCall(ctx)
livethread.playStreamCall(ctx)

window_id =glthread.createWindow()

glthread.newRenderGroupCall(window_id)

context_id=glthread.newRenderContextCall(1,window_id,0) # slot, render group, z

time.sleep(1)

"""<rtf>
Let's add a bounding box, overlaying the video.  Parameteres for bounding box (left, bottom) -> (right, top) are given in the order left, right, top, bottom.

Coordinates are relative coordinates from 0 to 1.
<rtf>"""
bbox=(0.25, 0.75, 0.75, 0.25) # left, right, top, bottom

glthread.addRectangleCall(context_id, bbox[0], bbox[1], bbox[2], bbox[3])

"""<rtf>
You could add more bounding boxes with consecutive calls to **glthread.addRectangleCall**

Let's play video for 10 seconds
<rtf>"""

time.sleep(10)

"""<rtf>
Finally, clear the bounding boxes and exit
<rtf>"""
glthread.clearObjectsCall(context_id)

glthread.delRenderContextCall(context_id)
glthread.delRenderGroupCall(window_id)

avthread.decodingOffCall()

livethread.stopCall()
avthread.stopCall()
glthread.stopCall()

print("bye")
