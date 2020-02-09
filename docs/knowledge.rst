Knowledge Base
**************

Tips, instructions, etc. for compiling libValkka, Qt & Yolo on out-of-the-ordinary hardware


General
=======

When compiling and generating yourself python binary packages these commands come handy:

::

    pip3 wheel --wheel-dir=YOUR_DIRECTORY -r requirements.txt
    pip3 install --no-index --find-links=YOUR_DIRECTORY -r requirements.txt

The first one downloads binary whl packages, defined in requirements.txt, from pypi.org to directory YOUR_DIRECTORY.

Next, put your manually compiled packages into YOUR_DIRECTORY

After that, launch the second command: it installs packages, defined in requirements.txt from YOUR_DIRECTORY.


References:

- https://pip.readthedocs.io/en/stable/user_guide/#installing-from-wheels


Jetson Nano
===========

Qt Python Bindings
------------------

There are two flavors of Qt Python bindings, namely, PyQt and PySide2.  Here we deal with the latter.  If you have information on PyQt on JetsonNano, please do send us an email.

PySide2 Qt python bindings are not available for all architectures simply from pypi using ``pip3 install`` command.  This is the case for Jetson Nano.  So we have to compile ourselves.


Install clang, build tools, Qt module clang header files, etc:

:: 

    sudo apt-get install git build-essential cmake libclang-dev qt5-default qtscript5-dev libssl-dev qttools5-dev qttools5-dev-tools qtmultimedia5-dev libqt5svg5-dev libqt5webkit5-dev libsdl2-dev libasound2 libxmu-dev libxi-dev freeglut3-dev libasound2-dev libjack-jackd2-dev libxrandr-dev libqt5xmlpatterns5-dev libqt5xmlpatterns5 libqt5xmlpatterns5-dev qtdeclarative5-private-dev qtbase5-private-dev qttools5-private-dev qtwebengine5-private-dev


Git clone PySide2 python bindings source code:

::

    git clone git://code.qt.io/pyside/pyside-setup.git
    cd pyside_setup


PySide2 python bindings must be compatible with your system's Qt version.  Find out the version with:

::

    qmake --version

For ubuntu 18 LTS for example, the version is 5.9.5, so:

::

    git checkout 5.9

Next, edit this file:

::

    sources/pyside2/PySide2/QtGui/CMakeLists.txt

Comment out (using #), these two lines:

::

    ${QtGui_GEN_DIR}/qopengltimemonitor_wrapper.cpp
    ${QtGui_GEN_DIR}/qopengltimerquery_wrapper.cpp

Finally, compile the bindings with:

::

    python3 setup.py build

That might take up to 8 hrs, so see a movie using your favorite streaming service.  :)

That compiles python bindings for all Qt features, so it could be a good idea to comment out more wrappers in that ``CMakeLists.txt``

After that, you can create a distributable package by:

::

    python3 setup.py --only-package bdist_wheel

The package appears in directory ``dist/`` and is installable with ``pip3 install --user packagename.whl``

References:

- https://github.com/PySide/pyside2/wiki/Dependencies
- https://wiki.qt.io/Qt_for_Python
- Pyside's ``setup.py`` : read the comments within the first lines
- https://bugreports.qt.io/browse/PYSIDE-568

