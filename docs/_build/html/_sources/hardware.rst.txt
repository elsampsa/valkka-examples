Supported hardware
==================

Cameras
-------

- You need OnVif compliant camera(s) (supporting the RTSP protocol)
- For the moment, the only codec supported is H264


Linux clients
-------------

libValkka uses OpenGL and OpenGL texture streaming, so it needs a robust OpenGL implementation.  The current situation is:

- Intel: the stock **i915** driver is OK
- Nvidia: use **nvidia** proprietary driver (instead of **noveau**)
- ATI: **not tested**

OpenGL version 3 or greater is required.  You can check your OpenGL version with the command *glxinfo*.

