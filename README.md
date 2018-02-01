# Valkka Python3 Examples
In order to use these example python3 programs, you need to install (i) Valkka core library and (ii) Valkka python3 bindings, available at [Valkka main repository](https://github.com/elsampsa/valkka-core).

Install also some necessary dependencies with

    sudo apt-get install python3-pip ipython3 python3-pyqt5
    
Install opencv with

    pip3 install opencv-python

Once you have done that and cloned this repo, do

    cd valkka-examples/major_version_0
    python3 quicktest.py
    
to see that you installed valkka correctly.
    
Documentation is at the moment, the python3 source code itself.  You should also study the documentation in the valkka-core repository.  To test valkka, do the following

    cd valkka-examples/major_version_0/api_level_2/qt
    export vblank_mode=0
    python3 test_studio_1.py

If you don't have that many ip cameras, you can replicate a single rtsp stream into various streams with the "unicast_to_multicast.bash" script (and using "multicast.sdp" as the input file).

## Combatibility
Valkka uses OpenGL.  It is important to disable the syncing to vertical refresh (a problem with glx).  Valkka has been tested with X.org/mesa drivers for Intel and Nvidia.  Nvidia proprietary drivers have not been tested.

## Authors
Sampsa Riikonen

## Copyright
(C) 2017, 2018 Sampsa Riikonen

## License
MIT License
