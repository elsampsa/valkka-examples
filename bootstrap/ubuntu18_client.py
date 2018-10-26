#!/usr/bin/python
"""
Start from Ubuntu 18 install, then run this
"""
import os

pklis=[
  "emacs",
  # "openssh-server",
  "encfs",
  "msttcorefonts",
  "kubuntu-desktop",
  "xubuntu-desktop",
  "kwrite",
  "kate",
  
  "curl", # http calls
  "k4dirstat",   # keeping your disk clean .. visualizes disk usage
  
  "iotop",

  "pavucontrol", 
  
  "vlc",
  "ffmpeg",
  "x-tile",
  
  "imagemagick",
  "inkscape",
  "gimp",
  "mkvtoolnix",
  "mkvtoolnix-gui",
  
  "wireshark",
  "git",
  "valgrind",
  
  "fakeroot",

  # databases
  "mongodb",
  
  "ipython3",
  "python3-pymongo",
  "python3-pip",
  "python3-stdeb", # needed for making .deb packages with setuptools
  "python3-venv",
  "python3-opencv",
  
  "mesa-utils",

  "build-essential", "libc6-dev", "yasm", "cmake", "pkg-config", "swig", "libglew-dev", "mesa-common-dev", "libstdc++-5-dev", "python3-dev", "python3-numpy", "libasound2-dev",  

  # binary editors
  "okteta",
  
  "gpa", # keys, etc. in directory: ~/.gnupg
  "kgpg", # kde client
  
  "arandr",
  "silversearcher-ag",
  "apt-transport-https", "ca-certificates", "software-properties-common", # apt over http (required for example by docker)
  
  "doxygen"
  ]

print("\nINSTALLING SYSTEM PACKAGES\n")
st="sudo apt-get install "
for pk in pklis:
  st=st+pk+" "

print(st); os.system(st)

print("\nINSTALLING VALKKA LIVE\n")
st="pip3 install --user --upgrade git+git://github.com/elsampsa/valkka-live.git"
print(st); os.system(st)

st="install-valkka-core"
print(st); os.system(st)

st="valkka-tune"
print(st); os.system(st)

print("\nFETCHING VALKKA EXAMPLES\n")
st="git clone https://github.com/elsampsa/valkka-examples"
print(st); os.system(st)

print("\nFETCHING DARKNET_PY\n")
st="git clone https://github.com/elsampsa/darknet-python"
print(st); os.system(st)

st="firefox https://github.com/elsampsa/darknet-python &"
print(st); os.system(st)

st="firefox https://elsampsa.github.io/valkka-live/_build/html/index.html &"
print(st); os.system(st)
