print()
print("Loading numerical python")
import numpy
print("Numpy loaded ok")
print("   Numpy loaded from",numpy.__file__)
print("   Numpy version    ",numpy.__version__)

print()
print("Loading Valkka")
import valkka
from valkka import core

print("Valkka loaded ok")
print("   Version          ",valkka.core.__version__)
print("   Core loaded from ",core.__file__)
"""Test instantiation of some objects
"""
print()
print("   Testing Valkka classes")
live =core.LiveThread("live")
inp  =core.FrameFifo("fifo")
ff   =core.FifoFrameFilter("fifo",inp)
out  =core.DummyFrameFilter("dummy")
av   =core.AVThread("av",out)
gl   =core.OpenGLThread("gl")

av_in =av.getFrameFilter();
gl_in =gl.getFrameFilter();

ctx=core.LiveConnectionContext()
ctx.slot=1
ctx.connection_type=core.LiveConnectionType_rtsp
ctx.address="rtsp://admin:12345@192.168.0.157"
ctx2=core.LiveConnectionContext(core.LiveConnectionType_rtsp, "rtsp://admin:12345@192.168.0.157", 1, out)
print("   Valkka classes ok")
print()

# this is modified automatically by setver.bash - don't touch!
VERSION_MAJOR=0
VERSION_MINOR=7
VERSION_PATCH=0

print("Checking Valkka python examples")
print("   version:",str(VERSION_MAJOR)+"."+str(VERSION_MINOR)+"."+str(VERSION_PATCH))

if (VERSION_MAJOR!=core.VERSION_MAJOR or VERSION_MINOR!=core.VERSION_MINOR or VERSION_PATCH!=core.VERSION_PATCH):
  print("   ** WARNING **")
  print("   INCONSISTENT VALKKA-CORE AND VALKKA_EXAMPLES VERSIONS")
  print("   You probably need to update your valkka-core module (say, 'sudo apt-get update' and 'sudo apt-get upgrade valkka')")
  print("   .. or update valkka-examples by running 'git pull' in this directory")
print()

print("Loading OpenCV")
import cv2
  
print("OpenCV loaded ok")
print("   Version      ",cv2.__version__)
print("   Loaded from  ",cv2.__file__)
print()
