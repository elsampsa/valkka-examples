Lesson 8: API level 2
=====================

General aspects
---------------

API level 2 tutorial codes are available at:

::

  cd valkka_examples/api_level_2/tutorial
  python3 lesson_8_a.py

So, by now you have learned how to construct complex framefilters to divert streams to filters, fifo queues and threads

Complex graphs of filters, queues and threads were encapsulated into a single, compact class in :ref:`lesson 3<multiple_streams>`.

API level 2 does just that.  It encapsulates some common cases into compact classes, starts the decoding threads for you, and provides easily accessible end-points (for the posix shared memory interface, etc.) for the API user.

The API level 2 filterchains can be accessed like this:
  
::

  from valkka.api2.chains import ..
  
  
API level 2 provides extra wrapping for the threads (LiveThread, OpenGLThread, etc.) as well.  The wrapped threads can be imported like this:

::

  from valkka.api2.threads import ...
  
  
the underlying API level 1 instances can be accessed like this:

::

  from valkka.api2.threads import LiveThread
  
  livethread=LiveThread("live_thread")
  livethread.core # this is the API level 1 instance, i.e. valkka.valkka_core.LiveThread

You should never import simultaneously from API levels 1 and two, i.e. from **valkka.valkka_core** and **valkka.api2.threads** as the threads have identical names; use either API level 1 or 2, but not both.


A simple example
----------------

**Download lesson** :download:`[here]<snippets/lesson_8_a.py>`

First, import API level 2:

::

  import time
  from valkka.api2.threads import LiveThread, OpenGLThread
  from valkka.api2.chains import BasicFilterchain

  
Instantiating a LiveThread starts running the thread.  Most of the parameters are optional:

::
  
  livethread=LiveThread( # starts live stream services (using live555)
    name   ="live_thread",
    verbose=False,
    affinity=-1
  )

Same goes for OpenGLThread:
  
::
  
  openglthread=OpenGLThread(
    name    ="glthread",
    n720p   =20,   # reserve stacks of YUV video frames for various resolutions
    n1080p  =20,
    n1440p  =0,
    n4K     =0,
    verbose =False,
    msbuftime=100,
    affinity=-1
  )

The filterchain and decoder (AVThread) are encapsulated into a single class.  Instantiating starts the AVThread (decoding is off by default):

::
  
  chain=BasicFilterchain( # decoding and branching the stream happens here
    livethread  =livethread, 
    openglthread=openglthread,
    address     ="rtsp://admin:nordic12345@192.168.1.41",
    slot        =1,
    affinity    =-1,
    verbose     =False,
    msreconnect =10000 # if no frames in ten seconds, try to reconnect
  )

BasicFilterchain takes as an argument the LiveThread and OpenGLThread instances.  It creates the relevant connections between the threads (fifo queues, etc.) under-the-hood.

Next, create an x-window, map stream to the screen, and start decoding:

::
  
  
  # create a window
  win_id =openglthread.createWindow()

  # create a stream-to-window mapping
  token  =openglthread.connect(slot=1,window_id=win_id) # present frames with slot number 1 at window win_id

  # start decoding
  chain.decodingOn()
  # stream for 20 secs
  time.sleep(20)

Finally, stop decoding and exit.  Threads are automatically stopped at garbage collection.
  
::
  
  chain.decodingOff()
  print("bye")

