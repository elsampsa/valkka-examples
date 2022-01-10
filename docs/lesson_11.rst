.. _valkkafs_tutorial:

Lesson 11 : ValkkaFS
====================

As you learned from earlier lessons, you can redirect video streams to matroska (.mkv) video files.

Here we'll be streaming video to the custom ValkkaFS filesystem.

ValkkaFS dumps video to a dedicated file, or to an entire partition or disk.  Arriving H264 frames are written in their arriving time order, into the same (large) file that is organized in blocks. 
For more details, consult the :ref:`ValkkaFS section <valkkafs>` and the cpp documentation.

Here we provide several examples for writing to and reading from ValkkaFS.  These include importing video from ValkkaFS to matroska, and caching frames from ValkkaFS and passing them downstream at play speed. 

In a typical VMS application, writing and reading run concurrently: writing thread dumps frames continuously to the disk, while reading thread is evoked only at user's request.


Writing
-------

Let's start by dumping video from IP cameras into ValkkaFS.

**Download lesson** :download:`[here]<snippets/lesson_11_a.py>`

.. include:: snippets/lesson_11_a.py_


Reading 1
---------

In these following two examples, we request frames from ValkkaFS

**Download lesson** :download:`[here]<snippets/lesson_11_b.py>`

.. include:: snippets/lesson_11_b.py_


Reading 2
---------

**Download lesson** :download:`[here]<snippets/lesson_11_c.py>`

.. include:: snippets/lesson_11_c.py_


Matroska export
---------------

Let's start by recalling :ref:`the very first lesson <lesson_1_a>`.  There we saw how LiveThread sends **Setup Frames** at streaming initialization.  
Setup frames are used all over the libValkka infrastructure, to carry information about the video stream, to signal the stream start and to initialize decoders, muxers, etc.

On the other hand, ValkkaFSReaderThread is designed to be a simple beast: it does not have any notion of stream initialization.  It simply provides frames on a per-block basis.

We must use a special FrameFilter called **InitStreamFrameFilter**, in order to add the Setup Frames into the stream. 

**Download lesson** :download:`[here]<snippets/lesson_11_d.py>`

.. include:: snippets/lesson_11_d.py_

Playing frames
--------------

As you learned in the previous examples of this section, ValkkaFSReader pushes frames downstream in "bursts", several blocks worth of frames in a single shot.

However, we also need something that passes recorded frames downstream (say, for visualization and/or for transmission) at "play speed" (say, at that 25 fps).

This is achieved with **FrameCacherThread**, which caches, seeks and passes frames downstream at play speed.  

In detail, ValkkaFSReaderThread passes frames to FrameCacherThread which caches them into memory.  After this, *seek*, *play* and *stop* can be requested from FrameCacherThread, 
which then passes the frames downstream from a seek point and at the original play speed at which the frames were recorded into ValkkaFS. 

FrameCacherThread can be given special python callback functions that are being called when the min and max time of cached frames changes and when frame presentation time goes forward.

FrameCacherThread is very similar to other threads that send stream (like LiveThread), so it also handles the sending of Setup Frames downstream correctly.

**Download lesson** :download:`[here]<snippets/lesson_11_e.py>`

.. include:: snippets/lesson_11_e.py_


ValkkaFSManager
---------------

In the previous example, two callback functions which define the application's behaviour with respect to recorded and cached frames were used.

How you define the callback functions, depends completely on your application, say, if you're creating an application that does playback of recorded stream, 
you might want to request new blocks at your *current_time_callback*, once the time goes over limits of currently cached frames.

We are starting to get some idea on the challenges that arise when doing *simultaneous reading, writing, caching and playing* of a large number
of (non-continuous) video streams.  For a more discussions on this, please see the :ref:`ValkkaFS section <valkkafs>`.

To make things easier, ``valkka.fs`` namespace has a special class ``ValkkaFSManager`` that handles the simultaneous & synchronous writing and playing of multiple video streams.

For an example on how to use ValkkaFSManager, please see ``test_studio_6.py`` at the :ref:`PyQt testsuite <testsuite>`.

