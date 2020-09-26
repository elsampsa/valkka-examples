import time
from valkka.core import *
from valkka.api2 import FragMP4ShmemClient

#</hide>
"""<rtf>
The filtergraph for simultaneous video viewing and frag-MP4 muxing looks like this:

::

                                                               
  (LiveThread:livethread) -->----------------------------------+  main branch (forks into two)
                                                               |   
  (OpenGLThread:glthread) <----(AVThread:avthread) << ---------+  decoding branch
                                                               |
       +-----------------------------------------<-------------+  mux branch
       |
       +--> {FragMP4MuxFrameFilter:fragmp4muxer} --> {FragMP4ShmemFrameFilter:fragmp4shmem}         
        
<rtf>"""

shmem_buffers = 10 # 10 element in the ring-buffer
shmem_name = "lesson_4_c" # unique name identifying the shared memory
cellsize = 1024*1024*3 # max size for each MP4 fragment
timeout = 1000 # in ms

# decoding branch
glthread        =OpenGLThread("glthread")
gl_in_filter    =glthread.getFrameFilter()
avthread        =AVThread("avthread",gl_in_filter)
av_in_filter    =avthread.getFrameFilter()

# mux branch
shmem_filter    =FragMP4ShmemFrameFilter(shmem_name, shmem_buffers, cellsize)
mux_filter      =FragMP4MuxFrameFilter("fragmp4muxer", shmem_filter)
mux_filter.activate() # don't forget!

# fork
fork_filter     =ForkFrameFilter("fork_filter", av_in_filter, mux_filter)

# main branch
livethread      =LiveThread("livethread")

"""<rtf>
Define connection to camera: frames from the IP camera are written to live_out_filter and tagged with slot number 1:
<rtf>"""
# ctx =LiveConnectionContext(LiveConnectionType_rtsp, "rtsp://admin:nordic12345@192.168.1.41", 1, fork_filter)
ctx =LiveConnectionContext(LiveConnectionType_rtsp, "rtsp://admin:123456@192.168.0.134", 1, fork_filter)
"""<rtf>
Start threads:
<rtf>"""
glthread.startCall()
avthread.startCall()
livethread.startCall()

# start decoding
avthread.decodingOnCall()

livethread.registerStreamCall(ctx)

# create an X-window
window_id =glthread.createWindow()
glthread.newRenderGroupCall(window_id)

# maps stream with slot 1 to window "window_id"
context_id=glthread.newRenderContextCall(1,window_id,0)

"""<rtf>
Ok, the server is alive and running.  Let's do the client part for receiving frames.
<rtf>"""
client = FragMP4ShmemClient(
    name=shmem_name,
    n_ringbuffer=shmem_buffers,
    n_size=cellsize,
    mstimeout=timeout,  
    verbose=False
)

"""<rtf>
The client is ready to go.  Before starting to receive frames, start playing the RTSP camera
<rtf>"""
livethread.playStreamCall(ctx)

"""<rtf>
Read 10 frames & exit
<rtf>"""
print("client starting")
cc = 0
while True:
    index, meta = client.pullFrame()
    if (index == None):
        print("timeout")
    else:
        data = client.shmem_list[index][0:meta.size]
        print("got", meta.name.decode("utf-8"), "of size", meta.size)
        cc += 1
    if cc >= 100:
        break

print("stopping..")

mux_filter.deActivate() # don't forget!
"""<rtf>
Clear the server
<rtf>"""
glthread.delRenderContextCall(context_id)
glthread.delRenderGroupCall(window_id)

# stop decoding
avthread.decodingOffCall()

# stop threads
livethread.stopCall()
avthread.stopCall()
glthread.stopCall()

print("bye")
