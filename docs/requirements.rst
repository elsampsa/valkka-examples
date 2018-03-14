
.. _requirements:

Installing
==========

1. Install two pre-built packages: the valkka-core debian package and the valkka bindings (a python .whl package) from `here <https://www.dropbox.com/sh/cx3uutbavp2cqpa/AAC_uDh-plu0Oo50r_klYPEXa?dl=0)>`_
  
- Install the valkka-core debian (.deb) package with: 

  ::

      sudo dpkg -i package_name
      sudo apt-get -f install
  
  
- Install the python3 binary package (.whl) with: 

  ::

      pip3 install --upgrade package_name

    
- You can find OpenCV debian packages there as well, in the case you need them
      
      
2. Download this very package (valkka-examples) with

  ::
  
      git clone https://github.com/elsampsa/valkka-examples


  Use the current stable version (that is compatible with the prebuild .deb and .whl packages):
    
  ::
  
      cd valkka-examples
      git checkout 0.3.0
      
      
3. Test the installation with:


  ::
  
      python3 quicktest.py
  
  
  and you're all set for the tutorial


