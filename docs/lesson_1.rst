
Lesson 1 : Receiving frames from an IP camera
=============================================

A single FrameFilter
--------------------

**Download lesson** :download:`[here]<snippets/lesson_1_a.py>`

.. include:: snippets/lesson_1_a.py_


Chaining FrameFilters
---------------------

**Download lesson** :download:`[here]<snippets/lesson_1_b.py>`

.. include:: snippets/lesson_1_b.py_


Forking FrameFilters
--------------------

**Download lesson** :download:`[here]<snippets/lesson_1_c.py>`

.. include:: snippets/lesson_1_c.py_


FrameFilter reference
---------------------

API level 1 considered in this lesson, is nothing but cpp code wrapped to python. 

To see all available FrameFilters, refer to the `cpp documentation <https://elsampsa.github.io/valkka-core/html/group__filters__tag.html>`_.  

In the cpp docs, only a small part of the member methods are wrapped and visible from python (these are marked with the "pyapi" tag)

.. note:: FrameFilter chains are nothing but callback cascades - they will block the execution of LiveThread when executing code.  At some moment, the callback chain should terminate and continue in another, independent thread.  This will be discussed in the next lesson.


