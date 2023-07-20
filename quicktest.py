from subprocess import Popen, PIPE

print()
print("Loading Valkka")

valkka_ok = False

try:
    import valkka
    from valkka import core
except Exception as e:
    print("Loading Valkka failed with", e)
else:
    valkka_ok = True
    print("Valkka loaded ok")
    print("   Version          ",valkka.core.__version__)
    print("   Core loaded from ",core.__file__)
    """Test instantiation of some objects
    """
    print()
    print("   Testing Valkka classes")
    live =core.LiveThread("live")
    # inp  =core.FrameFifo("fifo") # in the API no more
    # ff   =core.FifoFrameFilter("fifo",inp)
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
    VERSION_MAJOR=1
    VERSION_MINOR=4
    VERSION_PATCH=0

    print("Checking Valkka python examples")
    print("   version:",str(VERSION_MAJOR)+"."+str(VERSION_MINOR)+"."+str(VERSION_PATCH))

    if (VERSION_MAJOR!=core.VERSION_MAJOR or VERSION_MINOR!=core.VERSION_MINOR or VERSION_PATCH!=core.VERSION_PATCH):
        print("   ** WARNING **")
        print("   INCONSISTENT VALKKA-CORE AND VALKKA_EXAMPLES VERSIONS")
        print("   You probably need to update your valkka-core module (say, 'sudo apt-get update' and 'sudo apt-get upgrade valkka')")
        print("   .. or update valkka-examples by running 'git pull' in this directory")
        print()

print()
print("Loading numerical python")
try:
    import numpy
except Exception as e:
    print("loading numpy failed with", e)
else:
    print("Numpy loaded ok")
    print("   Numpy loaded from          : ",numpy.__file__)
    print("   Numpy version              : ",numpy.__version__)
    if valkka_ok:
        print("   libValkka was compiled       ")
        print("   with numpy version         : ",core.get_numpy_version())

        if (numpy.__version__ != core.get_numpy_version()):
            print()
            print("** ATTENTION ** ")
            print("    You are using a different numpy version than was used when libvalkka was compiled")
            print("    Normally this should pose no problem")
            print("    However,if you installed libValkka with apt-get, you'll have a consistent")
            print("    numpy installed in:")
            print("    /usr/lib/python3/dist-packages/")
            print("    you might want to use that version instead")
            print("    You can use the make_venv.bash script for creating a virtual environment")
            
        if not core.numpy_version_ok():
            print()
            print("** WARNING ** ")
            print("    INCOMPATIBLE NUMPY VERSIONS DETECTED")
            print("    YOU SHOULD INSTALL A COMPATIBLE VERSION OF NUMPY")
            print("    OR SUFFER THE CONSEQUENCES (SEGFAULTS)")
            print()

print()
print("Loading OpenCV")
try:
    import cv2
except Exception as e:
    print("loading opencv failed with", e)
else:
    print("OpenCV loaded ok")
    print("   Version      ",cv2.__version__)
    print("   Loaded from  ",cv2.__file__)

print()
print("Loading PySide2")
try:
    import PySide2
except Exception as e:
    print("loading pyside2 failed with", e)
else:
    print("   Version      ",PySide2.__version__)
    print("   Loaded from  ",PySide2.__file__)

print()
print("Checking Shapely")
try:
    import shapely
except Exception as e:
    print("    shapely not installed")
else:
    if shapely.__version__ != '1.6.0':
        print("    your shapely version is not 1.6.0")
        print("    with newer shapely versions, prepare for segfaults")
    else:
        print("   shapely ok")

print()
print("Loading setproctitle")
try:
    import setproctitle
except Exception as e:
    print("    setproctitle not installed")
else:
    print("    setproctitle ok")

print()
print("Checking for VAAPI hardware acceleration")

p=Popen("vainfo", stdout=PIPE, stderr=PIPE)
out, err = p.communicate()
if p.returncode != 0:
    print("    WARNING: command vainfo failed!  check that you have installed VAAPI drivers correctly")
if "H264" not in out.decode("utf-8"):
    print("    WARNING: your VAAPI drivers seems to be missing H264 decoding capabilities.  Please run vainfo.")

try:
    from valkka.core import VAAPIThread
except Exception as e:
    print("    could not import VAAPIThread from valkka.core")
else:
    print("    VAAPI acceleration available: you can use valkka.core.VAAPIThread instead of valkka.core.AVThread")

print()
print("Checking for NVIDIA/CUDA hardware acceleration")
try:
    from valkka.nv import NVThread
except Exception as e:
    print("    could not import NVThread from valkka.nv namespace : please install from https://github.com/xiaxoxin2/valkka-nv")
else:
    print("    CUDA acceleration available: you can use valkka.nv.NVThread instead of AVThread")
print()
