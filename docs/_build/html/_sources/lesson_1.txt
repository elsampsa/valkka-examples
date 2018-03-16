
Lesson 1 : Receiving frames from an IP camera
=============================================

A single FrameFilter
--------------------

**Download lesson** :download:`[here]<snippets/lesson_1_a.py>`

Import valkka level 1 API:

::

  import time
  from valkka.valkka_core import *

  
Create a starting point for a FrameFilter chain:
  
::

  live_out_filter =InfoFrameFilter("live_out_filter")


This is the "entry point" where we receive all the frames.  

InfoFrameFilter does nothing fancy - it just prints out the frames it receives.  

However, as you will learn during this tutorials, FrameFilters can do a lot of stuff.  You can chain them into chains of arbitrary length.  They can be used to fork and copy the stream into complex graphs,  etc.
  
Next thing we need, is a thread that feeds the frames into our FrameFilter, so we instantiate a LiveThread:

::
  
  livethread =LiveThread("livethread")
  
We also need a context describing the connection to an IP camera:
  
::

  ctx =LiveConnectionContext(LiveConnectionType_rtsp, "rtsp://admin:nordic12345@192.168.1.41", 1, live_out_filter)

The first parameter defines the device type, which in this case is an rtsp IP camera.  Note that we include the "entry point" live_out_filter.  The integer parameter "1" is the slot number - it will be discussed in detail later on in this tutorial.
  
Finally, we can start streaming frames from the IP camera:
  
::

  livethread.startCall()
  livethread.registerStreamCall(ctx)
  livethread.playStreamCall(ctx)
  time.sleep(5)
  livethread.stopCall()
  
  
The output looks like this:

::

  InfoFrameFilter: live_out_filter start dump>> 
  InfoFrameFilter: FRAME   : <Frame: size=0/0 timestamp=1519987750663 subsession_index=0 slot=1 / Setup: frametype=5>
  InfoFrameFilter: PAYLOAD : []
  InfoFrameFilter:<>
  InfoFrameFilter: timediff: 0
  InfoFrameFilter: live_out_filter <<end dump   
  InfoFrameFilter: live_out_filter start dump>> 
  InfoFrameFilter: FRAME   : <Frame: size=45/307204 timestamp=1519987750663 subsession_index=0 slot=1 / H264: slice_type=7>
  InfoFrameFilter: PAYLOAD : [0 0 0 1 103 100 0 42 173 132 1 12 32 8 97 0 67 8 2 24 ]
  InfoFrameFilter:<>
  InfoFrameFilter: timediff: 0
  InfoFrameFilter: live_out_filter <<end dump   
  InfoFrameFilter: live_out_filter start dump>> 
  InfoFrameFilter: FRAME   : <Frame: size=9/307204 timestamp=1519987750663 subsession_index=0 slot=1 / H264: slice_type=8>
  InfoFrameFilter: PAYLOAD : [0 0 0 1 104 238 49 178 27 ]
  InfoFrameFilter:<>
  ...
  ...

InfoFrameFilter prints the frame type and first few bytes of it's payload (if there is any).

The first frame we get is a setup frame ("Setup: frametype=5").  This is a key feature of Valkka: the stream of frames that flows from source to the final sink, consists, not only of payload (say, H264 or PCMU), but of frames that are used to inform the library about the stream type and codec.

.. note:: The code itself (LiveThread, InfoFrameFilter) runs in c++, while the connections are programmed here, at the python level


Chaining FrameFilters
---------------------

**Download lesson** :download:`[here]<snippets/lesson_1_b.py>`

In the previous example, we had a thread (LiveThread), feeding a single FrameFilter (InfoFrameFilter).  This trivial filtergraph can be illustrated like this:


::

    (LiveThread:livethread) --> {InfoFrameFilter:live_out_filter}


In this notation, threads are marked with normal parenthesis (), and FrameFilters with curly brackets {}.  Class and instance names are included as well.  This is a good practice from the documentation point of view.

Let's chain some FrameFilters like this:

::

    (LiveThread:livethread) --> {InfoFrameFilter:live_out_filter} -> {InfoFrameFilter:filter_2} -> {InfoFrameFilter:filter_3}
    
