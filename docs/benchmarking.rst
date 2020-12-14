.. raw:: html

    <style> .tiny {font-size: 8pt; color: blue} </style>


Benchmarking
============

*not up-do-date / maintained*

Here you will find some tabulated benchmark tests.  Tests are performed (if not otherwise mentioned) with the :ref:`PyQt testsuite program<testsuite>` "test_studio_1.py".  Parameters are same as in that program.  Some abbreviations are used:

====== ===========================
LIVA   = live affinity
GLA    = opengl affinity
D1A    = decoder affinity start
DNA    = decoder affinity stop
uptime = how long test was run
====== ===========================

Benchmarks
----------

*(in newest-first order)*


.. table::
   :class: tiny
   
   +--+------------+------------+------------+--------+---------+---------+-------+---------+-----------+-----------+------+-----+-----+-----+-------------------+----------------------+
   |N |  pc        | gf_driver  |  cameras   | n_720p | n_1080p | n_1440p | n_4K  | n_audio | msbuftime | replicate | LIVA | GLA | D1A | DNA | kernel            | comments             |
   +--+------------+------------+------------+--------+---------+---------+-------+---------+-----------+-----------+------+-----+-----+-----+-------------------+----------------------+
   |2 | Ubuntu     | nvidia     | 18 x       | 600    | 600     | 600     | 10    | 0       | 500       | 1         | -1   | -1  | -1  | -1  | 4.15.0-51-generic | libValkka v0.12.0    |
   |  | 18.04 LTS  |            | 2560p      |        |         |         |       |         |           |           |      |     |     |     |                   |                      |
   |  | 8xi7-7700HQ|            | 25 fps     |        |         |         |       |         |           |           |      |     |     |     |                   |                      |
   |  | Laptop     |            |            |        |         |         |       |         |           |           |      |     |     |     |                   |                      |
   +--+------------+------------+------------+--------+---------+---------+-------+---------+-----------+-----------+------+-----+-----+-----+-------------------+----------------------+

|

.. table::
   :class: tiny
   
   +--+------------+------------+------------+--------+---------+---------+-------+---------+-----------+-----------+------+-----+-----+-----+--------+------------------------------+
   |N |  pc        | gf_driver  |  cameras   | n_720p | n_1080p | n_1440p | n_4K  | n_audio | msbuftime | replicate | LIVA | GLA | D1A | DNA | uptime | comments                     |
   +--+------------+------------+------------+--------+---------+---------+-------+---------+-----------+-----------+------+-----+-----+-----+--------+------------------------------+
   |1 | Ubuntu     | i915       | 16 x       | 400    | 400     | 400     | 10    | 0       | 500       | 1         | 0    | 1   | 2   | 7   |  ?     | libValkka v0.4.5             |
   |  | 16.04 LTS  |            | 1920p      |        |         |         |       |         |           |           |      |     |     |     |        |                              |
   |  | 8xi7-4770  |            | 25 fps     |        |         |         |       |         |           |           |      |     |     |     |        |                              |
   +--+------------+------------+------------+--------+---------+---------+-------+---------+-----------+-----------+------+-----+-----+-----+--------+------------------------------+

|
Debugging
=========

LibValkka is rigorously "valgrinded" to remove any memory leaks at the cpp level.  However, combining cpp and python (with swig) and throwing into the mix multithreading, multiprocessing and 
sharing memory between processes, can (and will) give surprises.

**1\. Check that you are not pulling frames from the same shared-memory channel using more than one client**

**2\. Run Python + libValkka using gdb**

First, install python3 debugging symbols:

::

    sudo apt-get install gdb python3-dbg

Then, create a custom build of libValkka with debug symbols enabled.

Finally, run your application's entry point with:

::

    gdb --args python3 python_program.py
    run

See backtrace with

::

    bt

If the trace point into ``Objects/obmalloc.c``, then the cpp extensions have messed up python object reference counting.  See also `here <https://stackoverflow.com/questions/26330621/python-segfaults-in-pyobject-malloc>`_


**3\. Clear semaphores and shared memory every now and then by removing these files**

::

    /dev/shm/*valkka*


**4\. Follow python process memory consumption**

Use the `setproctitle python module <https://github.com/dvarrazzo/py-setproctitle>`_ to name your python multiprocesses.  This way you can find them easily using standard
linux monitoring tools, such as htop and smem.

Setting the name of the process should, of course, happen after the multiprocessing fork.

Install smem and htop:

::

    sudo apt-get install smem htop

After that, run for example the script memwatch.bash in the aux/ directory.  Or just launch htop.  In htop, remember to go to setup => display options and enable "Hide userland process threads" to make
the output more readable.

Valkka-live, for example, names all multiprocesses adequately, so you can easily see if a process is
leaking memory.

**\5. Prefer PyQt5 over PySide2**

You have the option of using PyQt5 instead of PySide2.  The former is significantly more stable and handles the tricky
cpp Qt vs. Python reference counting correctly.  Especially if you get that thing mention in (2), consider switching to PyQt5.
