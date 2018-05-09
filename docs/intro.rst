

.. Welcome!
.. As you can see, these are comments: they start with two dots and a space
.. Sphinx is very sensitive to spaces, empty lines, etc. so it can sometimes be frustrating
.. Two dots and a space are also used for special tagging, inclusion, etc.  Like here, where we are creating an internal link:

.. _intro:

.. So, lets start writing the documentation
.. Title fonts are written like this:

About Valkka
============

The problem
-----------

*So, yet another media player?  I need to stream video into my python/Qt program and I want something that can be developed fast and is easy to integrate into my code.  What's here for me?*

If you just need to stream video from your IP cameras, decode it and show it on the screen, we recommend a standard media player, say, VLC and its python bindings.

However, if you need to stream video and *simultaneously* (1) present it on the screen, (2) analyze it with machine vision, (3) write it to disk, and even (4) recast it to other clients, stock media players won't do.

Such requirements are typical in large-scale video surveillance, management and analysis solutions.  Demand for them is growing rapidly due to continuous decline in IP camera prices and growing computing power.

As a solution, you might try connect to the *same* camera 4 times and decode the stream 4 times - but then you'll burn all that CPU for nothing (you should decode only once).  And try to scale that only to, say, 20+ cameras.  In order avoid too many connections to your IP cameras (this is typically limited by the camera), you might desperately try your luck even with the multicast loopback.  We've been there and it's not a good idea.  And how about pluggin in your favorite machine vision/learning module, written with OpenCV or TensorFlow?

The solution
------------

Valkka will solve the problem for you; It is a programming library and an API to do just that - large scale video surveillance, management and analysis programs, from the comfort of python3.

With Valkka, you can create complex pipings ("filtergraphs") of media streams from the camera, to screen, machine vision subroutines, to disk, to the net, etc.  The code runs at the cpp level with threads, thread-safe queues, mutexes, semaphores, etc.  All those gory details are hidden from the API user that programs filtergraphs at the python level only.  Valkka can also share frames between python processes (and from there, with OpenCV, TensorFlow, etc.)

If you got interested, we recommend that you do the tutorial, and use the examples as a starting point.

This manual has a special emphasis for Qt and OpenCV.  You can create video streaming applications using PyQt: streaming video to widgets, and connect the signals from your machine vision subprograms to the Qt signal/slot system - and beyond.  

A test/benchmarking Qt test suite is provided :ref:`here <testsuite>`.

For more technical information, check out the `library architecture page <https://elsampsa.github.io/valkka-core/html/process_chart.html>`_

Finally, here is a small sample from the tutorial.  You'll get the idea.

::

  main branch, streaming
  (LiveThread:livethread) --> ----------------------------------+ 
                                                                |
                                                                |   
  {ForkFrameFilter: fork_filter} <----(AVThread:avthread) << ---+  main branch, decoding
                 |
        branch 1 +-->> (OpenGLThread:glthread) --> To X-Window System
                 |
        branch 2 +---> {IntervalFrameFilter: interval_filter} --> {SwScaleFrameFilter: sws_filter} --> {RGBSharedMemFrameFilter: shmem_filter}
                                                                                                                    |
                                                                                                To OpenCV  <--------+


The project
-----------

Valkka is in early beta stage.  Even so, you can do lot of stuff with it - all the things we have promised here in the intro, at least.  Check out the tentative project timetable :ref:`here<timetable>`

Valkka is open source software, licensed under the GNU Affero General Public License.  We also offer other licenses (mostly LGPL).

