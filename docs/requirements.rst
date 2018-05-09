
.. _requirements:

Installing
==========

1. You need to install two pre-built packages, available by clicking `here <https://www.dropbox.com/sh/cx3uutbavp2cqpa/AAC_uDh-plu0Oo50r_klYPEXa?dl=0)>`_
  
- `Download <https://www.dropbox.com/sh/cx3uutbavp2cqpa/AAC_uDh-plu0Oo50r_klYPEXa?dl=0)>`_ the valkka-core debian (.deb) package and use:

  ::

      sudo dpkg -i Valkka*.deb
      sudo apt-get -f install
  
  
- `Download <https://www.dropbox.com/sh/cx3uutbavp2cqpa/AAC_uDh-plu0Oo50r_klYPEXa?dl=0)>`_ the python3 binary package (.whl) and use:

  ::

      pip3 install --upgrade Valkka*.whl

      
- OpenCV and its python bindings (two debian packages) are provided as well (with working high-gui).  `Download them <https://www.dropbox.com/sh/cx3uutbavp2cqpa/AAC_uDh-plu0Oo50r_klYPEXa?dl=0)>`_ and use:

  :: 
    
      sudo dpkg -i OpenCV*.deb
      sudo apt-get -f install
  
      
2. Install PyQt and imutils (needed for the Qt test/demo suite):


  ::
  
      pip3 install --upgrade PyQt5 imutils


      
3. Download this very package (valkka-examples) with

  ::
  
      git clone https://github.com/elsampsa/valkka-examples


  Use the current stable version (that is compatible with the prebuild .deb and .whl packages):
    
  ::
  
      cd valkka-examples
      git checkout 0.3.6
      
      
4. Test the installation with:


  ::
  
      python3 quicktest.py
  
  
  and you're all set.
  

Next, try out the :ref:`PyQt test/demo <testsuite>` suite or learn to program with the :ref:`tutorial <tutorial>`.
  

