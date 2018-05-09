#<hide>
"""
filtergraph:

(LiveThread:livethread) -------------------------------------+  main branch, streaming
                                                             |   
{ForkFrameFilter: fork_filter} <----(AVThread:avthread) << --+  main branch, decoding
               |
      branch 1 +->> (OpenGLThread:glthread)
               |
      branch 2 +--> {IntervalFrameFilter: interval_filter} --> {SwScaleFrameFilter: sws_filter} --> {RGBSharedMemFrameFilter: shmem_filter}
"""
#</hide>
#<hide>
import time
from valkka.valkka_core import *
#</hide>
"""<rtf>
By now, we have learned how to receive, decode and send streams to the x window system.  In this chapter, we do all that, but at the same time, also send copies of the decoded frames to another python process.  

The filtergraph looks like this:

::


  (LiveThread:livethread) -------------------------------------+  main branch, streaming
                                                               |   
  {ForkFrameFilter: fork_filter} <----(AVThread:avthread) << --+  main branch, decoding
                 |
        branch 1 +->> (OpenGLThread:glthread)
                 |
        branch 2 +--> {IntervalFrameFilter: interval_filter} --> {SwScaleFrameFilter: sws_filter} --> {RGBSharedMemFrameFilter: shmem_filter}

We are using the ForkFrameFilter to branch the decoded stream into two branches.  Branch 1 goes to screen, while branch 2 does a lot of new stuff.

In branch 2, IntervalFrameFilter passes a frame through on regular intervals.  In our case we are going to use an interval of 1 second, i.e. even if your camera is sending 25 fps, at the other side of IntervalFrameFilter we'll be observing only 1 fps.

SwScaleFrameFilter does YUV => RGB interpolation on the CPU.  The final, interpolated RGB frame is passed to the posix shared memory with the RGBSharedMemFrameFilter.  From there it can be read by another python process.

(Remember that branch 1 does YUV => RGB interpolation as well, but on the GPU (and at 25 fps rate))

To summarize, branch 1 interpolates once a second a frame to RGB and passes it to shared memory.  The size of the frame can be adjusted.

Let's start the construction of the filtergraph by defining some parameters.  Frames are passed to SwScaleFrameFilter at 1000 millisecond intervals.  The image dimensions of the frame passed into shared memory, will be one quarter of a full-hd frame:
<rtf>"""
# define yuv=>rgb interpolation interval
image_interval=1000  # YUV => RGB interpolation to the small size is done each 1000 milliseconds and passed on to the shmem ringbuffer

# define rgb image dimensions
width  =1920//4
height =1080//4

"""<rtf>
RGBSharedMemFrameFilter needs also a unique name and the size of the shared memory ring-buffer:
<rtf>"""
# posix shared memory
shmem_name    ="lesson_4"      # This identifies posix shared memory - must be unique
shmem_buffers =10              # Size of the shmem ringbuffer

"""<rtf>
Next, we construct the filterchain as usual, from end-to-beginning:
<rtf>"""
# branch 1
glthread        =OpenGLThread("glthread")
gl_in_filter    =glthread.getFrameFilter()
                                        
# branch 2
shmem_filter    =RGBShmemFrameFilter(shmem_name, shmem_buffers, width, height)
# shmem_filter    =BriefInfoFrameFilter("shmem") # a nice way for debugging to see of you are actually getting any frames here ..
sws_filter      =SwScaleFrameFilter("sws_filter", width, height, shmem_filter)
interval_filter =TimeIntervalFrameFilter("interval_filter", image_interval, sws_filter)

# fork
fork_filter     =ForkFrameFilter("fork_filter", gl_in_filter, interval_filter)

# main branch
avthread        =AVThread("avthread",fork_filter)
av_in_filter    =avthread.getFrameFilter()
livethread      =LiveThread("livethread")

"""<rtf>
Define connection to camera: frames from 192.168.1.41 are written to live_out_filter and tagged with slot number 1:
<rtf>"""
ctx =LiveConnectionContext(LiveConnectionType_rtsp, "rtsp://admin:nordic12345@192.168.1.41", 1, av_in_filter)

"""<rtf>
Start processes, stream for 60 seconds and exit:
<rtf>"""
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

print("bye")
