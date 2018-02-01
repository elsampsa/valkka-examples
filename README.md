# Valkka Python3 Examples

(Tested on Ubuntu 16.04)

In order to use these example python3 programs, you need to install (i) Valkka core library and (ii) Valkka python3 bindings, available at [Valkka main repository](https://github.com/elsampsa/valkka-core).

Install also some necessary dependencies with

    sudo apt-get install python3-pip ipython3
    
Install pyqt and opencv with

    pip3 install pyqt5 opencv-python

That installs opencv and python bindings (at version 3.4.0.12).  A side note here: I could not make the OpenCV high-gui to work in that version (crasssh).  I'm using a home-compiled 3.1.0-dev version instead - that works.
    
Once you have done that and cloned this repo, do

    cd valkka-examples/major_version_0
    python3 quicktest.py
    
to see that you installed valkka correctly.
    
Documentation is at the moment the python3 source code itself.  You should also study the documentation in the valkka-core repository.  To test valkka, do the following

    cd valkka-examples/major_version_0/api_level_2/qt
    export vblank_mode=0
    python3 test_studio_1.py  

(disabling composition in your window manager may be a good idea)
    
If you don't have that many ip cameras, you can replicate a single rtsp stream into various streams with the "unicast_to_multicast.bash" script (and using "multicast.sdp" as the input file).

## Combatibility
Valkka uses OpenGL.  It is important to disable sync to vertical refresh (this seems to be a bug in glx - and a long story).  Valkka has been tested with X.org/mesa drivers for Intel and Nvidia.  Nvidia proprietary drivers have not been tested.

## Authors
Sampsa Riikonen

## Copyright
(C) 2017, 2018 Sampsa Riikonen

## License
MIT License

For production use, inform yourself about the PyQt5 license
