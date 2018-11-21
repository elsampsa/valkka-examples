Lesson 10 : USB Cameras
=======================

Valkka has experimental support for H264 streaming USB Cameras.  To see if your camera supports H264 streaming, use the following command:

::
    
    v4l2-ctl --list-formats -d /dev/video2

Information about your cameras can be found also under this directory structure:
    
::

    /sys/class/video4linux/

The only difference to handling IP cameras is that a different thread (*USBDeviceThread*) is used to stream the video.

**Download lesson** :download:`[here]<snippets/lesson_10.py>`

.. include:: snippets/lesson_10.py_
 
