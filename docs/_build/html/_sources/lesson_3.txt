Lesson 3 : Streaming to the X-window system
============================================

One camera to one window
------------------------

**Download lesson** :download:`[here]<snippets/lesson_3_a.py>`


In this lesson, we're directing the decoded stream to the screen.  The filtergraph looks like this:
  
::
  
    Streaming part                                                                           
    (LiveThread:livethread) --> {FifoFrameFilter:live_out_filter} --> [FrameFifo: av_fifo] 
                                                                               |
    Decoding part                                                              |
        (AVThread:avthread) << ------------------------------------------------+    
                  |
                  |                                                                         Presentation part
                  +---> {FifoFrameFilter:gl_in_filter} --> [OpenGLFrameFifo:gl_fifo] -->> (OpenGLThread:glthread)
    

Compared to the previous lesson, we're continuying the filterchain from the AVThread to another FrameFifo (OpenGLFrameFifo) and from there to another thread (thread borders designated with ">>"), the OpenGLThread.
    
OpenGLThread is responsible for sending the frames to designated x windows.

.. note:: OpenGLThread uses OpenGL texture streaming.  YUV interpolation to RGB is done on the GPU, using the shader language.

We start as always by importing the library:
    
::    
  
    import time
    from valkka.valkka_core import *
    
    
The first thing to instantiate is the OpenGLThread:
    
::
    
    # parameters are as follows: thread name, n720p, n1080p, n1440p, n4K, buffering time (in milliseconds)
    glthread =OpenGLThread ("glthread", 10, 10, 0, 0, 300)
                                            
OpenGLThread takes as arguments, the amount of frames per video stream type.  All frames are *pre-reserved*.   The amount of frames you need, depends on the buffering time.  If you are going to use two 720p cameras, each at 20 fps, with 300 millisecond buffering time, then you should reserve 

::

    2 * 20 fps * 0.3 sec = 12 frames
  
for 720p.  If you don't want to think about this, just reserve several hundred frames for each camera type, i.e. use:

::
  
    glthread =OpenGLThread ("glthread", 200, 200, 200, 200) # buffering time not defined here.. uses the default value of 100 milliseconds

Next, we construct the rest of the filterchain:
    
::
                                                                                        
    # used by both streaming and decoding parts
    av_fifo         =FrameFifo("av_fifo",10) 

    # used by decoding and presentation parts
    gl_fifo         =glthread.getFifo()
    gl_in_filter    =FifoFrameFilter("gl_in_filter",gl_fifo)
    
Note here that the *gl_fifo* instance (OpenGLFrameFifo class) is not created by the API user, but instead, requested from the OpenGLThread instance.
    
::

    # streaming part
    livethread      =LiveThread("livethread")
    live_out_filter =FifoFrameFilter("live_out_filter",av_fifo)

    # decoding part
    avthread        =AVThread("avthread",av_fifo,gl_in_filter)

    
Define the connection to the IP camera as usual, with **slot number** "1":

.. _connection:
  
::
    
    ctx =LiveConnectionContext(LiveConnectionType_rtsp, "rtsp://admin:nordic12345@192.168.1.41", 1, live_out_filter) # type, address, slot number, FrameFilter
    
    
Start all threads and register the live stream:
    
::

    # start threads
    glthread.startCall()
    avthread.startCall()
    livethread.startCall()

    # start decoding
    avthread.decodingOnCall()

    livethread.registerStreamCall(ctx)
    livethread.playStreamCall(ctx)
    
  
Now comes the new bit.  First, we create a new X window on the screen:
  
::

    # create an X-window
    window_id =glthread.createWindow()
    
In principle, we could as well take the window id of an existing X window.
  
Next, we create a new "render group" to the OpenGLThread.  Render group is a place where we can render bitmaps - in this case it's just the X window.
  
::
    
    glthread.newRenderGroupCall(window_id)
  
We still need a "render context".  Render context is a mapping from a frame source (in this case, the IP camera) to a certain render group (X window) on the screen:
  
::    
    
    context_id=glthread.newRenderContextCall(1,window_id,0) # slot, render group, z

The first argument to newRenderContextCall is the **slot number**.  We defined the slot number for the IP camera when we used the :ref:`LiveConnectionContext <connection>`.

Now, each time a frame with slot number "1" arrives to OpenGLThread it will be rendered to render group "window_id".

Stream for a while, and finally, close all threads:

::
    
    time.sleep(10)

    glthread.delRenderContextCall(context_id)
    glthread.delRenderGroupCall(window_id)

    # stop decoding
    avthread.decodingOffCall()

    # stop threads
    livethread.stopCall()
    avthread.stopCall()
    glthread.stopCall()

    print("bye")
    

One camera to several windows
-------------------------------

**Download lesson** :download:`[here]<snippets/lesson_3_b.py>`

Stream from a single IP camera can be mapped to several X windows, like this:

