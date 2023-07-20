Supported hardware
==================

IP Cameras
----------

*OnVif compliant IP cameras (supporting the RTSP protocol)*

Initial configuration of IP cameras can be a hurdle:

Many IP cameras typically require a half-broken Active-X (!) web-extension you have to download 
(to use with some outdated version of internet explorer).

Once you have sorted out those manufacturer-dependent issues you are good to go with OnVif and the RTSP protocol (as supported by libValkka).

Axis cameras, on the other hand, have a decent (standard javascript) web-interface for camera initial configuration.

Once you have done succesfull initial configuration, you can test the rtsp connection, with, say, using ffmpeg:

::

    ffmpeg rtsp://user:password@ip-address


USB Cameras
-----------

*USB Cameras capable of streaming H264*  

We have tested against *Logitech HD Pro Webcam C920*

Codecs
------

For the moment, the only supported codec is H264

Linux clients
-------------

libValkka uses OpenGL and OpenGL texture streaming, so it needs a robust OpenGL implementation.  The current situation is:

- Intel: the stock **i915** driver is OK
- Nvidia: use **nvidia** proprietary driver
- ATI: **not tested**

OpenGL version 3 or greater is required.  You can check your OpenGL version with the command *glxinfo*.

.. _hwaccel:

Hardware Acceleration
---------------------

*VAAPI*

Comes in the basic libValkka installation (and uses ffmpeg/libav infrastructure) - no additional packages needed.

In order to use the VAAPI acceleration, just replace `AVThread` with `VAAPIThread`, i.e. instead of

.. code:: python

    avthread = AVThread("avthread", target_filter)

use this:

.. code:: python

    avthread = VAAPIThread("avthread", target_filter)
    
For more details about VAAPI, please read `this article <https://wiki.archlinux.org/title/Hardware_video_acceleration>`_

*NVidia / CUDA*

Provided as a separate package that installs into the `valkka.nv` namespace and is used like this:

.. code:: python

    from valkka.nv import NVThread
    avthread = NVThread("avthread", target_filter, gpu_index)

Available `here <https://github.com/xiaxoxin2/valkka-nv>`_

*Huawei / CANN*

Provided as a separate package.  *Very* experimental and not guaranteed to work.  

Available `here <https://gitee.com/ElSampsa/valkka_cann>`_
