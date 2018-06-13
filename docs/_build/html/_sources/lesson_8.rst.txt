Lesson 8: API level 2
=====================

General aspects
---------------

API level 2 tutorial codes are available at:

::

  cd valkka_examples/api_level_2/tutorial
  python3 lesson_8_a.py

So, by now you have learned how to construct complex filtergraphs with framefilters and threads, and how to encapsulate parts of the filtergraphs into separate classes in :ref:`lesson 3<multiple_streams>`.

API level 2 does just that.  It encapsulates some common cases into compact classes, starts the decoding threads for you, and provides easily accessible end-points (for the posix shared memory interface, etc.) for the API user.

The API level 2 filterchains, threads and shared memory processes can be imported with
  
::

  from valkka.api2 import ...
  
  
API level 2 provides also extra wrapping for the thread classes (LiveThread, OpenGLThread, etc.).  The underlying API level 1 instances can be accessed like this:

::

  from valkka.api2 import LiveThread
  
  livethread=LiveThread("live_thread")
  livethread.core # this is the API level 1 instance, i.e. valkka.valkka_core.LiveThread


Keep in mind never to do a full import simultaneously from API levels one and two, i.e.

::

  # NEVER DO THIS!
  from valkka.valkka_core import *
  from valkka.api2 import *

as the threads (LiveThread, OpenGLThread, etc.) have indentical names.

The :ref:`PyQT testsuite <testsuite>` serves also as API level 2 reference.


A simple example
----------------

**Download lesson** :download:`[here]<snippets/lesson_8_a.py>`

.. include:: snippets/lesson_8_a.py_
