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

Please first read this :ref:`word of warning <gpuaccel>`.

*VAAPI*

Comes in the basic libValkka installation (and uses ffmpeg/libav infrastructure) - no additional packages needed.

First of all, the user using VAAPI, must belong to the "video" user group:

.. code:: bash

    groups $USER
    # run the following command if the user does not appear in the video group
    sudo usermod -a -G video $USER
    # after that you still need to logout & login

In order to use the VAAPI acceleration, just replace `AVThread` with `VAAPIThread`, i.e. instead of

.. code:: python

    avthread = AVThread("avthread", target_filter)

use this:

.. code:: python

    avthread = VAAPIThread("avthread", target_filter)


For more details about VAAPI, you can read `this <https://wiki.archlinux.org/title/Hardware_video_acceleration>`_,
`this <https://wiki.debian.org/HardwareVideoAcceleration>`_ and `this <https://en.wikipedia.org/wiki/Video_Acceleration_API#Supported_hardware_and_drivers>`_.

*WARNING:* VAAPI, especially the intel implementation, comes with a memory leak, which seems
to be feature, not a bug - see discussions in `here <https://ffmpeg.org/pipermail/ffmpeg-user/2017-May/036232.html>`_ and
`here <https://github.com/mpv-player/mpv/issues/4383>`_.  I have confirmed this memory leak myself with libva 2.6.0.

The opensource Mesa implementation ("i965") is (surprise!) more stable and libValkka enforces i965 internally by setting the
environment variable `LIBVA_DRIVER_NAME` to `i965` (this happens when you do `from valkka.core import *`).

If you *really* want to use other `libva` implementation, you can set

.. code:: bash

    export VALKKA_LIBVA_DRIVER_NAME=your-driver-name

If you wish to use VAAPI in a docker environment, you should start docker with

.. code:: bash

    --device=/dev/dri:/dev/dri

And be sure that the host machine has all required vaapi-related libraries installed (the easiest way: install libValkka on the host as well).

Finally, you can follow the GPU usage in realtime with:

.. code:: bash

    sudo intel_gpu_top


*NVidia / CUDA*

Provided as a separate package that installs into the `valkka.nv` namespace and is used like this:

.. code:: python

    from valkka.nv import NVThread
    avthread = NVThread("avthread", target_filter, gpu_index)

Available `here <https://github.com/xiaxoxin2/valkka-nv>`_

*Huawei / CANN*

Provided as a separate package.  *Very* experimental and not guaranteed to work.  

Available `here <https://gitee.com/ElSampsa/valkka_cann>`_
