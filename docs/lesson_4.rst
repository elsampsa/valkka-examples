Lesson 4 : Sharing streams between python processes
===================================================

Server side
-----------

**Download server side** :download:`[here]<snippets/lesson_4_a.py>`

.. include:: snippets/lesson_4_a.py_

Next we need a separate python process, a client, that reads the frames.  Two versions are provided, the API level 2 being the most compact one.
    
.. note:: In the previous lessons, all streaming has taken place at the cpp level.  
          Here we are starting to use posix shared memory and semaphores in order to share frames between python processes, with the ultimate goal
          to share them with machine vision processes.  However, if you need very high-resolution and high fps solutions, you might want to implement the sharing 
          of frames and your machine vision routines directly at the cpp level.

Client side: API level 2
------------------------

**Download client side API level 2** :download:`[here]<snippets/lesson_4_a_client_api2.py>`

.. include:: snippets/lesson_4_a_client_api2.py_

(an older version of this code snippet is available :download:`[here]<snippets/lesson_4_a_client_api2_0_11_0.py>`)


Client side: openCV
-------------------

.. _opencv_client:

**Download client side openCV example** :download:`[here]<snippets/lesson_4_a_client_opencv.py>`

OpenCV is a popular machine vision library.  We modify the previous example to make it work with openCV like this:

.. include:: snippets/lesson_4_a_client_opencv.py_

Here the main difference to the previous example is, that the image data is reshaped.  After this, some gaussian blur is applied to the image.  Then it is visualized using openCV's own "high-gui" infrastructure.  If everything went ok, you should see a blurred image of your video once in a second.

Start this script *after* starting the server side script (server side must also be running).

(an older version of this code snippet is available :download:`[here]<snippets/lesson_4_a_client_opencv_0_11_0.py>`)


Client side: API level 1
------------------------

**Download client side example** :download:`[here]<snippets/lesson_4_a_client.py>`

API level 2 provides extra wrapping.  Let's see what goes on at the lowest level (plain, cpp wrapped python code).

.. include:: snippets/lesson_4_a_client.py_

(an older version of this code snippet is available :download:`[here]<snippets/lesson_4_a_client_0_11_0.py>`)

Cpp documentation for Valkka shared memory classes be found `here. <https://elsampsa.github.io/valkka-core/html/group__shmem__tag.html>`_


Advanced topics
---------------

By now you have learned how to pass frames from the libValkka infrastructure into a separate python program.

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




