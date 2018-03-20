import time
from valkka.valkka_core import *
"""
 
Streaming part                                                                           | Decoding part
                                                                                         |
(LiveThread:livethread) --> {FifoFrameFilter:live_out_filter} --> [FrameFifo: av_fifo] -->> (AVThread:avthread) --> {InfoFrameFilter:info_filter}
"""

# used by both streaming and decoding parts
av_fifo         =FrameFifo("av_fifo",10) 

# streaming part
livethread      =LiveThread("livethread")
live_out_filter =FifoFrameFilter("live_out_filter",av_fifo)

# decoding part
info_filter     =InfoFrameFilter("info_filter")
avthread        =AVThread("avthread",av_fifo,info_filter)
                                              
ctx =LiveConnectionContext(LiveConnectionType_rtsp, "rtsp://admin:nordic12345@192.168.1.41", 1, live_out_filter)

# start threads
avthread.startCall()
livethread.startCall()

# start decoding
avthread.decodingOnCall()

livethread.registerStreamCall(ctx)
livethread.playStreamCall(ctx)
time.sleep(5)

# stop decoding
# avthread.decodingOffCall()

# stop threads
livethread.stopCall()
avthread.stopCall()

# invokes the garbage collection => cpp level destructors
livethread=None
avthread  =None

print("bye")
