
.. _requirements:

Installing
==========

1. You need to install two pre-built packages, available by clicking `here <https://www.dropbox.com/sh/cx3uutbavp2cqpa/AAC_uDh-plu0Oo50r_klYPEXa?dl=0)>`_
  
- Install the valkka-core debian (.deb) package with: 

  ::

      sudo dpkg -i package_name
      sudo apt-get -f install
  
  
- Install the python3 binary package (.whl) with: 

  ::

      pip3 install --upgrade package_name

      
- OpenCV and its python bindings (as debian packages) are provided as well.  Install also them (if not already installed in your system).
      
      
2. Install PyQt (needed for the Qt test/demo suite) with:


  ::
  
      pip3 install --upgrade PyQt5


      
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
  

