
.. _requirements:

Installing
==========


1. A Python3 package that includes pre-built binary libraries is available at the python package index (PyPI) and can be installed with:

  ::
  
    pip3 install --upgrade valkka
    

  The libraries have been built on **Ubuntu 16.04 LTS**, **x86_64** (there is no guarantee that they work on another setup).
    
  
  If pip gives you problems with the installation directory, use:
    
  ::
  
    pip3 install --upgrade --user valkka
  
  or even:
  
  ::
  
    pip3 install --upgrade --target=$HOME/.local/lib/python3.5/site-packages/ valkka
    
    
  If you need to build libValkka and it's python bindings yourself, please refer to the `valkka-core github page <https://github.com/elsampsa/valkka-core>`_.
  
      
2. OpenCV and its python bindings (with a working high-gui) for **python 3.5** are provided `here <https://www.dropbox.com/sh/cx3uutbavp2cqpa/AAC_uDh-plu0Oo50r_klYPEXa?dl=0)>`_.  Download them and use:

  :: 
    
      sudo dpkg -i OpenCV*.deb
      sudo apt-get -f install
  
  
3. Download this very package (valkka-examples) with

  ::
  
      git clone https://github.com/elsampsa/valkka-examples
      cd valkka_examples
      

.. Use the current stable version (that is compatible with the prebuilt python package):
.. cd valkka-examples      
.. git checkout 0.4.0
      
      
4. Test the installation with:


  ::
  
      python3 quicktest.py
  
  
  and you're all set.
  

Next, try out the :ref:`PyQt test/demo <testsuite>` suite or learn to program with the :ref:`tutorial <tutorial>`.
  
