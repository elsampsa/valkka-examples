.. raw:: html

    <style> .tiny {font-size: 8pt; color: blue} </style>

Modules
=======

Valkka consists of python modules, organized under the **valkka.** namespace, i.e. we're using the python "namespace packaging" scheme.

Cpp modules
-----------

Modules written in cpp are installed as debian packages, and the python parts are installed "globally" under

::

    /usr/lib/python3/dist-packages/valkka/
    
For instructions on how to create such a package, see `here <https://github.com/elsampsa/valkka-cpp-examples>`_

The valkka-core module belongs to this category
        
Pure python modules
-------------------

These are just normal python modules, installed typically with *pip3 install --user*


Module list
-----------

List of currently available modules.  *cpp* stands for a module written in cpp, while *python* indicates a pure python module.

.. table::
   :class: tiny
   
   +------------------+---------------------------------------------------------------+----------------+-----------------------------------------------------------------+
   | Namespace        | Explanation                                                   | Type           | URL                                                             |
   +------------------+---------------------------------------------------------------+----------------+-----------------------------------------------------------------+
   | valkka.core      | Valkka core module                                            | cpp            | (this page)                                                     |
   +------------------+---------------------------------------------------------------+----------------+-----------------------------------------------------------------+
   | valkka.api2      | Valkka core module, API level 2                               | python         | (this page)                                                     |
   +------------------+---------------------------------------------------------------+----------------+-----------------------------------------------------------------+
   | valkka.live      | Valkka Live video program                                     | python         | `Valkka Live <https://elsampsa.github.io/valkka-live/>`_        |
   +------------------+---------------------------------------------------------------+----------------+-----------------------------------------------------------------+
   | valkka.mvision   | Pure-python machine vision interface for Valkka Live          | python         | `Valkka Live <https://elsampsa.github.io/valkka-live/>`_        |
   +------------------+---------------------------------------------------------------+----------------+-----------------------------------------------------------------+
   


