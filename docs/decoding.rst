
.. _decoding:

Decoding
========

Single thread
-------------

By default, libValkka uses only a single core per decoder (the decoding threads can also be bound to a certain core - see :ref:`the testsuite<testsuite_decode>` for more details).

This is a good idea if you have a *large number of light streams*.  What is exactly a *light stream* depends on your linux box, but let's assume here that it is a 1080p video running approx. at 20 frames per second.

.. If a single core is capable of decoding the stream, there is no reason to create "thread swarming" and let all streams to use all cores (with decoders constantly switching from one set of cores to another). # we're being too smart here

Multithread
-----------

If you need to use a single *heavy stream*, then you might want to dedicate several cores in decoding a single stream.  A *heavy stream* could be example that 4000x3000 4K camera of yours running at 60 frames per second (!)

However, before using such a beast, you must ask yourself, do you really need something like that?

The biggest screen you'll ever be viewing the video from, is probably 1080p, while a framerate of 15 fps is good for the human eye.  Modern convoluted neural networks (yolo, for example), are using typically a resolution of ~ 600x600 pixels and analyzing max. 30 frames per seconds.  And we still haven't talked about clogging up your LAN.

If you really, really have to use several threads per decoder, modify tutorial's :ref:`lesson 2 <decoding_lesson>` like this:

::

    avthread = AVThread("avthread",info_filter)
    avthread.setNumberOfThreads(4)
    
That will dedicate four cores to the decoder.  Remember to call *setNumberOfThreads* before starting the AVThread instance.
    
GPU
---

(Nvidia) GPU accelerated decoding is not currently available, but will be in the near future.

.. _buffering:

Queueing frames
---------------

Typically, when decoding H264 video, handling the intra-frame takes much more time than decoding the consecutive B- and P-frames.  This is very pronounced for *heavy streams* (see above).

Because of that the intra frame will arrive late for the presentation, while the consecutive frames arrive in a burst.

This problem can be solved with buffering.  Modify tutorial's :ref:`lesson 3 <xwindow_lesson>` like this:

::

    from valkka.core import *

    glthread = OpenGLThread ("glthread")
        
    gl_ctx = core.OpenGLFrameFifoContext()
    gl_ctx.n_720p = 0
    gl_ctx.n_1080p = 0
    gl_ctx.n_1440p = 0
    gl_ctx.n_4K = 40

    glthread = OpenGLThread("glthread", gl_ctx, 500)
            
That will reserve 40 4K frames for queueing and presentation of video, while the buffering time is 500 milliseconds.  

For level 2 API, it would look like this:

::

    from valkka.api2 import *
    
    glthread = OpenGLThread(
        name ="glthread",
        n_720p = 0,
        n_1080p = 0,
        n_1440p = 0,
        n_4K = 0,
        msbuftime = 500
      )

Remember also that for certain class of frames (720p, 1080p, etc.):

::

    number of pre-reserved frames >= total framerate x buffering time

For testing, you should use the :ref:`test_studio_1.py <testsuite>` program.  See also :ref:`this <xwindow_lesson>` lesson of the tutorial.

Buffering solves many other issues as well.  If you don't get any image and the terminal screaming that "there are no more frames", then just enhance the buffering.


