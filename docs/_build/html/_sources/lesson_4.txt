Lesson 4 : Sharing streams between python processes
===================================================

Server side
-----------

**Download server side** :download:`[here]<snippets/lesson_4_a.py>`

By now, we have learned how to receive, decode and send streams to the x window system.  In this chapter, we do all that, but at the same time, also send copies of the decoded frames to another python process.  

The filtergraph looks like this:

::

    streaming part 
    (LiveThread:livethread) --> {FifoFrameFilter:live_out_filter} --> [FrameFifo: av_fifo] 
                                                                              |
                                                                              |   
    {ForkFrameFilter: fork_filter} <----(AVThread:avthread) << ---------------+  main branch, decoding
                   |
          branch 1 +--> {FifoFrameFilter:gl_in_gilter} --> [OpenGLFrameFifo:gl_fifo] -->> (OpenGLThread:glthread)
                   |
          branch 2 +--> {IntervalFrameFilter: interval_filter} --> {SwScaleFrameFilter: sws_filter} --> {SharedMemFrameFilter: shmem_filter}


We are using the ForkFrameFilter to branch the decoded stream into two branches.  Branch 1 goes to screen, while branch 2 does a lot of new stuff.

In branch 2, IntervalFrameFilter passes a frame through on regular intervals.  In our case we are going to use an interval of 1 second, i.e. even if your camera is sending 25 fps, at the other side of IntervalFrameFilter we'll be observing only 1 fps.

SwScaleFrameFilter does YUV => RGB interpolation on the CPU.  The final, interpolated RGB frame is passed to the posix shared memory with the SharedMemFrameFilter.  From there it can be read by another python process.

Remember that branch 1 does YUV => RGB interpolation as well, but on the GPU (and at 25 fps rate).

To summarize, branch 1 interpolates once a second a frame to RGB and passes it to shared memory.  The size of the frame can be adjusted.

Let's start the construction of the filtergraph by defining some parameters.  The interval frames are passed to SwScaleFrameFilter will be 1000 milliseconds.  The image dimensions of the frame passed into shared memory, will be one quarter of a full-hd frame:

::

    # IntervalTimeFilter
    image_interval=1000  # YUV => RGB interpolation to the small size is done each 1000 milliseconds and passed on to the shmem ringbuffer

    # CPU interpolation
    width  =1920//4
    height =1080//4
    cc     =3 # its rgb

SharedMemFrameFilter (shared memory) requiers as parameters a unique name, size of shared memory ring-buffer and the size of each element in the ring-buffer:
    
::

    # posix shared memory
    shmem_name    ="lesson_4"      # This identifies posix shared memory - must be unique
    shmem_bytes   =width*height*cc # Size for each element in the ringbuffer
    shmem_buffers =10              # Size of the shmem ringbuffer

Next, we construct the filterchain as usual:
    
::

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

    
.. note:: If that got you all fuzzy, recall that programming the tree structure is started from the outer leafs of the tree, and moving hierarchically towards the main branch.
  
Define connection to camera: frames from 192.168.1.41 are written to live_out_filter and tagged with slot number 1:

::

  ctx =LiveConnectionContext(LiveConnectionType_rtsp, "rtsp://admin:nordic12345@192.168.1.41", 1, live_out_filter)


Start processes, stream for 60 seconds and exit:
  
::
    
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

    print("bye")

    
Next we need a separate python process, a client, that reads the frames.  Two versions are provided, the API level 2 being the most compact one.
    
.. note:: In the previous lessons, all streaming has taken place at the cpp level.  Here we are starting to use posix shared memory and semaphores in order to share frames between python processes.  However, don't expect posix shared memory and semaphores to keep up with several full-hd cameras running at 25+ fps!  Such high-throughput should be implemented at the cpp level using multithreading, while only defining the connections at the python level.


Client side: API level 2
------------------------

**Download client side API level 2** :download:`[here]<snippets/lesson_4_a_client_api2.py>`

This is a *separate* python program for reading the frames that are written by Valkka to the shared memory.

The parameters used both in the server side (above) and on the client side (below) **must be exactly the same** and the client program should be started *after* the server program (and while the server is running).  Otherwise undefined behaviour will occur.  

The used shmem_name(s) should be same in both server and client, but different for another server/client pair.

