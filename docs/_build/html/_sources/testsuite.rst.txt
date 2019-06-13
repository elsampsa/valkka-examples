
.. _testsuite:

The PyQt testsuite
==================

So, you have installed valkka-core and valkka-examples as instructed :ref:`here<requirements>`.  The same hardware requirements apply here as in the :ref:`tutorial<tutorial>`.

The PyQt testsuite is available at

::

  valkka_examples/api_level_2/qt/

The testsuite is intended for:

 - Demonstration
 - Benchmarking 
 - Ultimate debugging
 - As *materia prima* for developers - take a copy of your own and use it as a basis for your own Valkka / Qt program
 
If you want a more serious demonstration, try out `Valkka Live <https://elsampsa.github.io/valkka-live/>`_ instead.
 
Currently the testsuite consists of the following programs:

========================== ================================================================================
File                       Explanation
========================== ================================================================================
test_studio_1.py           | - Stream from several rtsp cameras or sdp sources
                           | - Widgets are grouped together
                           | - This is just live streaming, so use:
                           |
                           |   *rtsp://username:password@your_ip*
                           |
                           | - If you define a filename, it is interpreted as an sdp file
                           |
test_studio_2.py           | - Like *test_studio_1.py*
                           | - Floating widgets
                           |
test_studio_3.py           | - Like *test_studio_2.py*
                           | - On a multi-gpu system, video can be sent to another gpu/x-screen pair
                           |
test_studio_4.py           | - Like *test_studio_3.py*
                           | - A simple user menu where video widgets can be opened
                           | - Open the *File* menu to add video on the screen
                           |                           
test_studio_detector.py    | - Like *test_studio_1.py*
                           | - Shares video to OpenCV processes
                           | - OpenCV processes connect to Qt signal/slot system 
                           |
test_studio_file.py        | - Read and play stream from a matroska file
                           | - Only matroska contained h264 is accepted.  
                           | - Convert your video with:
                           |
                           |   *ffmpeg -i your_video_file -c:v h264 -an outfile.mkv*
                           |
test_studio_multicast.py   | - Like *test_studio_1.py*
                           | - Recast multiple IP cameras into multicast
                           |
test_studio_rtsp.py        | - Like *test_studio_1.py* 
                           | - Recast IP cameras to unicast.  
                           | - Streams are accessible from local server:
                           |
                           |   *rtsp://127.0.0.1:8554/streamN*
                           |
                           |   (where *N* is the number of the camera)
                           | 
test_studio_5.py           | **experimental**
                           | - Continuous recording to :ref:`ValkkaFS <valkkafs>`
                           | - and simultaneous, interactive playback
                           | - remove directory ``fs_directory/``` if the program refuses to start
========================== ================================================================================

Before launching any of the testsuite programs you should be aware of the :ref:`common problems<pitfalls>` of linux video streaming.

test_studio_1.py
----------------

Do this:

::

  cd valkka_examples/api_level_2/qt/
  python3 test_studio_1.py

The program launches with the following menu:

.. image:: images/test_config.png
   :width: 70 %
   
   
The field on the left is used to specify stream sources, one source per line.  For IP cameras, use "rtsp://", for sdp files, just give the filename.  In the above example, we are connecting to two rtsp IP cams.

The fields on the right are:

=========================== ================================================================
Field name                  What it does
=========================== ================================================================
n720p                       Number of pre-reserved frames for 720p resolution
n1080p                      Number of pre-reserved frames for 1080p resolution
n1440p                      etc.
n4K                         etc.
naudio                      (not used)
verbose                     (not used)
msbuftime                   Frame buffering time in milliseconds
live affinity               Bind the streaming thread to a core. Default = -1 (no binding)
gl affinity                 Bind frame presentation thread to a core. Default = -1
dec affinity start          Bind decoding threads to a core (first core). Default = -1
dec affinity stop           Bind decoding threads to cores (last core). Default = -1
replicate                   Dump each stream to screen this many times
correct timestamp           | 1 = smart-correct timestamp (use this!)
                            | 0 = restamp upon arrival
socket size bytes           don't touch.  Default value = 0.
ordering time millisecs     don't touch.  Default value = 0.
=========================== ================================================================

.. _testsuite_decode:

As you learned from the :ref:`tutorial<tutorial>`, in Valkka, frames are pre-reserved on the GPU.  If you're planning to use 720p and 1080p cameras, reserve, say 200 frames for both.

Decoded frames are being queued for "msbuftime" milliseconds.  This is necessary for de-jitter (among other things).  The bigger the buffering time, the more pre-reserved frames you'll need and the more lag you get into your live streaming.  A nice value is 300.  For more on the subject, read :ref:`this <decoding>`.

Replicate demonstrates how Valkka can dump the stream (that's decoded only once) to multiple X windows.  Try for example the value 24 - you get each stream on the screen 24 times, without any performance degradation or the need to decode streams more than once.

In Valkka, all threads can be bound to a certain processor core.  Default value "-1" indicates that the thread is unbound and that the kernel can switch it from one core to another (normal behaviour).

Let's consider an example:

=================== =====
Field name          value
=================== =====
live affinity       0
gl affinity         1
dec affinity start  2
dec affinity stop   4
=================== =====

Now LiveThread (the thread that streams from cameras) stays at core index 0, all OpenGL operations and frame presenting at core index 1.  Let's imagine you have ten decoders running, then they will placed like this:

======== ==============
Core     Decoder thread
======== ==============
core 2   1, 4, 7, 10
core 3   2, 5, 8
core 4   3, 6, 9
======== ==============
   
.. Before starting the test suite, you can use the script
.. !!this is al sooo niche
.. valkka_examples/aux/
..   
..  process_crowd.bash
.. to throw all system processes into core 0.

Setting processor affinities might help, if you can afford the luxury of having one processor per decoder.  Otherwise, it might mess up the load-balancing performed by the kernel.  

**By default, don't touch the affinities (simply use the default value -1)**.

Finally, the buttons that launch the test, do the following:

============= ====================================================
Button        What it does?
============= ====================================================
SAVE          Saves the test configuration (yes, save it)
**RUN(QT)**   Runs THE TEST (after saving, press this!)
RUN           Runs the test without Qt
FFPLAY        Runs the streams in ffplay instead (if installed)
VLC           Runs the streams in vlc instead (if installed)
============= ====================================================

*RUN(QT)* is the thing you want to do.

*FFPLAY* and *VLC* launch the same rtsp streams by using either ffplay or vlc.  This is a nice test to see how Valkka performs against some popular video players.

test_studio_detector.py
-----------------------

The detector test program uses OpenCV, so you need to have it :ref:`installed <install_opencv>`

Launch the program like this:

::

  cd valkka_examples/api_level_2/qt/
  python3 test_studio_detector.py

This is similar to *test_studio_1.py*.  In addition to presenting the streams on-screen, the decoded frames are passed, once in a second, to OpenCV movement detectors.  When movement is detected, a signal is sent with the Qt signal/slot system to the screen.

This test program is also used in the *gold standard test*.  Everything is here: streaming, decoding, OpenGL streaming, interface to python and even the posix shared memory and semaphores.  One should be able to run this test with a large number of cameras for a long period of time without excessive memory consumption or system instabilities.




