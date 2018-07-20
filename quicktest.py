print()
print("Loading numerical python")
import numpy
print("Numpy loaded ok")
print("   Numpy loaded from",numpy.__file__)
print("   Numpy version    ",numpy.__version__)

print()
print("Loading Valkka")
import valkka
from valkka.valkka_core import *

print("Valkka loaded ok")
print("   Version          ",valkka.__version__)
print("   Loaded from      ",valkka.__file__)
print("   Core loaded from ",valkka.valkka_core.__file__)
"""Test instantiation of some objects
"""
print("   Testing Valkka classes")
live =LiveThread("live")
inp  =FrameFifo("fifo")
ff   =FifoFrameFilter("fifo",inp)
out  =DummyFrameFilter("dummy")
av   =AVThread("av",out)
gl   =OpenGLThread("gl")

av_in =av.getFrameFilter();
gl_in =gl.getFrameFilter();

ctx=LiveConnectionContext()
ctx.slot=1
ctx.connection_type=LiveConnectionType_rtsp
ctx.address="rtsp://admin:12345@192.168.0.157"
ctx2=LiveConnectionContext(LiveConnectionType_rtsp, "rtsp://admin:12345@192.168.0.157", 1, out)

print("   Valkka classes ok")
print()

print("Loading OpenCV")
import cv2
  
print("OpenCV loaded ok")
print("   Version      ",cv2.__version__)
print("   Loaded from  ",cv2.__file__)
print()
