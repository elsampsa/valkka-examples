.. valkka_examples documentation master file, created by
   sphinx-quickstart on Mon Mar 20 16:31:00 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Valkka
======

.. meta::
   :description: A python programming library for building opensource video surveillance, management and analysis programs with Qt
   :keywords: opensource, python, video surveillance, video management, video analysis, machine vision, qt

Valkka is a python programming library for creating video surveillance and management solutions for linux desktop in local area / virtual private networks.

*Some highlights of Valkka*

- Python3 API, while streaming itself runs in the background at the cpp level
- Works with stock OnVif compliant IP cameras
- Create complex filtergraphs for your streams - send stream to screen, to disk or to your module of choice via shared memory
- Share decoded video with python processes across your Linux system
- Plug in your python-based machine vision modules
- Designed for massive video streaming : view and analyze simultaneously a large number of IP cameras
- Recast the IP camera video streams to either multicast or unicast
- Build graphical user interfaces with PyQt, interact machine vision with Qt's signal/slot system and build highly customized GUIs

This documentation is a quickstart for installing and developing with Valkka using the Python3 API.  A Tutorial, a PyQt testsuite and some benchmarking results are provided.

For a demo program using Valkka, check out `Valkka Live <https://elsampsa.github.io/valkka-live/>`_

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
   onvif
   pitfalls
   repos
   license
   benchmarking
   authors
   
.. Indices and tables
.. ==================
.. * :ref:`genindex`
.. * :ref:`modindex`

* :ref:`search`