That chain can be created in python like this:

::

    filter_3        =InfoFrameFilter("filter_3")
    filter_2        =InfoFrameFilter("filter_2",filter_3)
    live_out_filter =InfoFrameFilter("live_out_filter",filter_2)
    
    
The output when running the python code looks like this:
    
::

    InfoFrameFilter: live_out_filter start dump>> 
    ...
    InfoFrameFilter: live_out_filter <<end dump   
    InfoFrameFilter: filter_2 start dump>> 
    ...
    InfoFrameFilter: filter_2 <<end dump   
    InfoFrameFilter: filter_3 start dump>> 
    ...
    InfoFrameFilter: filter_3 <<end dump   

So, live_out_filter gets frame from livethread.  It prints out info about the frame.  Then it passes it to filter_2 that again prints information about the frame.  filter_2 passes the frame onto filter_3, etc.

.. note:: LiveThread has an internal FrameFilter chain that is used to correct the timestamps of your IP camera 
    

Forking FrameFilters
--------------------

**Download lesson** :download:`[here]<snippets/lesson_1_c.py>`

As a final trivial example for this lesson, we fork the FrameFilter chain into two:


::

    filtergraph:
                                                                       branch 1
                                                                       +------------> {GateFrameFilter: gate_filter}
    main branch                                                        |                 | 
    (LiveThread:livethread) --> {ForkFrameFilter:live_out_filter}  --> |                 +--- {InfoFrameFilter: info_filter}
                                                                       |
                                                                       +-------------> {FileFrameFilter: file_filter}
                                                                       branch 2         
                                                                                    

Frames are fed to a ForkFrameFilter that copies the stream into two branches.

At branch 1, there is an on/off gate.  When the gate is on, the frames are passed further on to the verbose InfoFrameFilter.

At branch 2, frames are written to a file

This filtergraph can be implemented in python like this:

::

    # branch 1
    info_filter     =InfoFrameFilter("info_filter")
    gate_filter     =GateFrameFilter("gate_filter",info_filter)

    # branch 2
    file_filter     =FileFrameFilter("file_filter")

    # main branch
    live_out_filter =ForkFrameFilter("live_out_filter",gate_filter,file_filter)
    livethread      =LiveThread("livethread")

    
.. note:: When defining FrameFilter graphs (or "trees"), creating the tree structure is always started from the outer leafs of the tree (in this case, from "info_filter", etc.) and moving from the outer edge towards the main branch.  This is simply because the inner parts of the tree are referring to the outer parts of the tree.
    
Let's run it like this:

::

    # close the gate before streaming
    gate_filter.unSet()

    livethread.startCall()
    livethread.registerStreamCall(ctx)
    livethread.playStreamCall(ctx)
    
    print("start writing to disk")
    file_filter.activate("stream.mkv")
    time.sleep(5)

    print("let's get verbose")
    gate_filter.set()
    time.sleep(2)

    print("close file and exit")
    file_filter.deActivate()

    livethread.stopCall()

    print("bye")

Here we first close the gate, so we get no information about the files to the terminal.  We write the stream to the disk by calling "activate" method of the FileFrameFilter.  After 5 secs. we turn on the gate and start getting information about the frames into the screen.  Finally we close the file by calling "deActivate".

You can play the resulting "stream.mkv" with your favorite media player.

.. note:: Valkka is *not* a mediaplayer that understands thousands of codecs and container formats.  Emphasis is on an internally consistent (for that a single or a few codec/container formats are enough, i.e. what we write we can also read) library that is capable of massive video streaming.  At the moment only H264 video is accepted.  Container format is matroska (mkv).


FrameFilter reference
---------------------

API level 1 considered in this lesson, is nothing but cpp code wrapped to python. 

To see all available FrameFilters, refer to the `cpp documentation <https://elsampsa.github.io/valkka-core/html/group__filters__tag.html>`_.  

In the cpp docs, only a small part of the member methods are wrapped and visible from python (these are marked with the "pyapi" tag)

.. note:: FrameFilter chains are nothing but callback cascades - they will block the execution of LiveThread when executing code.  At some moment, the callback chain should terminate and continue in another, independent thread.  This will be discussed in the next lesson.


