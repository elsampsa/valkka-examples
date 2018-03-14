
Lesson 6 : Writing / reading stream
===================================

**Download lesson** :download:`[here]<snippets/lesson_6_a.py>`

In this lesson, we are (a) writing from a live stream to a file and (b) read the file, decode the stream and present it on the screen.  The filtergraph goes like this:

::

  *** writing ***

  (LiveThread:livethread) --> {FileFrameFilter:file_filter}

  *** reading ***

  reading part
  (FileThread:filethread) --> {BlockingFifoFrameFilter:av_filter} --> [FrameFifo:av_fifo] 
                                                                             |
  decoding part                                                              |
      (AVThread:avthread) << ------------------------------------------------+    
                |
                |                                                                         Presentation part
                +---> {FifoFrameFilter:gl_in_filter} --> [OpenGLFrameFifo:gl_fifo] -->> (OpenGLThread:glthread)


Note that live and file streams are treated on an equal basis and with a similar filtergraph.  We could also send the file over the net as a multicast stream.  This is left as an excercise.

Writing is done simply by piping the stream into a FileFrameFilter:
                
::

  # *** writing ***
  livethread   =LiveThread("livethread")
  file_filter  =FileFrameFilter("file_filter")
  # file_filter  =BriefInfoFrameFilter("info_filter") # uncomment this to do debugging (i.e., are you getting any frames?)
  # stream from 192.168.1.41, tag frames with slot number 1 and write to file_filter
  ctx          =LiveConnectionContext(LiveConnectionType_rtsp, "rtsp://admin:nordic12345@192.168.1.41", 1, file_filter) 

Keep in mind that it is the LiveThread that "drives" the writing to the disk (in the first filtergraph, there is just one thread, the LiveThread)

For reading, decoding and presenting, we instantiate the threads and construct the filtergraph as usual:

::
    
  # *** reading ***
  glthread      =OpenGLThread ("glthread", 10, 10, 0, 0) # parameters are as follows: thread name, n720p, n1080p, n1440p, n4K
  gl_fifo       =glthread.getFifo()
  gl_in_filter  =FifoFrameFilter("gl_in_filter",gl_fifo)

  # used by both reading and decoding parts
  av_fifo       =FrameFifo("av_fifo",10) 

  # reading part
  av_filter     =BlockingFifoFrameFilter("av_filter",av_fifo)
  filethread    =FileThread("filethread")
  file_ctx      =FileContext("kokkelis.mkv", 1, av_filter) # read from file "kokkelis.mkv", tag frames with slot number 1 and write to av_filter

  # decoding part
  avthread        =AVThread("avthread",av_fifo,gl_in_filter)

Starting LiveThread will stream the frames to FileFrameFilter.  

::

  # *** writing ***
  # start streaming
  livethread .startCall()
  livethread .registerStreamCall(ctx)
  livethread .playStreamCall(ctx)

In order to start writing to disk, FileFrameFilter's "activate" method must be called with the filename.  Only matroska (.mkv) files are supported:
  
::
  
  # start writing to a file
  print("writing to file")
  file_filter.activate("kokkelis.mkv")

  # stream for 30 secs
  time.sleep(30)

  # close the file
  file_filter.deActivate()

  # stop livethread
  livethread.stopCall()

Let's setup stream decoding, presenting, etc. as usual:
  
::
  
  # *** reading ***
  print("reading file")
  glthread   .startCall()
  filethread .startCall()
  avthread   .startCall()

  # start decoding
  avthread.decodingOnCall()

  # create an x-window
  window_id =glthread.createWindow()
  glthread.newRenderGroupCall(window_id)

  # maps stream with slot 1 to window "window_id"
  context_id =glthread.newRenderContextCall(1, window_id, 0)

Open the file by sending it a call with the FileContext (file_ctx) identifying the file stream:
  
::

  print("open file")
  filethread.openFileStreamCall(file_ctx)

Playing, seeking and stopping is done as follows:
  
::
  
  print("play file")
  filethread.playFileStreamCall(file_ctx)

  # play the file for 10 secs
  time.sleep(10)

  # let's seek to seekpoint 2 seconds
  print("seeking")
  file_ctx.seektime_=2000
  filethread.seekFileStreamCall(file_ctx)

  # pause for 3 secs
  print("pausing")
  filethread.stopFileStreamCall(file_ctx)
  time.sleep(3)

  # continue playing for 5 secs
  print("play again")
  filethread.playFileStreamCall(file_ctx)
  time.sleep(5)

Finally, exit:

::  
  
  glthread.delRenderContextCall(context_id)
  glthread.delRenderGroupCall(window_id)
  filethread.stopCall()
  avthread  .stopCall()
  glthread  .stopCall()

  print("bye")