::

  from valkka.api2.threads import ShmemClient

  width  =1920//4
  height =1080//4
  cc     =3 # its rgb

  shmem_name    ="lesson_4"      # This identifies posix shared memory - must be unique
  shmem_bytes   =width*height*cc # Size for each element in the ringbuffer
  shmem_buffers =10              # Size of the shmem ringbuffer

  client=ShmemClient(
    name          =shmem_name, 
    n_ringbuffer  =shmem_buffers,   
    n_bytes       =shmem_bytes,    
    mstimeout     =1000,        # client timeouts if nothing has been received in 1000 milliseconds
    verbose       =False
  )

  
The *mstimeout* defines the semaphore timeout in milliseconds, i.e. the time when the client returns even if no frame was received:
  
::
  
  while True:
    index, isize = client.pull()
    if (index==None):
      print("timeout")
    else:
      data=client.shmem_list[index][0:isize]
      print("got data: ",data[0:min(10,isize)])
  
The *client.shmem_list* is a list of numpy arrays, while *isize* defines the extent of data in the array.  This example simply prints out the first ten bytes of the RGB image.

.. _opencv_client:

Client side: openCV
-------------------

**Download client side openCV example** :download:`[here]<snippets/lesson_4_a_client_opencv.py>`

OpenCV is a popular machine vision library.  We modify the previous example to make it work with openCV like this:

::

  import cv2
  from valkka.api2.threads import ShmemClient

  width  =1920//4
  height =1080//4
  cc     =3 # its rgb

  shmem_name    ="lesson_4"      # This identifies posix shared memory - must be unique
  shmem_bytes   =width*height*cc # Size for each element in the ringbuffer
  shmem_buffers =10              # Size of the shmem ringbuffer

  client=ShmemClient(
    name          =shmem_name, 
    n_ringbuffer  =shmem_buffers,   
    n_bytes       =shmem_bytes,    
    mstimeout     =1000,        # client timeouts if nothing has been received in 1000 milliseconds
    verbose       =False
  )

  while True:
    index, isize = client.pull()
    if (index==None):
      print("timeout")
    else:
      data =client.shmem_list[index][0:isize]
      img =data.reshape((height,width,3))
      img =cv2.GaussianBlur(img, (21, 21), 0)
      cv2.imshow("valkka_opencv_demo",img)
      cv2.waitKey(1)

Here the main difference to the previous example is, that the image data is reshaped.  After this, some gaussian blur is applied to the image.  Then it is visualized using openCV's own "high-gui" infrastructure.  If everything went ok, you should see a blurred image of your video once in a second.

Start this script *after* starting the server side script (server side must also be running).


Client side: API level 1
------------------------

**Download client side example** :download:`[here]<snippets/lesson_4_a_client.py>`

API level 2 provides extra wrapping.  Let's see what goes on at the lowest level (plain, cpp wrapped python code).

::

  from valkka.valkka_core import *

  width  =1920//4
  height =1080//4
  cc     =3 # its rgb

  shmem_name    ="lesson_4"      # This identifies posix shared memory - must be unique
  shmem_bytes   =width*height*cc # Size for each element in the ringbuffer
  shmem_buffers =10              # Size of the shmem ringbuffer

The wrapped cpp level class is SharedMemRingBuffer (at the server side, SharedMemFrameFilter is using SharedMemRingBuffer):
  
::

  shmem=SharedMemRingBuffer(shmem_name, shmem_buffers, shmem_bytes, 1000 , False) # shmem id, buffers, bytes per buffer, timeout, False=this is a client
    

We are using integer pointers from python:
    
::

  # pointers at the python side:
  index_p =new_intp() # shmem index
  isize_p =new_intp() # size of data


Next, get handles to the shared memory as numpy arrays:
  
::

  shmem_list=[]
  for i in range(shmem_buffers):
    shmem_list.append(getNumpyShmem(shmem,i)) # getNumpyShmem defined in the swig interface file
    print("got element i=",i)
    
Finally, start reading frames:
    
    
::

  while True:
    got=shmem.clientPull(index_p, isize_p)
    if (got):
      index=intp_value(index_p)
      isize=intp_value(isize_p)
      print("got index, size =", index, isize)
      ar=shmem_list[index][0:isize] # this is just a numpy array
      print("payload         =", ar[0:min(10,isize)])
    else:
      print("timeout")

Cpp documentation for Valkka shared memory classes be found `here. <https://elsampsa.github.io/valkka-core/html/group__shmem__tag.html>`_
