"""<rtf>
First, import API level 2:
<rtf>"""
import time
from valkka.api2 import LiveThread, OpenGLThread
from valkka.api2 import BasicFilterchain

"""<rtf>
Instantiating the API level 2 LiveThread starts running the underlying cpp thread:
<rtf>"""
livethread=LiveThread( # starts live stream services (using live555)
  name   ="live_thread",
  verbose=False,
  affinity=-1
)

"""<rtf>
Same goes for OpenGLThread:
<rtf>"""
openglthread=OpenGLThread(
  name    ="glthread",
  n_720p   =20,   # reserve stacks of YUV video frames for various resolutions
  n_1080p  =20,
  n_1440p  =0,
  n_4K     =0,
  verbose =False,
  msbuftime=100,
  affinity=-1
)


"""<rtf>
The filterchain and decoder (AVThread) are encapsulated into a single class.  Instantiating starts the AVThread (decoding is off by default):
<rtf>"""
chain=BasicFilterchain( # decoding and branching the stream happens here
  livethread  =livethread, 
  openglthread=openglthread,
  address     ="rtsp://admin:nordic12345@192.168.1.41",
  slot        =1,
  affinity    =-1,
  verbose     =False,
  msreconnect =10000 # if no frames in ten seconds, try to reconnect
)

"""<rtf>
BasicFilterchain takes as an argument the LiveThread and OpenGLThread instances.  It creates the relevant connections between the threads.

Next, create an x-window, map stream to the screen, and start decoding:
<rtf>"""
# create a window
win_id =openglthread.createWindow()

# create a stream-to-window mapping
token  =openglthread.connect(slot=1,window_id=win_id) # present frames with slot number 1 at window win_id

# start decoding
chain.decodingOn()
# stream for 20 secs
time.sleep(20)

"""<rtf>
Finally, stop decoding and exit.  Threads are automatically stopped at garbage collection.
<rtf>"""
chain.decodingOff()
print("bye")
