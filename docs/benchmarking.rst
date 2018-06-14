.. raw:: html

    <style> .tiny {font-size: 8pt; color: blue} </style>


Benchmarking
============

Here you will find some tabulated benchmark tests.  Tests are performed (if not otherwise mentioned) with the :ref:`PyQt testsuite program<testsuite>` "test_studio_1.py".  Parameters are same as in that program.  Some abbreviations are used:

====== ===========================
LIVA   = live affinity
GLA    = opengl affinity
D1A    = decoder affinity start
DNA    = decoder affinity stop
uptime = how long test was run
====== ===========================

Some tabulated benchmark tests follow **(under construction)**


.. table::
   :class: tiny
   
   +--+------------+------------+------------+--------+---------+---------+-------+---------+-----------+-----------+------+-----+-----+-----+--------+------------------------------+
   |N |  pc        | gf_driver  |  cameras   | n_720p | n_1080p | n_1440p | n_4K  | n_audio | msbuftime | replicate | LIVA | GLA | D1A | DNA | uptime | comments                     |
   +--+------------+------------+------------+--------+---------+---------+-------+---------+-----------+-----------+------+-----+-----+-----+--------+------------------------------+
   |1 | Ubuntu     | i915       | 16 x       | 400    | 400     | 400     | 10    | 0       | 500       | 1         | 0    | 1   | 2   | 7   |        | v0.4.5                       |
   |  | 16.04 LTS  |            | full-HD,   |        |         |         |       |         |           |           |      |     |     |     |        | OK                           |
   |  | 8xi7-4770  |            | 25 fps     |        |         |         |       |         |           |           |      |     |     |     |        |                              |
   +--+------------+------------+------------+--------+---------+---------+-------+---------+-----------+-----------+------+-----+-----+-----+--------+------------------------------+



