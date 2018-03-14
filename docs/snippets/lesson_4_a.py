import time
from valkka.valkka_core import *
"""
main branch, streaming
(LiveThread:livethread) --> {FifoFrameFilter:live_out_filter} --> [FrameFifo: av_fifo] 
                                                                           |
                                                                           |   
 {ForkFrameFilter: fork_filter} <----(AVThread:avthread) << ---------------+  main branch, decoding
               |
      branch 1 +--> {FifoFrameFilter:gl_in_gilter} --> [OpenGLFrameFifo:gl_fifo] -->> (OpenGLThread:glthread)
               |
      branch 2 +--> {IntervalFrameFilter: interval_filter} --> {SwScaleFrameFilter: sws_filter} --> {SharedMemFrameFilter: shmem_filter}
"""

# IntervalTimeFilter
image_interval=1000  # YUV => RGB interpolation to the small size is done each 1000 milliseconds and passed on to the shmem ringbuffer

# CPU interpolation
width  =1920//4
height =1080//4
cc     =3 # its rgb

# posix shared memory
shmem_name    ="lesson_4"      # This identifies posix shared memory - must be unique
shmem_bytes   =width*height*cc # Size for each element in the ringbuffer
shmem_buffers =10              # Size of the shmem ringbuffer

# parameters are as follows: thread name, n720p, n1080p, n1440p, n4K
glthread        =OpenGLThread ("glthread", 10, 10, 0, 0)
                                        
# used by both streaming and decoding parts
av_fifo         =FrameFifo("av_fifo",10) 

# branch 1
gl_fifo         =glthread.getFifo()
gl_in_filter    =FifoFrameFilter("gl_in_filter",gl_fifo)

# branch 2
shmem_filter    =SharedMemFrameFilter(shmem_name, shmem_buffers, shmem_bytes) # shmem id, buffers, bytes per buffer
# shmem_filter    =BriefInfoFrameFilter("shmem") # nice way for debugging if you are actually getting stream here ..
sws_filter      =SwScaleFrameFilter("sws_filter", width, height, shmem_filter)
interval_filter =TimeIntervalFrameFilter("interval_filter", image_interval, sws_filter)

# fork
fork_filter     =ForkFrameFilter("fork_filter", gl_in_filter, interval_filter)

# main branch, streaming
livethread      =LiveThread("livethread")
live_out_filter =FifoFrameFilter("live_out_filter",av_fifo)

# main branch, decoding
avthread        =AVThread("avthread",av_fifo,fork_filter)

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

# maps stream with slot 1 to window "window_id"
context_id=glthread.newRenderContextCall(1,window_id,0)

time.sleep(60)

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
