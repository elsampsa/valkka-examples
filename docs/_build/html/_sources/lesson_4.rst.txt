Lesson 4 : Receiving Frames at Python
=====================================

Here we start with two separate python programs: (1) a server that reads RTSP cameras and writes RGB frames into shared memory
and (2) a client that reads those RGB frames from memory.  For the client program, two versions are provided, the API level 2 being the most compact one.
    
Such scheme is only for demo/tutorial purposes.  Normally you would start both the server and client from within the same
python program.  We give an example of that as well.

Server side
-----------

**Download server side** :download:`[here]<snippets/lesson_4_a.py>`

.. include:: snippets/lesson_4_a.py_

.. note:: In the previous lessons, all streaming has taken place at the cpp level.  
          Here we are starting to use posix shared memory and semaphores in order to share frames between python processes, with the ultimate goal
          to share them with machine vision processes.  However, if you need very high-resolution and high fps solutions, you might want to implement the sharing 
          of frames and your machine vision routines directly at the cpp level.

Client side: API level 2
------------------------

**Download client side API level 2** :download:`[here]<snippets/lesson_4_a_client_api2.py>`

.. include:: snippets/lesson_4_a_client_api2.py_

Client side: openCV
-------------------

.. _opencv_client:

**Download client side openCV example** :download:`[here]<snippets/lesson_4_a_client_opencv.py>`

OpenCV is a popular machine vision library.  We modify the previous example to make it work with openCV like this:

.. include:: snippets/lesson_4_a_client_opencv.py_

After receiving the RGB frame, some gaussian blur is applied to the image.  Then it is visualized using openCV's own "high-gui" infrastructure.  
If everything went ok, you should see a blurred image of your video once in a second.

Start this script *after* starting the server side script (server side must also be running).


Client side: API level 1
------------------------

**Download client side example** :download:`[here]<snippets/lesson_4_a_client.py>`

API level 2 provides extra wrapping.  Let's see what goes on at the lowest level (plain, cpp wrapped python code).

.. include:: snippets/lesson_4_a_client.py_

Cpp documentation for Valkka shared memory classes be found `here. <https://elsampsa.github.io/valkka-core/html/group__shmem__tag.html>`_


Server + Client
---------------

**Download server + client example** :download:`[here]<snippets/lesson_4_b.py>`

Here we have a complete example running both server & client within the same python file.

You could wrap the client part further into a python thread, releasing your main python process
to, say, run a GUI.

Yet another possibility is to run the server and client in separate multiprocesses.  
In this case one must be extra carefull to spawn the multiprocesses *before* instantiating any libValkka objects,
since libValkka relies heavily on multithreading (this is the well-known "fork must go before threading" problem).

These problems have been addressed/resolved more deeply in the valkka-live video surveillance client.

But let's turn back to the complete server + client example

.. include:: snippets/lesson_4_b.py_


.. _fragmp4:

Receiving frag-MP4 at Python
----------------------------

**Download frag-MP4 example** :download:`[here]<snippets/lesson_4_c.py>`

Fragmented MP4 (frag-MP4) is a container format suitable for live streaming and playing the video in most web browsers.
For more information about this, see :ref:`here <cloud>`.

With libValkka you can mux your IP camera's H264 stream on-the-fly into frag-MP4 and then push it into cloud, using Python3 only.

This is similar what we have just done for the RGB bitmap frames.  Now, instead of RGB24 frames, we receive frag-MP4 to the python side.

And, of course, we could do all the following things simultaneously: decode, show on screen, push RGB24 frames for video analysis, push
frag-MP4 to your browser, etc. However, for clarity, here we just show the video on screen & receive frag-MP4 frames in our
python process.

.. include:: snippets/lesson_4_c.py_

Advanced topics
---------------

By now you have learned how to pass frames from the libValkka infrastructure into python.

When creating more serious solutions, you can use a single python program to span multiprocesses (using Python's multiprocessing module) into servers and clients.

In these cases you must remember to span all multiprocesses in the very beginning of your code and then arrange an interprocess communication between them, so that the multiprocesses
will instantiate the server and client in the correct order.

You can also create shared memory servers, where you can feed frames from the python side (vs. at the cpp side)

LibValkka shared memory server and client also features a posix file-descriptor API. It is convenient in cases, where a single process is listening simultaneously to several shared memory servers,
and you want to do the i/o efficiently: you can use python's "select" module to do efficient "multiplexing" of pulling frames from several shmem clients.

For example, the Valkka Live program takes advantage of these features.  It performs the following joggling of the frames through the shared memory:

1. Several shared memory servers, each one sending video from one camera.
2. Several client processes, each one receiving video from a shared memory server.  Each client process establish it's own shared memory server for further sharing of the frames.
3. A master process that listens to multiple clients at the same time.

Number (1) works at the cpp side.  (2) Is a separate multiprocess running OpenCV-based analysis.  (3) Is a common Yolo object detector for all the clients.




