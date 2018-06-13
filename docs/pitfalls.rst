
Common problems
===============

.. _pitfalls:

Pitfalls
--------

Valkka has been designed for massive video streaming.  If your linux box, running a Valkka-based program starts to choke up and you get frame jittering, video freezes, etc.  You should consider the following issues:

1\. Is your PC powerful enough to decode simultaneously 4+ full-hd videos?  Test against a reference program, say, ffplay.  Launch KSysGuard to monitor your processor usage.

2\. Have you told Valkka to reserve enough bitmap frames on the GPU?  Is your buffering time too large?  The issue of pre-reserved frames and buffering time has been discussed in the :ref:`PyQt testsuite section <testsuite>`.

3\. Disable OpenGL rendering synchronization to vertical refresh ("vsync").  

On MESA based X.org drivers (intel, nouveau, etc.), this can be achieved from command line with "export vblank_mode=0".  With nvidia proprietary drivers, use the *nvidia-settings* program.  
  
Test if vsync is disabled with the "glxgears" command.  It should report 1000+ frames per second with vsync disabled.

4\. Disable OpenGL composition.  

In a KDE based system, go to *System Settings => Display and Monitor => Compositor* and uncheck "Enable compositor on startup".  After that, you still have to restart your X-server (i.e. do logout and login).  CTRL-ALT-F12 might also work.

5\. Is your IP camera's time set correctly?  Valkka tries hard to correct the timestamps of arriving frames, but if the timestamps are "almost" right (i.e. off by a second or so), there is no way to know if the frames are stamped incorrectly or if they really arrive late..! 

So, either set your IP camera's clock really off (say, 5+ mins off) or exactly to the correct time.  In the latter case, you might want to sync both your IP camera and PC to the same NTP server.


Bottlenecks
-----------

Once you ramp up the number of streams, you might start to experience some *real* performance issues.  Some typical problems include:


6\. Your LAN and/or the LiveThread process sending frames in bursts
  
  - Frames arrive late, and all in once.  You should increase the buffering time OpenGLThread.
  - This is very common problem when streaming over Wifi
  - Using several LiveThread(s), instead of just one *might* help
  
7\. The AVThread(s) performing the decoding and uploading YUV bitmaps to GPU are taking too long

  - This is, of course, to be expected if all your CPU(s) are screaming 100%
  - Assign AVThreads to certain CPU(s) to check this and monitor the CPU usage

8\. OpenGLThread that queues YUV frames and does the YUV => RGB interpolation on the GPU is stalling

  - There might still be some problems with the queueing/presenting algorithm (please do inform us by creating a ticket in valkka-core's GitHub page).
  - Your GPU might not have enough muscle

If you compile libValkka from source, there are many available debug options that can be enabled in *run_cmake.bash*.   A particularly useful one is *profile_timing*.  Enabling this debug switch allows you to trace the culprit for frame dropping to slow network, slow decoding or the OpenGL part.

Some common fixes (that are frequently used in commercial video surveillance applications) for problems (6-8) include:

* Configure your cameras to a lower frame rate (say, 10 fps): this sucks.
* Reduce the YUV frame before sending it to GPU: we still use lots of resources for decoding.
* Tell AVThread to send only every n:th frame to the GPU: unnecessary decoding of all arriving frames.
* Tell AVThread to decode only keyframes: choppy video.
* The mainstream/substream scheme:

  - This is the best solution and it avoids problems (6-8) simultaneously
  - If you have, say, 20 small-sized video streams in your grid, it is an exaggeration to decode full-HD video for each one of the streams.  
  - For small windows, you should switch to using a substream provided by your IP camera.  A resolution of, say, half of HD-ready might be enough.  
  - Decode and present the full-HD mainstream only when there are video windows that are large enough

Valkka provides (or will provide) API methods and FrameFilter(s) to implement each one of these strategies.

System tuning
-------------

Adding the following lines into */etc/syscntl.conf*

::

  vm.swappiness = 1
  net.core.wmem_max=2097152
  net.core.rmem_max=2097152
  
And running

::

  sudo sysctl -p
  

Turns off swap and sets maximum allowed read/write socket sizes to 2 MB.

Receiving socket size can be adjusted for each live connection with the associated *LiveConnectionContext* (see the tutorial).  For an example how to do this, refer to **valkka.api2.basic.BasicFilterChain**

