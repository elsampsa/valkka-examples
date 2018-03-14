
Programming with Qt
===================

General aspects
---------------

Valkka can be used with any GUI framework, say, with GTK or Qt.  Here we have an emphasis on Qt, but the general guidelines discussed here, apply to any other GUI framework as well.  Concrete examples are provided only for Qt.

For any GUI framework, this is what you want to do:

1. At the GUI's main window constructor, program your filtergraph and create signal/slot connections to Valkka's methods
2. Still at the main window ctor, start all threads
3. Start your GUI frameworks execution loop
4. At main window close event, close all threads

X-windows, i.e. "widgets" in the Qt slang, can be created at the Qt side and passed to Valkka.  Alternatively, x-windows can be created at the Valkka side and passed to Qt as "foreign widgets".  We recommend the latter approach.

Complex filterchains per camera should be encapsulated in classes, like we did in the :ref:`tutorial <multiple_streams>`.

Some typical filterclasses are readily accessible at the API 2 level and are suitable for direct integration into your Qt program.

Python multiprocessing
----------------------

In :ref:`lesson 4<opencv_client>` of the tutorial, we launched a separate python interpreter running a client program that was using shared frames from the camera.  

That approach works for Qt programs as well, but it is more convenient to use multiprocesses constructed with python3's `multiprocessing <https://docs.python.org/3/library/multiprocessing.html>`_ library.

Using python multiprocesses in a Qt program complicates things a bit, but not that much.  We simply need a way to map from events taking place at the multiprocess into signals at the main Qt program.  This can be done by communicating with the python multiprocess via pipes and converting the pipe messages into incoming and outgoing Qt signals.  

Let's state that graphically:

::

  Qt main loop running with signals and slots                                           
      |                                                                                  
      +--- QThread receiving/sending signals --- writing/reading communication pipes
           ==> use an instance of QValkkaThread               |
                                                         +----+----+
                                                         |    |    |
                                                         python multiprocesses doing their thing
                                                         and writing/reading their communication pipes
                                                         ==> subclass from api2.threads.ValkkaProcess

                                                         
For interprocess communication with the Qt signal/slot system, you can use the following strategy:

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
    |                          |    |  |          :    api2.threads.ValkkaProcess    
    +--------------------------+    |  |          :
    | Backend methods          |    |  |          :    Backend is running in the "background" at its own memory space
    |                          |    |  |          :
    | sendSignal_("ping")  ------->----+          :
    |                          |    |             :
    | watching childpipe <------- childpipe       :
    |                 |        |                  :
    | def pong_():  <-+        |                  :
    |  do something            |                  :
    |                          |                  :
    +--------------------------+                ..:
          
    

Two stripped-down sample programs are provided in

::

  valkka_examples/api_level_2/qt/
  
    multiprocessing_demo.py
    multiprocessing_demo_signals.py

    
Drawing video to a widget
-------------------------

TODO
    
    
    
Streaming from several cameras
------------------------------
    
For decoding, visualizing and analyzing a large number of cameras, filterchains should be encapsulated in classes, like we did in tutorial, :ref:`lesson 3<multiple_streams>`.  

API level 2 has several such classes that you might want to use.  The Qt test suite itself constitutes an example code for API level 2.


 




