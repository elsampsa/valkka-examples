.. _valkkafs_tutorial:

Lesson 11 : ValkkaFS
====================

As you learned from earlier lessons, you can redirect video streams to matroska (.mkv) video files.

Here we'll be streaming video to the custom ValkkaFS filesystem.

ValkkaFS dumps video to a dedicated file, or to an entire partition or disk.  Arriving H264 frames from all cameras are written in their arriving time order, into the same (large) file that is organized in blocks.  For more details, consult the :ref:`ValkkaFS section <valkkafs>` and the cpp documentation.

Here we provide two examples, one for writing to, and another one for reading from ValkkaFS.  Normally in an application, writing and reading would run in parallel: writing thread dumps frames continuously and reading thread evoked only at users request.

Writing
-------

Let's start by dumping video from IP cameras into ValkkaFS

**Download lesson** :download:`[here]<snippets/lesson_11_a.py>`

.. include:: snippets/lesson_11_a.py_
  
Reading
-------

Here we use the data written into ValkkaFS in the previous example

**Download lesson** :download:`[here]<snippets/lesson_11_b.py>`

.. include:: snippets/lesson_11_b.py_

Requesting blocks
-----------------

Here we use the data written into ValkkaFS in the writing example

**Download lesson** :download:`[here]<snippets/lesson_11_c.py>`

.. include:: snippets/lesson_11_c.py_




