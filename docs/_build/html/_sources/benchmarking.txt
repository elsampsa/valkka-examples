
Benchmarking
============

Here we touch upon some common problems in video surveillance and management software.  Tabulated tests using the PyQt testsuite are provided.


Bottlenecks
-----------

If your final rendering (performed by OpenGLThread) is dropping frames, resulting in sporadic video freezes, it is caused by one or many of the following common problems and/or bottlenecks (0-4):

0. Did you disable vsync and OpenGL compositor (see :ref:`here<testsuite>`) ?

1. Did you reserve enough frames on the GPU (do you see "no more frames.." output in the terminal) ?

Typical performance bottlenecks are:

2. Your LAN and/or the LiveThread process sending frames in bursts
  
  - Frames arrive late, and all in once.  You should increase the buffering time OpenGLThread.
  - This is very common problem when streaming over Wifi
  - Using several LiveThread(s), instead of just one *might* help
  
3. The AVThread(s) performing the decoding and uploading YUV bitmaps to GPU are taking too long

  - This is, of course, to be expected if all your CPU(s) are screaming 100%
  - Assign AVThreads to certain CPU(s) to check this and monitor the CPU usage

4. OpenGLThread that queues YUV frames and does the YUV => RGB interpolation on the GPU is stalling

  - There might still be some problems with the queueing/presenting algorithm (please do inform us!)
  - Your GPU might not have enough muscle

If you compile libValkka from source, there are many available debug options that can be enabled in *run_cmake.bash*.   A particularly useful one is *profile_timing*.  Enabling this debug switch allows you to trace the culprit for frame dropping to slow network, slow decoding or the OpenGL part.

Some common fixes (that are frequently used in commercial video surveillance applications) for problems (2-4) include:

* Configure your cameras to a lower frame rate (say, 10 fps)  
  
  - This sucks

* Reduce the YUV frame before sending it to GPU.

  - Uses still lots of resources for decoding

* Tell AVThread to send only every n:th frame to the GPU

  - Uses still lots of resources for decoding

* Tell AVThread to decode only keyframes

  - Choppy video

* The mainstream/substream scheme.  This is the best solution and it avoids problems (2-4) simultaneously

  - If you have, say, 20 small-sized video streams in your grid, it is an exaggeration to decode full-HD video for each one of the streams.  
  - For small windows, you should switch to using a substream provided by your IP camera.  A resolution of, say, half of HD-ready might be enough.  
  - Decode and present the full-HD mainstream only when there are video windows that are large enough

Valkka provides (or will provide) API methods and FrameFilter(s) to implement each one of these strategies.


Tests
-----

Here you will find some tabulated benchmark tests.  Tests are performed (if not otherwise mentioned) with the PyQt testsuite program "test_studio_1.py".  Parameters are same as in that program.  Some abbreviations are used:

====== ===========================
LIVA   = live affinity
GLA    = opengl affinity
D1A    = decoder affinity start
DNA    = decoder affinity stop
uptime = how long test was run
====== ===========================

Some tabulated benchmark tests follow **(under construction)**

=== ============ ============ ============  ======= ======= ======= ======= ======= ========= ========= ==== ==== ==== ==== ====== ==============================
N   pc           gf_driver    cameras       n_720p  n_1080p n_1440p n_4K    n_audio msbuftime replicate LIVA GLA  D1A  DNA  uptime  comments
=== ============ ============ ============  ======= ======= ======= ======= ======= ========= ========= ==== ==== ==== ==== ====== ==============================
1   | Ubuntu     | i915       | 16 x        | 400   | 400   | 400   | 10    | 0     | 500     | 1       | 0  | 1  | 2  | 7  |      | v0.4.5
    | 16.04 LTS  |            | full-HD,    |       |       |       |       |       |         |         |    |    |    |    |      | Mostly OK
    | 8xi7-4770  |            | 25 fps      |       |       |       |       |       |         |         |    |    |    |    |      | Sporadic framedrop
    
2   | Ubuntu     | i915       | 16 x        | 400   | 400   | 400   | 10    | 0     | 500     | 1       | 0  | 1  | 2  | 7  |      | v0.4.5
    | 16.04 LTS  |            | full-HD,    |       |       |       |       |       |         |         |    |    |    |    |      | Mostly OK
    | 8xi7-4770  |            | 25 fps      |       |       |       |       |       |         |         |    |    |    |    |      | Sporadic framedrop
=== ============ ============ ============  ======= ======= ======= ======= ======= ========= ========= ==== ==== ==== ==== ====== ==============================

