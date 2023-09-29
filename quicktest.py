from subprocess import Popen, PIPE
import os, sys

print()
print("Loading Valkka")

valkka_ok = False

try:
    import valkka
    from valkka import core
except Exception as e:
    print("FATAL: Loading Valkka failed with", e)
    print("       Have you installed libValkka at all?")
    print()
    sys.exit(2)
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
    out_filter  =core.DummyFrameFilter("dummy")
    av   =core.AVThread("av",out_filter)
    gl   =core.OpenGLThread("gl")

    av_in =av.getFrameFilter();
    gl_in =gl.getFrameFilter();

    ctx=core.LiveConnectionContext()
    ctx.slot=1
    ctx.connection_type=core.LiveConnectionType_rtsp
    ctx.address="rtsp://admin:12345@192.168.0.157"
    ctx2=core.LiveConnectionContext(core.LiveConnectionType_rtsp, "rtsp://admin:12345@192.168.0.157", 1, out_filter)
    print("   Valkka classes ok")
    print()

    # this is modified automatically by setver.bash - don't touch!
    VERSION_MAJOR=1
    VERSION_MINOR=6
    VERSION_PATCH=1

    print("Checking Valkka python examples")
    print("   version:",str(VERSION_MAJOR)+"."+str(VERSION_MINOR)+"."+str(VERSION_PATCH))

    if (VERSION_MAJOR!=core.VERSION_MAJOR or VERSION_MINOR!=core.VERSION_MINOR or VERSION_PATCH!=core.VERSION_PATCH):
        print("   ** WARNING **")
        print("   INCONSISTENT VALKKA-CORE AND VALKKA_EXAMPLES VERSIONS")
        print("   You probably need to update your valkka-core module (say, 'sudo apt-get update' and 'sudo apt-get upgrade valkka')")
        print("   .. or update valkka-examples by running 'git pull' in this directory")
        print()

print()
print("Checking valkka.onvif and valkka.discovery")
try:
    from valkka.onvif import base as base_onvif
    from valkka.discovery import base as base_discovery
except Exception as e:
    print("WARNING: loading valkka.onvif and valkka.discovery failed with", e)
    print("have you installed valkka-onvif?")
else:
    print("onvif & discovery loaded ok")
    print("   onvif loaded from          : ",base_onvif.__file__)
    print("   discovery loaded from      : ",base_discovery.__file__)

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
    if "/usr/lib/" not in cv2.__file__:
        print("   WARNING       your opencv is not installed into the standard /usr/lib/ location")
        print("                 consider using these commands:")
        print("                 pip3 uninstall opencv-python")
        print("                 sudo pip3 uninstall opencv-python")
        print("                 sudo apt-get install python3-opencv")

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
else:
    if "H264" not in out.decode("utf-8"):
        print("    WARNING: your VAAPI drivers seems to be missing H264 decoding capabilities.  Please run vainfo.")
    if "Intel iHD driver" in out.decode("utf-8"):
        print("    FATAL: libValkka tries to enforce the i965 for VAAPI, but you seem to use intel iHD")
        print("           --> prepare for memleaks!")

try:
    from valkka.core import VAAPIThread
    avthread=VAAPIThread("decoder", out_filter)
except Exception as e:
    print("    could not import VAAPIThread from valkka.core")
    print(e)
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

print("Taking a look at your X11 DISPLAY variable")
if "DISPLAY" not in os.environ:
    print("    No DISPLAY env variable found - please check your X11 config")
else:
    if os.environ["DISPLAY"] not in [":0.0", ":.0", ":0"]:
        print(f"    Weird X11 DISPLAY env variable {os.environ['DISPLAY']}")
        print("    WARNING: Some valkka example / test programs assume :0.0 (aka :0 or :.0)")
    else:
        print("    All good")
print()


print("Taking a look at current user's groups")
if "USER" not in os.environ:
    print("    WARNING: $USER doesn't exist")
else:
    p=Popen(f"groups {os.environ['USER']}".split(), stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        print("    WARNING: command groups failed - something is VERY WRONG in your system")
        print()
    else:
        try:
            res = out.decode("utf-8")
            user, groups = res.split(":")
        except Exception as e:
            print("    WARNING: can't resolve command 'groups' output, please try manually 'groups $USER'")
            print()
        else:
            # print(groups)
            if "video" not in groups:
                print(f"    WARNING: user not in the 'video' group: VAAPI hw acceleration will not work - please run:")
                print(f"             sudo usermod -a -G video {os.environ['USER']}")
                print(f"             after that you still need to logout & login")
            if "render" not in groups:
                print(f"    WARNING: user not in the 'render' group - consider running:")
                print(f"             sudo usermod -a -G render {os.environ['USER']}")
                print(f"             after that you still need to logout & login")
            if "docker" not in groups:
                print(f"    WARNING: user not in the 'docker' group - if you want to use docker, do:")
                print(f"             sudo usermod -a -G docker {os.environ['USER']}")
                print(f"             after that you still need to logout & login")
            print()


