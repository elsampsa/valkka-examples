# Valkka Python3 Examples
In order to use these example python3 programs, you need to install (i) Valkka core library and (ii) Valkka python3 bindings, available at [Valkka main repository](https://github.com/elsampsa/valkka-core).

Install also some necessary dependencies for the python examples with:

    sudo apt-get install python3-pip ipython3 python3-pyqt5
    
To check that Valkka and its python3 bindings are in place, run "python3 quicktest.py" in the "major_version_0" directory.

Documentation is, at the moment, the python3 source code itself (I will be adding shortly more python3 examples plus more explanations in the existing python3 programs).  You should also study the main Valkka repository page first.

To replicate a single rtsp stream into various streams, use the "unicast_to_multicast.bash" script and "multicast.sdp".  You can give "multicast.sdp" various times as an argument to "multiple_stream.py":

    python3 multiple_stream.py multicast.sdp multicast.sdp ...

## Authors
Sampsa Riikonen

## Copyright
(C) 2017 Sampsa Riikonen

## License
MIT License
