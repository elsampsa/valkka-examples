Supported hardware
==================

Cameras
-------

- OnVif compliant IP cameras (supporting the RTSP protocol)
- USB Cameras capable of streaming H264.  We have tested against *Logitech HD Pro Webcam C920*
- For the moment, the only codec supported is H264


Linux clients
-------------

libValkka uses OpenGL and OpenGL texture streaming, so it needs a robust OpenGL implementation.  The current situation is:

- Intel: the stock **i915** driver is OK
- Nvidia: use **nvidia** proprietary driver
- ATI: **not tested**

OpenGL version 3 or greater is required.  You can check your OpenGL version with the command *glxinfo*.

