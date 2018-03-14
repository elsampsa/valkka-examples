Lesson 5 : Sending frames to a multicast address
================================================

**Download lesson** :download:`[here]<snippets/lesson_5_a.py>`

In this lesson, we are receiving frames from an IP camera using LiveThread and recast those frames to a multicast address using another LiveThread. The filterchain looks like this:

:: 

  (LiveThread:livethread) --> {InfoFrameFilter:info_filter) --> {FifoFrameFilter:fifo_filter} --> [LiveFifo:live_fifo] -->> (LiveThread:livethread2) 


Let's start by importing Valkka and instantiating two LiveThreads:

::

  import time
  from valkka.valkka_core import *
  
  livethread  =LiveThread("livethread")
  livethread2 =LiveThread("livethread2",20) # reserve stack for incoming frames
  live_fifo   =livethread2.getFifo()

Here we have requested a special FrameFifo from the LiveThread that can be used to feed the frames.

Construct the filtergraph:

::

  
  fifo_filter =FifoFrameFilter("in_live_filter",live_fifo)
  info_filter =InfoFrameFilter("info_filter",fifo_filter)

  
Start threads:

::
  
  livethread. startCall()
  livethread2.startCall()

  
Define incoming and outgoing (multicast) streams:

::
  
  ctx     =LiveConnectionContext(LiveConnectionType_rtsp, "rtsp://admin:nordic12345@192.168.1.41", 2, info_filter)
  
i.e., incoming frames from IP camera 192.168.1.41 are tagged with slot number "2" and they are written to "info_filter".

All outgoing frames with slot number "2" are sent to port 50000:
  
::

  out_ctx =LiveOutboundContext(LiveConnectionType_sdp, "224.1.168.91", 2, 50000)

Start playing:

::
  
  livethread2.registerOutboundCall(out_ctx)
  livethread. registerStreamCall(ctx)
  livethread. playStreamCall(ctx)

Stream and recast to multicast for two minutes:

::
  
  time.sleep(120)

Stop and exit

::
  
  livethread. stopStreamCall(ctx)
  livethread. deregisterStreamCall(ctx)
  livethread2.deregisterOutbound(out_ctx)

  livethread. stopCall();
  livethread2.stopCall();

  print("bye")
  
  
.. _multicast:
  
To receive the multicast stream, you need this file, save it as "multicast.sdp":

::

  v=0
  o=- 0 0 IN IP4 127.0.0.1
  s=No Name
  c=IN IP4 224.1.168.91
  t=0 0
  a=tool:libavformat 56.36.100
  m=video 50000 RTP/AVP 96
  a=rtpmap:96 H264/90000
  a=fmtp:96 packetization-mode=1
  a=control:streamid=0

Then you can test that the stream is multicasted with:

::

  ffplay multicast.sdp
  
(feel free to launch that command several times simultaneously)

.. note:: Receiving and recasting the stream can also be done using a single LiveThread only.  This is left as an excercise.