::

    id_list=[]

    for i in range(10):
      window_id =glthread.createWindow() # create an x window
      glthread.newRenderGroupCall(window_id)
      context_id=glthread.newRenderContextCall(1,window_id,0)
      id_list.append((context_id,window_id)) # save context and window ids

    time.sleep(10)

    for ids in id_list:
      glthread.delRenderContextCall(ids[0])
      glthread.delRenderGroupCall(ids[1])
      
      
Presenting the same stream in several windows is a typical situation in video surveillance applications, where one would like to have the same stream be shown simultaneously in various "views" 

Keep in mind that here we have connected to the IP camera only once - and that the H264 stream has been decoded only once.

.. note:: When streaming video (from multiple sources) to multiple windows, OpenGL rendering synchronization to vertical refresh ("vsync") should be disabled, as it will limit your total framerate to the refresh rate of your monitor (i.e. to around 50 frames per second).  On MESA based X.org drivers (intel, nouveau, etc.), this can be achieved from command line with "export vblank_mode=0".  With nvidia proprietary drivers, use the nvidia-settings program.  You can test if vsync is disabled with the "glxgears" command (in package "mesa-utils").  Glxgears should report 1000+ frames per second with vsync disabled.

Decoding multiple streams
-------------------------

.. _multiple_streams:

**Download lesson** :download:`[here]<snippets/lesson_3_c.py>`

Let's consider decoding the H264 streams from multiple RTSP cameras.  For that, we'll be needing several decoding AVThreads.  Let's take another look at the filtergraph:

::

    Streaming part                                                                           
    (LiveThread:livethread) --> 1. {FifoFrameFilter:live_out_filter} --> 2. [FrameFifo: av_fifo] 
                                                                                  |
    Decoding part                                                                 |
        3. (AVThread:avthread) << ------------------------------------------------+    
                  |
                  |                                                                         Presentation part
                  +---> 4. {FifoFrameFilter:gl_in_filter} --> [OpenGLFrameFifo:gl_fifo] -->> (OpenGLThread:glthread)


Here we have numerated some parts in the graph with numbers 1-4.  While we only need a single LiveThread, OpenGLFrameFifo and OpenGLThread, we need multiple AVThreads, FrameFifos, etc. (everything that's been enumerated from 1-4).

In other words, LiveThread and OpenGLThread can deal with media streams in serial, while for decoding, we need one thread per decoder.  Take a look at the `library architecture page <https://elsampsa.github.io/valkka-core/html/process_chart.html>`_

It's a good idea to encapsulate (1-4) into a class:

::

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
    

Let's instantiate OpenGLThread and LiveThread and start them:
    
::
    

    # parameters are as follows: thread name, n720p, n1080p, n1440p, n4K
    glthread        =OpenGLThread ("glthread", 10, 10, 0, 0)
    gl_fifo         =glthread.getFifo()
    livethread      =LiveThread("livethread")

    glthread.startCall()
    livethread.startCall()


Instantiate LiveStreams.  This will also start the AVThreads.  Frames from 192.168.0.134 are tagged with slot number 1, while frames from 192.168.0.135 are tagged with slot number 2:
    
::    
    
    stream1 = LiveStream(gl_fifo, "rtsp://admin:123456@192.168.0.134", 1) # slot 1  
    stream2 = LiveStream(gl_fifo, "rtsp://admin:123456@192.168.0.135", 2) # slot 2


Register streams to LiveThread and start playing them:
    
::

    # register and start streams
    livethread.registerStreamCall(stream1.ctx)
    livethread.playStreamCall(stream1.ctx)

    livethread.registerStreamCall(stream2.ctx)
    livethread.playStreamCall(stream2.ctx)

Create x windows, and map slot numbers to certain x windows:
    
::
    
    # stream1 uses slot 1
    window_id1 =glthread.createWindow()
    glthread.newRenderGroupCall(window_id1)
    context_id1 =glthread.newRenderContextCall(1, window_id1, 0)

    # stream2 uses slot 2
    window_id2 =glthread.createWindow()
    glthread.newRenderGroupCall(window_id2)
    context_id2 =glthread.newRenderContextCall(2, window_id2, 0)

Render video for a while, stop threads and exit:
    
::
    
    time.sleep(10)

    glthread.delRenderContextCall(context_id1)
    glthread.delRenderGroupCall(window_id1)

    glthread.delRenderContextCall(context_id2)
    glthread.delRenderGroupCall(window_id2)

    # stop threads
    livethread.stopCall()
    glthread.stopCall()

    print("bye")

There are many ways to organize threads, render contexes (slot to x window mappings) and complex filtergraphs into classes.  It's all quite flexible and left for the API user.

One could even opt for an architecture, where there is a LiveThread and OpenGLThread for each individual stream (however, this is not recommended).

The level 2 API provides ready-made filtergraph classes for different purposes (similar to class LiveStream constructed here).
