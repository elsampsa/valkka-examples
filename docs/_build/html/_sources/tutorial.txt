
.. _tutorial:

Tutorial
========

Using the tutorial
------------------

Once you have installed this package with git, the example codes of this tutorial can be run like this:

::

  cd valkka_examples/api_level_1/tutorial
  python3 lesson_1_a.py

Prerequisites
-------------

Before starting with the tutorial, you need at least:

- A decent desktop/laptop linux box with Ubuntu 16 installed
- At least 4 GB of total memory (as modern linux distros take around 2 GB out of that)
- Valkka and its python bindings installed (instructions :ref:`here <requirements>`)
- OpenCV installed (instructions :ref:`here <requirements>`)
- An RTSP camera connected to your router

  - Valkka uses standard protocols (RTSP, RTP, etc.), so it works with most of the cameras on the market
  - If your camera is onvif compliant, then it support RTSP and RTP

- Basic knowledge of media streaming in linux:

  - How to connect to an rtsp camera (e.g. "ffplay rtsp://username:passwd@ip_address")
  - What are RTSP, SDP, etc., what is H264 and how video is streamed, etc.

- A media player installed, say, vlc and/or ffplay

Lessons
-------
  
.. toctree::
   :maxdepth: 3

   lesson_1
   lesson_2
   lesson_3
   lesson_4
   lesson_5
   lesson_6
   lesson_7
   lesson_8

