import time
from valkka.valkka_core import *
"""
 
Streaming part                                                                           
(LiveThread:livethread) --> {FifoFrameFilter:live_out_filter} --> [FrameFifo: av_fifo] 
                                                                           |
Decoding part                                                              |
    (AVThread:avthread) << ------------------------------------------------+    
              |
              |                                                                         Presentation part
              +---> {FifoFrameFilter:gl_in_filter} --> [OpenGLFrameFifo:gl_fifo] -->> (OpenGLThread:glthread)
"""

# parameters are as follows: thread name, n720p, n1080p, n1440p, n4K
glthread        =OpenGLThread ("glthread", 10, 10, 0, 0)
                                        
# used by both streaming and decoding parts
av_fifo         =FrameFifo("av_fifo",10) 

# used by decoding and presentation parts
gl_fifo         =glthread.getFifo()
gl_in_filter    =FifoFrameFilter("gl_in_filter",gl_fifo)

# streaming part
livethread      =LiveThread("livethread")
live_out_filter =FifoFrameFilter("live_out_filter",av_fifo)

# decoding part
avthread        =AVThread("avthread",av_fifo,gl_in_filter)

# define connection to camera
ctx =LiveConnectionContext(LiveConnectionType_rtsp, "rtsp://admin:nordic12345@192.168.1.41", 1, live_out_filter)

# start threads
glthread.startCall()
avthread.startCall()
livethread.startCall()

# start decoding
avthread.decodingOnCall()

livethread.registerStreamCall(ctx)
livethread.playStreamCall(ctx)

# create an X-window
window_id =glthread.createWindow()
glthread.newRenderGroupCall(window_id)
context_id=glthread.newRenderContextCall(1,window_id,0)

time.sleep(10)

glthread.delRenderContextCall(context_id)
glthread.delRenderGroupCall(window_id)

# stop decoding
avthread.decodingOffCall()

# stop threads
livethread.stopCall()
avthread.stopCall()
glthread.stopCall()

# invokes the garbage collection => cpp level destructors
livethread=None
avthread  =None
glthread  =None

print("bye")
