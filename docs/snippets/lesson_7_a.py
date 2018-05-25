#<hide>
import time
from valkka.valkka_core import *
#</hide>
"""<rtf>
In this example, we do simultaneously a lot of stuff, namely, save the stream to disk, decode it to bitmap, visualize it in two different x windows, pass the decoded frames to an OpenCV analyzer and re-transmit the stream to a multicast address.

Only a single connection to the IP camera is required and the stream is decoded only once.

The filtergraph looks like this:

::

    main branch
    (LiveThread:livethread) --> {ForkFrameFilter3: fork_filter}
                                             |
                                branch 1 <---+ 
                                             |
                                branch 2 <---+
                                             |
                                branch 3 <---+
                                                                    
    branch 1 : recast
    -->> (LiveThread:livethread2_1) 

    branch 2 : save to disk
    --> (FileFrameFilter:file_filter_2)

    branch 3 : decode
    -->> {AVThread:avthread_3} ------------+
                                           |                                                       
      {ForkFrameFilter: fork_filter_3} <---+
                     |
          branch 3.1 +--->> (OpenGLThread:glthread_3_1) --> to two x-windows
                     |
          branch 3.2 +----> {IntervalFrameFilter: interval_filter_3_2} --> {SwScaleFrameFilter: sws_filter_3_2} --> {RGBSharedMemFrameFilter: shmem_filter_3_2}
      
There is a new naming convention: the names of filters, threads and fifos are tagged with "_branch_sub-branch".  

Programming the filtergraph tree is started as usual, from the outer leaves, moving towards the main branch:
<rtf>"""
# *** branch 1 ***
livethread2_1    =LiveThread("livethread2_1")
live2_in_filter  =livethread2_1.getFrameFilter()

# *** branch 2 ***
file_filter_2    =FileFrameFilter("file_filter_2")

# *** branch 3.1 ***
glthread_3_1     =OpenGLThread("glthread")
gl_in_filter_3_1 =glthread_3_1.getFrameFilter()

# *** branch 3.2 ***
image_interval=1000  # YUV => RGB interpolation to the small size is done each 1000 milliseconds and passed on to the shmem ringbuffer
width  =1920//4      # CPU YUV => RGB interpolation
height =1080//4      # CPU YUV => RGB interpolation
shmem_name    ="lesson_4"      # This identifies posix shared memory - must be unique
shmem_buffers =10              # Size of the shmem ringbuffer

shmem_filter_3_2    =RGBShmemFrameFilter(shmem_name, shmem_buffers, width, height)
sws_filter_3_2      =SwScaleFrameFilter("sws_filter", width, height, shmem_filter_3_2)
interval_filter_3_2 =TimeIntervalFrameFilter("interval_filter", image_interval, sws_filter_3_2)

# *** branch 3 ***
fork_filter_3  =ForkFrameFilter("fork_3",gl_in_filter_3_1,interval_filter_3_2)
avthread_3     =AVThread("avthread_3",fork_filter_3)
av3_in_filter  =avthread_3.getFrameFilter()

# *** main branch ***
livethread  =LiveThread("livethread_1")
fork_filter =ForkFrameFilter3("fork_filter",live2_in_filter,file_filter_2,av3_in_filter)

#<hide>
# start threads (end-to-beginning order)
glthread_3_1   .startCall()
avthread_3     .startCall()
livethread2_1  .startCall()
livethread     .startCall()

# start decoding
avthread_3 .decodingOnCall()

ctx =LiveConnectionContext(LiveConnectionType_rtsp, "rtsp://admin:nordic12345@192.168.1.41", 2, fork_filter) # stream from 192.168.1.41 is sent to fork_filter with slot number 2
livethread    .registerStreamCall(ctx) # receive frames
livethread    .playStreamCall(ctx)

out_ctx =LiveOutboundContext(LiveConnectionType_sdp, "224.1.168.91", 2, 50000) # frames with slot number 2 are sent to port 50000
livethread2_1 .registerOutboundCall(out_ctx) # send frames

# create two X windows
window_id =glthread_3_1.createWindow()
glthread_3_1.newRenderGroupCall(window_id)
window_id2=glthread_3_1.createWindow()
glthread_3_1.newRenderGroupCall(window_id2)

# maps stream with slot 2 to window "window_id"
context_id  =glthread_3_1.newRenderContextCall(2,window_id,0)
# maps stream with slot 2 also to window "window_id2"
context_id2 =glthread_3_1.newRenderContextCall(2,window_id2,0)

# stream for 10 secs
time.sleep(10)

print("writing to disk")
# .. after that start writing stream to disk
file_filter_2.activate("kokkelis.mkv")

time.sleep(10) # write for 10 secs

# close the file
file_filter_2.deActivate()

# keep on streaming for 10 secs
# time.sleep(30)
time.sleep(10)

# close the file
# file_filter_2.deActivate()

glthread_3_1.delRenderContextCall(context_id)
glthread_3_1.delRenderContextCall(context_id2)
glthread_3_1.delRenderGroupCall(window_id)
glthread_3_1.delRenderGroupCall(window_id2)

# stop decoding
avthread_3 .decodingOffCall()

# stop threads in beginning-to-end order
livethread     .stopCall()
livethread2_1  .stopCall()
avthread_3     .stopCall()
glthread_3_1   .stopCall()

print("bye")
#</hide>
