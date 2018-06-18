

.. Welcome!
.. As you can see, these are comments: they start with two dots and a space
.. Sphinx is very sensitive to spaces, empty lines, etc. so it can sometimes be frustrating
.. Two dots and a space are also used for special tagging, inclusion, etc.  Like here, where we are creating an internal link:

.. _intro:

.. So, lets start writing the documentation
.. Title fonts are written like this:


About Valkka
============

  
Why this library?
-----------------

*So, yet another media player?  I need to stream video from my IP camera into my python/Qt program and I want something that can be developed fast and is easy to integrate into my code.  What's here for me?*

If you just need to stream video from your IP cameras, decode it and show it on the screen, we recommend a standard media player, say, VLC and its python bindings.

However, if you need to stream video and *simultaneously* (1) present it on the screen, (2) analyze it with machine vision, (3) write it to disk, and even (4) recast it to other clients, stock media players won't do.

Such requirements are typical in large-scale video surveillance, management and analysis solutions.  Demand for them is growing rapidly due to continuous decline in IP camera prices and growing computing power.

As a solution, you might try connect to the *same* camera 4 times and decode the stream 4 times - but then you'll burn all that CPU for nothing (you should decode only once).  And try to scale that only to, say, 20+ cameras.  In order avoid too many connections to your IP cameras (this is typically limited by the camera), you might desperately try your luck even with the multicast loopback.  We've been there and it's not a good idea.  And how about pluggin in your favorite machine vision/learning module, written with OpenCV or TensorFlow?

Valkka API
----------

Valkka will solve the problem for you; It is a programming library and an API to do just that - large scale video surveillance, management and analysis programs, from the comfort of python3.

With Valkka, you can create complex pipings ("filtergraphs") of media streams from the camera, to screen, machine vision subroutines, to disk, to the net, etc.  The code runs at the cpp level with threads, thread-safe queues, mutexes, semaphores, etc.  All those gory details are hidden from the API user that programs filtergraphs at the python level only.  Valkka can also share frames between python processes (and from there, with OpenCV, TensorFlow, etc.)

If you got interested, we recommend that you do the :ref:`tutorial<tutorial>`, and use it together with the :ref:`PyQt testsuite<testsuite>` as a starting point for your own projects.

This manual has a special emphasis for Qt and OpenCV.  You can create video streaming applications using PyQt: streaming video to widgets, and connect the signals from your machine vision subprograms to the Qt signal/slot system - and beyond.  

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


The Project
-----------

In Valkka, the "streaming pipeline" from IP cameras to decoders and to the GPU has been completely re-thinked and written from scratch:

- No dependencies on external libraries or x window extensions (we use only glx)
- Everything is pre-reserved in the system memory and in the GPU.  During streaming, frames are pulled from pre-reserved stacks
- OpenGL pixel buffer objects are used for texture video streaming (in the future, we will implement fish-eye projections)
- Customized queueing and presentation algorithms
- etc., etc.

Valkka is in alpha stage.  Even so, you can do lot of stuff with it - at least all the things we have promised here in the intro.

Repositories are organized as follows:

**valkka-core** : the cpp codebase and its python bindings are available at the `valkka-core github repository <https://github.com/elsampsa/valkka-core>`_.  The cpp core library is licensed under the GNU Affero General Public License.  If you need another licensing arrangement (say, LGPL), please contact us.

**valkka-examples** : the python tutorial and PyQt example/testsuite are available at the `valkka-examples github repository <https://github.com/elsampsa/valkka-examples>`_. MIT licensed.

**valkka-cpp-examples** : Valkka API is usable from cpp as well.  Examples of this and how to build your own Valkka extensions (FrameFilters, Threads) will be made available at some moment.  MIT licensed.

All functional features are demonstrated in the :ref:`tutorial<tutorial>` which is updated as new features appear.  Same goes for the :ref:`PyQt testsuite<testsuite>`.

We'd like to see the following features in the first beta release, coming online before end of 2018 (tentative; depending on available time and funding):

- Interserver communications between Valkka-based server and clients
- ValkkaFS filesystem, designed for recording large amounts of video
- Synchronized recording of video
- Picture-in-picture 
- Fisheye projections (trivial to implement as we are using OpenGL textures)
- Support for sound
- An ultralight OnVif client library, based on `Zeep <http://docs.python-zeep.org/en/master/>`_


Valkka is based on the following opensource libraries and technologies:

.. https://stackoverflow.com/questions/13497561/put-spacing-between-divs-in-a-horizontal-row

.. raw:: html

    <div style="overflow: hidden; position: relative;">
      <div style="float: left; margin: 5%; "><a href="http://www.live555.com/"> 
        <img class="logo" height=100 src="_static/svg/live.svg.png"></a>
        </br> Live555
      </div>
      <div style="float: left; margin: 5% "><a href="https://ffmpeg.org"> 
        <img class="logo" height=100 src="_static/svg/ffmpeg.svg.png"></a> 
        </br> FFmpeg Libav
      </div>
      <div style="float: left; margin: 5% "><a href="https://www.opengl.org/"> 
        <img class="logo" height=100 src="_static/svg/opengl.svg.png"></a> 
        </br> OpenGL
      </div>
    </div>

