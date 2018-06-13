
Lesson 2 : Decoding 
-------------------

**Download lesson** :download:`[here]<snippets/lesson_2_a.py>`

.. include:: snippets/lesson_2_a.py_

When using the API to pass frames between threads, that's all you need to know for now.

"Under the hood", however, things are a bit more complex.  The framefilter requested from AVThread writes into AVThread's internal *FrameFifo*.  This is a first-in-first-out queue where a copy of the incoming frame is placed.  Frames are copied into pre-reserved frames, taken from a pre-reserved stack.  Both the fifo and the stack are thread-safe and mutex-protected.  The user has the possibility to define the size of the stack when instantiating AVThread.  For more details, see the cpp documentation and especially the *FrameFifo* class.

However, all these gory details are not a concern for the API user at this stage.  :)

.. note:: There are several FrameFifo and Thread classes in Valkka.  See the `inheritance diagram <https://elsampsa.github.io/valkka-core/html/inherits.html>`_.  Only a small subset of the methods should be called by the API user.  These typically end with the word "Call" (and are marked with the "<pyapi>" tag).
