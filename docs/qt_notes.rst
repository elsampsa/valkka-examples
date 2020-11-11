
Integrating with Qt and multiprocessing
=======================================

Qt integration
--------------

Valkka can be used with any GUI framework, say, with GTK or Qt.  Here we have an emphasis on Qt, but the general guidelines discussed here, apply to any other GUI framework as well.  Concrete examples are provided only for Qt.

For any GUI framework, this is what you want to do:

1. At the GUI's main window constructor, program your filtergraph and create signal/slot connections to Valkka's methods
2. Still at the main window ctor, start all threads
3. Start your GUI frameworks execution loop
4. At main window close event, close all threads

X-windows, i.e. "widgets" in the Qt slang, can be created at the Qt side and passed to Valkka.  Alternatively, x-windows can be created at the Valkka side and passed to Qt as "foreign widgets".

Complex filterchains per camera should be encapsulated in classes, like we did in the :ref:`tutorial <multiple_streams>`.

Some typical filterchain classes are readily accessible at the API 2 level and are suitable for direct integration into your Qt program.


Drawing video into a widget
---------------------------

As you learned in the tutorial, we use the X-window window ids like this:

::

  context_id=glthread.newRenderContextCall(1,window_id,0)


That creates a mapping: all frames with slot number "1" are directed to an X-window with a window id "window_id" (the last number "0" is the z-stacking and is not currently used).

We can use the window id of an existing Qt widget "some_widget" like this:


::

  window_id=int(some_widget.winId())
  
There is a stripped-down example of this in

::

  valkka_examples/api_level_1/qt/
  
    single_stream_rtsp.py
  

However, it's a better idea to let Valkka create the X-window (with correct visual parameters, no XSignals, etc.) and embed that X-window into Qt.  This can be done with:

::

  foreign_window =QtGui.QWindow.fromWinId(win_id)
  foreign_widget =QtWidgets.QWidget.createWindowContainer(foreign_window,parent=parent)

  
where "win_id" is the window_id returned by Valkka, "parent" is the parent widget of the widget we're creating here and "foreign_widget" is the resulting widget we're going to use in Qt.

However, "foreign_widget" created this way does not catch mouse gestures.  This can be solved by placing a "dummy" QWidget on top of the "foreign_widget" (using a layout).  An example of this can be found in

::

  valkka_examples/api_level_1/qt/
  
    single_stream_rtsp_1.py

    
Streaming from several cameras
------------------------------
    
For decoding, visualizing and analyzing a large number of cameras, filterchains should be encapsulated in classes, like we did in tutorial, :ref:`lesson 3<multiple_streams>`.  

API level 2 has several such classes that you might want to use.  The Qt test suite itself constitutes an example code for API level 2.


Python multiprocessing
----------------------

In :ref:`lesson 4<opencv_client>` of the tutorial, we launched a separate python interpreter running a client program that was using decoded and shared frames.  

That approach works for Qt programs as well, but it is more convenient to use multiprocesses constructed with python3's `multiprocessing <https://docs.python.org/3/library/multiprocessing.html>`_ library.

Using python multiprocesses in a Qt program complicates things a bit, but not that much.  We simply need a way to map from events taking place at the separate and isolated multiprocess into signals at the main Qt program.  This can be done by communicating with the python multiprocess via pipes and converting the pipe messages into incoming and outgoing Qt signals.  

Let's state that graphically:

::

  Qt main loop running with signals and slots                                           
      |                                                                                  
      +--- QThread receiving/sending signals --- writing/reading communication pipes
           ==> use an instance of QValkkaThread                        |
                                                         +-------------+------+----------------+
                                                         |                    |                |
                                                        multiprocess_1   multiprocess_2  multiprocess_3
                                                         
                                                         python multiprocesses doing their thing
                                                         and writing/reading their communication pipes
                                                         ==> subclass from valkka.multiprocess.MessageProcess

  
Note that we only need a single QValkkaThread to control several multiprocesses.
                                                         
Let's dig deeper into our strategy for interprocess communication with the Qt signal/slot system:

