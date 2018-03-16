
Lesson 2 : Decoding 
-------------------

**Download lesson** :download:`[here]<snippets/lesson_2_a.py>`

Let's consider the following filtergraph:

::

    Streaming part                                                                          | Decoding part
                                                                                            |
    (LiveThread:livethread) --> {FifoFrameFilter:live_out_filter} --> [FrameFifo: av_fifo] -->> (AVThread:avthread) --> {InfoFrameFilter:info_filter}
    
    
Compared to the previous lesson, we have lot's of new stuff here.

So, again, LiveThread writes frames to "live_out_filter".  "live_out_filter" in turn writes to a class called "FrameFifo".

FrameFifo is a "first-in-first-out" (fifo) queue for frames.  One thread writes frames to the fifo, while another thread reads them, like this:

::

    LiveThread writes frames -->> [f5 f4 f3 f2 f1] -->> AVThread reads frames
    
So it acts as a bridge between independently running threads.  In our notation the ">>" arrow is used to emphasize cross-over between threads.

.. note:: FrameFifo has an internal stack of pre-reserved frames and mutex protection.  This works "under the hood" and is no concern for the API user.

In order to write into the FrameFifo, we need a special frame filter class FifoFrameFilter.

AVThread, on the other hand, reads directly from the fifo.  To keep things consistent, we follow this rule:

**Threads write into FrameFilter.  Threads read from FrameFifo**

Let's list all the symbols used until now and the corresponding objects:

====== ============ ==================================
Symbol Base class   Explanation
====== ============ ==================================
()     Thread       An independently running thread
>>                  Crossover between two threads
{}     FrameFilter  A framefilter
[]     FrameFifo    A fifo (first-in-first-out) queue
====== ============ ==================================

It's a good idea to use this consistent notation throughout your program development.

Finally, there is business as usual, on the "Decoding part": we could continue FrameFilter chains from AVThread, fork them, etc. as in the previous lesson.  In this example, we just print out the decoded (bitmap) frames.

The complete filterchain can be constructed like this:

::

    # used by both streaming and decoding parts
    av_fifo         =FrameFifo("av_fifo",10) 

    # streaming part
    livethread      =LiveThread("livethread")
    live_out_filter =FifoFrameFilter("live_out_filter",av_fifo)

    # decoding part
    info_filter     =InfoFrameFilter("info_filter")
    avthread        =AVThread("avthread",av_fifo,info_filter)

    
As usual, create a context describing the connection:

::
    
    ctx =LiveConnectionContext(LiveConnectionType_rtsp, "rtsp://admin:nordic12345@192.168.1.41", 1, live_out_filter)

  
Start both LiveThread and AVThread:
  
::

    avthread.startCall()
    livethread.startCall()

Order AVThread to start decoding:

::

    avthread.decodingOnCall()

Start streaming:

::

    livethread.registerStreamCall(ctx)
    livethread.playStreamCall(ctx)
    time.sleep(5)

Finally, stop streaming:

::

    # stop decoding
    avthread.decodingOffCall()

    # stop threads
    livethread.stopCall()
    avthread.stopCall()
    
You will see output like this:

::

    ...
    ...
    InfoFrameFilter: info_filter start dump>> 
    InfoFrameFilter: FRAME   : <Frame: size=0/0 timestamp=1519997727455 subsession_index=0 slot=1 / AVFRAME>
    InfoFrameFilter: PAYLOAD : []
    InfoFrameFilter:<AVFrame height         : 1080
    AVFrame width          : 1920
    AVFrame linesizes      : 1920 960 960
    AVFrame format         : 12
    AVCodecContext pix_fmt : 12
    >
    InfoFrameFilter: timediff: -48
    InfoFrameFilter: info_filter <<end dump  
    ...
    ...

So, instead of H264 packets, we have decoded bitmap frames here.

In the next lesson, we'll dump them on the screen.

.. note:: There are several FrameFifo and Thread classes in Valkka.  See the `inheritance diagram <https://elsampsa.github.io/valkka-core/html/inherits.html>`_.  Only a small subset of the methods should be called by the API user.  These typically end with the word "Call" (and are marked with the "<pyapi>" tag).

    

