
Lesson 7 : Decode, save, visualize, analyze and re-transmit
===========================================================

**Download lesson** :download:`[here]<snippets/lesson_7_a.py>`

This lesson demonstrates the full power of Valkka.  We do simultaneously a lot of stuff, namely, save the stream to disk, decode it to bitmap, visualize it in two different x windows, pass the decoded frames to an OpenCV analyzer and re-transmit the stream to a multicast address.

Only a single connection to the IP camera is required and the stream is decoded only once.

This can be achieved with the following filtergraph:

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
  --> {FifoFrameFilter:fifo_filter_1} --> [LiveFifo:live_fifo_1] -->> (LiveThread:livethread2_1) 

  branch 2 : save to disk
  --> (FileFrameFilter:file_filter_2)

  branch 3 : decode
  --> {FifoFrameFilter:fifo_filter_3} --> [FrameFifo: av_fifo_3] --->> (AVThread:avthread_3) --+
                                                                                               |
   {ForkFrameFilter: fork_filter_3} <----------------------------------------------------------+
                   |
        branch 3.1 +--> {FifoFrameFilter:gl_in_filter_3_1} --> [OpenGLFrameFifo:gl_fifo_3_1] -->> (OpenGLThread:glthread_3_1) --> to two x-windows
                   |
        branch 3.2 +--> {IntervalFrameFilter: interval_filter_3_2} --> {SwScaleFrameFilter: sws_filter_3_2} --> {SharedMemFrameFilter: shmem_filter_3_2} 

There is a new naming convention: the names of filters, threads and fifos are tagged with "_branch_sub-branch".  

Programming the filtergraph tree is started from the outer leaves, moving towards the main branch:

::

  # ** branch 3.1 **
  glthread_3_1     =OpenGLThread ("glthread", 10, 10, 0, 0) # parameters are as follows: thread name, n720p, n1080p, n1440p, n4K
  gl_fifo_3_1      =glthread_3_1.getFifo()
  gl_in_filter_3_1 =FifoFrameFilter("gl_in_filter_3_1",gl_fifo_3_1)
  ...
  ...
  # *** branch 3 ***
  av_fifo_3      =FrameFifo("av_fifo_3",10)
  fork_filter_3  =ForkFrameFilter("fork_filter_3", gl_in_filter_3_1, interval_filter_3_2)
  fifo_filter_3  =FifoFrameFilter("fifo_filter_3",av_fifo_3)
  avthread_3     =AVThread("avthread_3",av_fifo_3,fork_filter_3)
  ...
  ...
  # *** main branch ***
  livethread  =LiveThread("livethread_1")
  fork_filter =ForkFrameFilter3("fork_filter",fifo_filter_1,file_filter_2,fifo_filter_3)
  ctx =LiveConnectionContext(LiveConnectionType_rtsp, "rtsp://admin:nordic12345@192.168.1.41", 2, fork_filter) # stream from 192.168.1.41 is sent to fork_filter with slot number 2
  
The full code can be downloaded from :download:`[here]<snippets/lesson_7_a.py>`.

The OpenCV client program for reading shared memory can be found from :ref:`[lesson 4]<opencv_client>`.

Testing the shared multicast stream was explained in :ref:`[lesson 5]<multicast>`.
  
