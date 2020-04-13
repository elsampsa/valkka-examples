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



OpenCV & OpenCV contrib
=======================

Normally you might install OpenCV & its python bindings just with

::

    pip3 install --user --upgrade opencv-python opencv-contrib-python

The "contrib" module includes the "non-free" part (with patented algorithms etc.) of OpenCV library.  However, most of the time
this won't work either, since the libraries have been compiled with non-free algorithms disabled.

There's no other way here than to compile this by yourself.  You need to install (at least):

::

    sudo apt-get install build-essential cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev libv4l-dev python-dev python-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev libxvidcore-dev libx264-dev

Check out `opencv <https://github.com/opencv/opencv>`_ & `opencv-contrib <https://github.com/opencv/opencv_contrib>`_ from github.  
Add build directory and therein a file named run_cmake.bash.  Your directory structure should look like this:

::

    opencv/
        build/
            run_cmake.bash
    opencv-contrib/


run_cmake.bash looks like this:

::

    #!/bin/bash
    cmake   -D WITH_CUDA=OFF \
            -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules \
            -D OPENCV_ENABLE_NONFREE=ON \
            -D WITH_GSTREAMER=ON \
            -D WITH_LIBV4L=ON \
            -D BUILD_opencv_python2=OFF \                                                                                                                                       
            -D BUILD_opencv_python3=ON \
            -D CPACK_BINARY_DEB=ON \
            -D BUILD_TESTS=OFF \
            -D BUILD_PERF_TESTS=OFF \
            -D BUILD_EXAMPLES=OFF \
            -D CMAKE_BUILD_TYPE=RELEASE \
            -D CMAKE_INSTALL_PREFIX=/usr/local \
            ..

While at build directory, do

::

    ./run_cmake.bash
    make -j 4

There's a bug in the opencv build system, so we have to employ a 
`trick <https://stackoverflow.com/questions/45582565/opencv-cmake-error-no-such-file-or-directory-on-ubuntu>`_
before building the debian packages: comment out this line

::

    # set(CPACK_DEBIAN_PACKAGE_SHLIBDEPS "TRUE")

from "CPackConfig.cmake".  After that you should be able to run

::

    make package

Before installing all deb packages from the directory with

::

    sudo dpkg -i *.deb

remember to remove any pip-installed opencv and opencv contrib modules





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

