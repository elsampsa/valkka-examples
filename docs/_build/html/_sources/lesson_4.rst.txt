Lesson 4 : Sharing streams between python processes
===================================================

Server side
-----------

**Download server side** :download:`[here]<snippets/lesson_4_a.py>`

.. include:: snippets/lesson_4_a.py_

Next we need a separate python process, a client, that reads the frames.  Two versions are provided, the API level 2 being the most compact one.
    
.. note:: In the previous lessons, all streaming has taken place at the cpp level.  Here we are starting to use posix shared memory and semaphores in order to share frames between python processes.  However, don't expect posix shared memory and semaphores to keep up with several full-hd cameras running at 25+ fps!  Such high-throughput should be implemented at the cpp level using multithreading (while defining only the connections at the python level)


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

Here the main difference to the previous example is, that the image data is reshaped.  After this, some gaussian blur is applied to the image.  Then it is visualized using openCV's own "high-gui" infrastructure.  If everything went ok, you should see a blurred image of your video once in a second.

Start this script *after* starting the server side script (server side must also be running).


Client side: API level 1
------------------------

**Download client side example** :download:`[here]<snippets/lesson_4_a_client.py>`

API level 2 provides extra wrapping.  Let's see what goes on at the lowest level (plain, cpp wrapped python code).

.. include:: snippets/lesson_4_a_client.py_

Cpp documentation for Valkka shared memory classes be found `here. <https://elsampsa.github.io/valkka-core/html/group__shmem__tag.html>`_
