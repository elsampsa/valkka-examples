import time
from valkka.valkka_core import *
"""
Streaming part                                                                           
(LiveThread:livethread) --> 1. {FifoFrameFilter:live_out_filter} --> 2. [FrameFifo: av_fifo] 
                                                                              |
Decoding part                                                                 |
    3. (AVThread:avthread) << ------------------------------------------------+    
              |
              |                                                                         Presentation part
              +---> 4. {FifoFrameFilter:gl_in_filter} --> [OpenGLFrameFifo:gl_fifo] -->> (OpenGLThread:glthread)
 
"""


class LiveStream: # encapsulates FrameFifos, FrameFilters and an AVThread decoder for a single stream
  
  def __init__(self, gl_fifo, address, slot):
    self.gl_fifo =gl_fifo
    self.address =address
    self.slot    =slot
    
    # used by both streaming and decoding parts
    self.av_fifo         =FrameFifo("av_fifo",10) 

    # used by decoding and presentation parts
    self.gl_in_filter    =FifoFrameFilter("gl_in_filter",self.gl_fifo)

    # streaming part
    self.live_out_filter =FifoFrameFilter("live_out_filter",self.av_fifo)

    # decoding part
    self.avthread        =AVThread("avthread", self.av_fifo, self.gl_in_filter)

    # define connection to camera
    self.ctx =LiveConnectionContext(LiveConnectionType_rtsp, self.address, self.slot, self.live_out_filter)

    self.avthread.startCall()
    self.avthread.decodingOnCall


  def __del__(self):
    self.avthread.decodingOffCall()
    self.avthread.stopCall()
    

# parameters are as follows: thread name, n720p, n1080p, n1440p, n4K
glthread        =OpenGLThread ("glthread", 10, 10, 0, 0)
gl_fifo         =glthread.getFifo()
livethread      =LiveThread("livethread")

# start threads
glthread.startCall()
livethread.startCall()

# instantiating LiveStream starts the AVThread
stream1 = LiveStream(gl_fifo, "rtsp://admin:123456@192.168.0.134", 1) # slot 1  
stream2 = LiveStream(gl_fifo, "rtsp://admin:123456@192.168.0.135", 2) # slot 2

# register and start streams
livethread.registerStreamCall(stream1.ctx)
livethread.playStreamCall(stream1.ctx)

livethread.registerStreamCall(stream2.ctx)
livethread.playStreamCall(stream2.ctx)

# stream1 uses slot 1
window_id1 =glthread.createWindow()
glthread.newRenderGroupCall(window_id1)
context_id1 =glthread.newRenderContextCall(1, window_id1, 0)

# stream2 uses slot 2
window_id2 =glthread.createWindow()
glthread.newRenderGroupCall(window_id2)
context_id2 =glthread.newRenderContextCall(2, window_id2, 0)

time.sleep(3)

glthread.delRenderContextCall(context_id1)
glthread.delRenderGroupCall(window_id1)

glthread.delRenderContextCall(context_id2)
glthread.delRenderGroupCall(window_id2)

# stop threads
livethread.stopCall()
glthread.stopCall()

# invokes the garbage collection => cpp level destructors
livethread=None
glthread  =None

print("bye")
