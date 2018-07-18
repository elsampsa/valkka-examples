
.. _requirements:

Installing
==========

Install valkka-core
-------------------

For recent ubuntu distributions, the core library binary packages and python bindings are provided by a PPA repository.  Subscribe to the PPA repo (do this only once) with:

::

  sudo apt-add-repository ppa:sampsa-riikonen/valkka
  
Install with:

::

    sudo apt-get update
    sudo apt-get install valkka
  

If you're not using a recent Ubuntu distro and need to build libValkka and it's python bindings yourself, please refer to the `valkka-core github page <https://github.com/elsampsa/valkka-core>`_.

The debian package includes the core library, its python bindings and some API level 2 python code.  The python part is installed "globally" into */usr/lib/python3/dist-packages/*

Install the testsuite
---------------------

First, install some debian packages:

::

  sudo apt-get install python3-pip git mesa-utils ffmpeg vlc x-tile 

some of these will be used for benchmarking Valkka agains other programs.

The testsuite and tutorials use also imutils and PyQt5, so install a fresh version of them locally with pip:

::

  pip3 install imutils PyQt5

Finally, for tutorial code and the PyQt test suite, download **valkka-examples** with:

::

    git clone https://github.com/elsampsa/valkka-examples
    
Test the installation with:

::
  
  cd valkka_examples
  python3 quicktest.py
  
  
and you're all set.
  
In the case of a numerical python version mismatch error, you are not using the default numpy provided by your Ubuntu distribution (from the debian package *python3-numpy*).  Remove the conflicting numpy installation with *pip3 uninstall* or setting up a virtualenv.
  
Next, try out the :ref:`PyQt test/demo <testsuite>` suite or learn to program with the :ref:`tutorial <tutorial>`.

OpenCV
------

There are many options available to install OpenCV and its python bindings.  A binary package with a working high-gui for **python 3.5** (used by Ubuntu 16 LTS) is provided `here <https://www.dropbox.com/sh/cx3uutbavp2cqpa/AAC_uDh-plu0Oo50r_klYPEXa?dl=0)>`_.  Download the files and use:

:: 
  
    sudo dpkg -i OpenCV*.deb
    sudo apt-get -fy install
  
  
