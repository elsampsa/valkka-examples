Lesson 3 : Streaming to the X-window system
============================================

One camera to one window
------------------------

**Download lesson** :download:`[here]<snippets/lesson_3_a.py>`

.. include:: snippets/lesson_3_a.py_

So, all nice simple from the API.  

However, here it is important to understand what's going on "under-the-hood".  Similar to AVThread, OpenGLThread manages a stack of YUV bitmap frames.  These are pre-reserved on the GPU (for details, see the *OpenGLFrameFifo* class in the cpp documentation).

The number of pre-reserved frames you need, depends on the buffering time used to queue the frames.

You can adjust the number of pre-reserved frames for different resolutions and the buffering time like this:

::

    gl_ctx =OpenGLFrameFifoContext()
    gl_ctx.n_720p    =20
    gl_ctx.n_1080p   =20
    gl_ctx.n_1440p   =20
    gl_ctx.n_4K      =20

    glthread =OpenGLThread("glthread", gl_ctx, 300)

Here we have reserved 20 frames for each available resolution.  A buffering time of 300 milliseconds is used.
    
For example, if you are going to use two 720p cameras, each at 20 fps, with 300 millisecond buffering time, then you should reserve 

::

    2 * 20 fps * 0.3 sec = 12 frames
  
for 720p.  If this math is too hard for you, just reserve several hundred frames for each frame resolution (or until you run out of GPU memory).  :)


One camera to several windows
-------------------------------

**Download lesson** :download:`[here]<snippets/lesson_3_b.py>`

.. include:: snippets/lesson_3_b.py_

Presenting the same stream in several windows is a typical situation in video surveillance applications, where one would like to have the same stream be shown simultaneously in various "views" 

Keep in mind that here we have connected to the IP camera only once - and that the H264 stream has been decoded only once.

.. note:: When streaming video (from multiple sources) to multiple windows, OpenGL rendering synchronization to vertical refresh ("vsync") should be disabled, as it will limit your total framerate to the refresh rate of your monitor (i.e. to around 50 frames per second).  On MESA based X.org drivers (intel, nouveau, etc.), this can be achieved from command line with "export vblank_mode=0".  With nvidia proprietary drivers, use the nvidia-settings program.  You can test if vsync is disabled with the "glxgears" command (in package "mesa-utils").  Glxgears should report 1000+ frames per second with vsync disabled.


Decoding multiple streams
-------------------------

.. _multiple_streams:

**Download lesson** :download:`[here]<snippets/lesson_3_c.py>`

.. include:: snippets/lesson_3_c.py_
