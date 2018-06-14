Supported hardware
==================

Cameras
-------

- You need an OnVif compliant cameras (supporting the RTSP protocol)
- For the moment, the only codec supported is H264


Linux clients
-------------

libValkka uses OpenGL and OpenGL texture streaming.   The library needs a robust OpenGL implementation.  As of **Ubuntu 16.04 LTS**, the working graphics drivers are:

- Intel: the stock **i915** driver works nicely
- Nvidia: use **nvidia** proprietary driver (instead of **noveau**)
- ATI: **not tested**