::

   +--------------------------------------+
   |                                      |
   | QValkkaThread (derived from QThread) |
   |  watching the communication pipe     | 
   |                   +----- reads "ping"|  
   |                   |               |  | 
   +-------------------|------------------+
                       |               |
    +------------------|-------+       |        ...
    | Frontend methods |       |       ^          : 
    |                  |       |      pipe        : 
    | def ping():  <---+       |       |          :  
    |   do something           |       |          :
    |   (say, send a qt signal)|       |          :
    |                          |       |          : 
    | def pong(): # qt slot    |       |          :
    |   sendSignal("pong") ---------+  |          :
    |                          |    |  |          :    valkka.multiprocess.MessageProcess
    +--------------------------+    |  |          :
    | Backend methods          |    |  |          :    Backend is running in the "background" in its own virtual memory space
    |                          |    |  |          :
    | sendSignal_("ping")  ------->----+          :
    |                          |    |             :
    | watching childpipe <------- childpipe       :
    |                 |        |                  :
    | def pong_():  <-+        |                  :
    |  do something            |                  :
    |                          |                  :
    +--------------------------+                ..:
          
          
The class **valkka.multiprocess.MessageProcess** provides a model class that has been derived from python's **multiprocessing.Process** class.  
In MessageProcess, the class has both "frontend" and "backend" methods.  

Frontend methods can be called after the process has been started (e.g. after the .start() method has been called and fork has been performed), 
while backend methods are called only from within the processes "run" method - i.e. at the "other side" of the fork, where the forked process lives in its own virtual memory space.

A signalling scheme between back- and frontend is provided in the MessageProcess class.  Don't be afraid - the MessageProcess class is just a few lines of python code!
          
To make starting easier, two stripped-down sample programs are provided in:

::

  valkka_examples/api_level_2/qt/
  
    multiprocessing_demo.py
    multiprocessing_demo_signals.py

Try them with python3 to see the magic of python multiprocesses connecting with the Qt signal/slot system.

Finally, for creating your own Qt application having a frontend QThread, that controls OpenCV process(es), copy the following file into your own module:

::

  valkka_examples/api_level_2/qt/
  
    demo_multiprocess.py

It contains:

  - *QValkkaProcess* (a general multiprocess class with Qt signals)
  - *QValkkaOpenCVProcess* (multiprocess with Qt signals and OpenCV)
  - *QValkkaThread* (the frontend QThread) that you can use in your own applications.  

Consult the *test_studio_*.py* programs how to use these classes.

A more full-blown multiprocess orchestration example can be found as a separate python package, from `here <https://github.com/elsampsa/valkka-examples/tree/master/example_projects/basic>`_.

    
.. _multiprocess_warning:

Multiprocessing Warning
-----------------------

Before you go full-throttle into launching multiprocesses that pull frames from shared memory, please be aware of a very common multithread/processing pitfall:

**you should spawn your multiprocess before spawning threads**

Here "spawning the multiprocess" is a synonym to "fork".

You can expect many of the libraries you'll be using with Valkka, to rely heavily on multithreading.

A well-known problem arises, if you **first** import a library that **spawns several threads**, and **after** that perform a **fork**.  This leads to an undefined situation with "dangling" multithreads, creating segfaults and mysterious memory leaks.

In order to avoid all that, be sure to import your modules and instantiate your classes once and only once at the "backend" (see the discussion above), aka "the other side of the fork" of the multiprocess.

This boils down to a simple rule of thumb:

**Import external modules and instantiate the classes of those modules in your python multiprocess' run() method and nowhere else**

Ideally, you'd start the analyzing multiprocesses in the very beginning of your Qt program (that's what we're doing in the *valkka-live* demo program), and communicate them all necessary information when they're services are required.


Just use C++ instead of Python?
-------------------------------

There is no obligation to use Valkka from python - the API is usable from cpp as well.

If programming in Qt with C++ is your thing, then you can just forget all that multiprocessing considered here and use cpp threads instead.  

Say, you can use Valkka's FrameFifo and Thread infrastructure to create threads that read frames and feed them to an OpenCV analyzer (written in cpp).  This way you can skip posix shared memory and semaphores alltogether.  This is what you want to do for high-throughput video analysis (when you need that 20+ fps per second per camera in your OpenCV analyzer).

A python program using an example cpp thread (*TestThread*) which communicates with PyQt signals and slots can be found here:

::

  valkka_examples/api_level_2/qt/
  
    cpp_thread_demo.py

See also the documentation for the cpp source code of `TestThread <https://elsampsa.github.io/valkka-core/html/classTestThread.html>`_
    
Examples using the API with cpp will be added to this documentation in the near future.
