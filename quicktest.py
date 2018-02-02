print()
print("Loading Valkka")
import valkka
from valkka.valkka_core import *
  
print("Valkka loaded ok")
print("   Version      ",valkka.__version__)
print("   Loaded from  ",valkka.__file__)
"""Test instantiation of some objects
"""
print("   Testing Valkka classes")
live =LiveThread("live")
inp  =FrameFifo("fifo",10)
ff   =FifoFrameFilter("fifo",inp)
out  =DummyFrameFilter("dummy")
av   =AVThread("av",inp,out)
gl   =OpenGLThread("gl")
ctx  =LiveConnectionContext()
print("   Valkka classes ok")
print()

print("Loading OpenCV")
import cv2
  
print("OpenCV loaded ok")
print("   Version      ",cv2.__version__)
print("   Loaded from  ",cv2.__file__)
print()
