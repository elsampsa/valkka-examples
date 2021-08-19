
Common problems
===============

.. _pitfalls:

Pitfalls
--------

Valkka has been designed for massive video streaming.  
If your linux box, running a Valkka-based program, starts to choke up and you get frame jittering, stuttering / video freezes, and typically, this:

::

    OpenGLThread: handleFifo: DISCARDING late frame ...

You should consider the following issues:

**0\. Are you using correct Valkka version?**

Use the latest version.  When running the PyQt testsuite, remember to run *quicktest.py* to see if your installation is consistent.

**1\. Are you using sub-standard cameras?**

Nowadays the image quality is impressive in all stock IP cameras, however, the rtsp server and/or timestamping of the cameras can be buggy 
(there might be problems when maintaining several connections to the same camera, or when re-connecting several times to the same camera).

Before blaming us, *generate the same situation with a reference program*, say with ffplay, and see if it works or not.  
The :ref:`PyQt testsuite <testsuite>` offers nice tools for benchmarking agains ffplay and vlc.

**2\. Is your PC powerful enough to decode simultaneously 4+ full-hd videos?**  

*Test against a reference program* (ffplay).  Launch KSysGuard to monitor your processor usage.  Read also :ref:`this <decoding>`.

**3\. Have you told Valkka to reserve enough bitmap frames on the GPU?  Is your buffering time too large?**

The issue of pre-reserved frames and buffering time has been discussed :ref:`here <decoding>` and in the :ref:`PyQt testsuite section <testsuite_decode>`.

**4\. Disable OpenGL rendering synchronization to vertical refresh ("vsync").**

On MESA based X.org drivers (intel, nouveau, etc.), this can be achieved from command line with "export vblank_mode=0".  With nvidia proprietary drivers, use the *nvidia-settings* program.  
  
Test if vsync is disabled with the "glxgears" command.  It should report 1000+ frames per second with vsync disabled.

**5\. Disable OpenGL composition.**

In a KDE based system, go to *System Settings => Display and Monitor => Compositor* and uncheck "Enable compositor on startup".  
After that, you still have to restart your X-server (i.e. do logout and login).  CTRL-ALT-F12 might also work.  
In Xcfe based desktop, do *Settings Manager -> Window Manager Tweaks -> Compositor -> uncheck Enable Display Compositor*. 

Alternatively, you can user this command:

::

    dbus org.kde.KWin /Compositor suspend

**6\. Is your IP camera's time set correctly?**  

Valkka tries hard to correct the timestamps of arriving frames, but if the timestamps are "almost" right (i.e. off by a second or so), 
there is no way to know if the frames are stamped incorrectly or if they really arrive late..! 

So, either set your IP camera's clock really off (say, 5+ mins off) or exactly to the correct time.  
In the latter case, you might want to sync both your IP camera and PC to the same NTP server.

**7\. Are you really using a gigabit nic?**

How's your network interface hardware?  Using an old usb dongle?  Check your nic's capacity with this command:

::

    cat /sys/class/net/<device_name>/speed

It should say at least "100", preferably "1000"
    

Bottlenecks
-----------

Once you ramp up the number of streams, you might start to experience some *real* performance issues.  Some typical problems include:

**8\. Your LAN and/or the LiveThread process sending frames in bursts**
  
  - Frames arrive late, and all in once.  You should increase the buffering time OpenGLThread.  See :ref:`here <buffering>`.
  - This is very common problem when streaming over Wifi
  - If you observe broken frames, most likely your network interface is not keeping up.  What is the bandwith of your network and nic ? (as we just discussed.  See also "System tuning" below)
  
..  - Using several LiveThread(s), instead of just one *might* help
.. TODO: talk about the multicast loopback test  
  
**9\. The AVThread(s) performing the decoding and uploading to GPU are taking too long**

  - This is to be expected if all your CPU(s) are screaming 100%, so check that.

**10\. OpenGLThread is stalling**

If you have tried everything suggested on this page so far, but you're still getting

::

    OpenGLThread: handleFifo: DISCARDING late frame ...

Then the problem is in the last part of the pipeline: the OpenGLThread.  

It performs image interpolation and various other OpenGL calls, that, depending
on your driver's OpenGL implementation, might be efficient or not.  Generally, NVidia seems to perform better that Intel.

If you compile libValkka from source, there are many available debug options that can be enabled in *run_cmake.bash*.   
A particularly useful ones are *profile_timing* and *opengl_timing*.  Enabling these debug switch allows you to trace the culprit for frame dropping to slow network, slow decoding or the OpenGL part.

Some common fixes (that are frequently used in commercial video surveillance applications) include:

* Configure your cameras to a lower frame rate (say, 10 fps): unfortunately this sucks.
* Tell AVThread to decode only keyframes: choppy video.
* The mainstream/substream scheme:

  - If you have, say, 20 small-sized video streams in your grid, it is an exaggeration to decode full-HD video for each one of the streams.  
  - For small windows, you should switch to using a substream provided by your IP camera.  A resolution of, say, half of HD-ready might be enough.  
  - Decode and present the full-HD mainstream only when there are video windows that are large enough

.. * Reduce the YUV frame before sending it to GPU: however, we'll still use lots of resources for decoding. # this is not really the bottleneck ever
.. * Tell AVThread to send only every n:th frame to the GPU: unnecessary decoding of all arriving frames.
  
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

FAQ
---

*How can I stream over internet, instead of just LAN?*

By default, stream is transported through UDP sockets.  When streaming over internet, most of the ports are closed due to firewalls, etc., so you have to stream through the same TCP port
that is used for the RTSP negotiation (typically port 554).

Modify your LiveConnectionContext like this:

::

    ctx =LiveConnectionContext(LiveConnectionType_rtsp, "rtsp://admin:nordic12345@192.168.1.41", 1, live_out_filter)
    ctx.request_tcp = True

(for more information, see `here <https://elsampsa.github.io/valkka-core/html/structLiveConnectionContext.html>`_)
