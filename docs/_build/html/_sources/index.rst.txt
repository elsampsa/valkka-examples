.. valkka_examples documentation master file, created by
   sphinx-quickstart on Mon Mar 20 16:31:00 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Valkka
======

.. meta::
   :description: A python programming library for building opensource video surveillance, management and analysis programs with Qt
   :keywords: opensource, python, video surveillance, video management, video analysis, machine vision, qt

*Valkka is a python media streaming framework*

Create video streaming and surveillance solutions purely in Python.  No need to go C++ ever again.

*Some highlights of Valkka*

- Python3 API, while streaming itself runs in the background at the cpp level.  Threads, semaphores, frame queues etc. are hidden from the API user.
- Works with stock OnVif compliant IP cameras
- Create complex filtergraphs for your streams - send stream to screen, to disk or to your module of choice via shared memory
- Share decoded video with python processes across your Linux system
- Plug in your python-based machine vision modules : libValkka is framework agnostic, so everything goes - pytorch, tensorflow, you name it!
- Designed for massive video streaming : view and analyze simultaneously a large number of IP cameras
- Recast the IP camera video streams to either multicast or unicast
- Build graphical user interfaces with PyQt, interact machine vision with Qt's signal/slot system and build highly customized GUIs

If you are not a developer and wonder why all this is supposed to be cool and the economic benefits of it 
(an investor perhaps), please take a look at the Valkka VMS `whitepaper <https://drive.google.com/file/d/1bKCEqo3-30fiYNIbxkbD_OsgUcW1ycH_/view?usp=sharing>`_

Devs already involved knee-deep in the video streaming / machine vision business, might want to take a look 
at `this presentation <https://drive.google.com/file/d/19VXmhTYi19EKDlSorv-Tmd0gholeD9SJ>`_
to see some of the typical video streaming / machine vision problems libValkka can solve for you.

This documentation is a quickstart for :ref:`installing <requirements>` and developing with Valkka using the Python3 API.  

This is the recommended learning process:

- Start with the :ref:`tutorial <tutorial>`
- Proceed with `valkka-multiprocessing  <https://elsampsa.github.io/valkka-multiprocess/_build/html/index.html>`_ and the `multiprocessing
  examples <https://github.com/elsampsa/valkka-examples/tree/master/multiprocess>`_

After that, if you're

- into creating PyQt/PySide2 applications, take a look at :ref:`the PyQt testsuite<testsuite>`
- more into cloud apps, check out `valkka-streamer <https://github.com/elsampsa/valkka-streamer>`_

For a desktop proof-of-concept program using Valkka, check out `Valkka Live <https://elsampsa.github.io/valkka-live/>`_

.. toctree::
   :maxdepth: 2
   
   intro
   hardware
   requirements
   testsuite
   tutorial
   decoding
   qt_notes
   multi_gpu
   valkkafs
   cloud
   onvif
   pitfalls
   debugging
   repos
   license
   authors
   knowledge
   
.. Indices and tables
.. ==================
.. * :ref:`genindex`
.. * :ref:`modindex`

* :ref:`search`
