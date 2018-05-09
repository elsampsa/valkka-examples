#<hide>
"""
filtergraph:

Streaming part                                                                           
(LiveThread:livethread)---+
                          |
Decoding part             |
(AVThread:avthread) <<----+    
 |
 |       Presentation part
 +--->> (OpenGLThread:glthread)
"""
#</hide>
#<hide>
import time
from valkka.valkka_core import *

# presentation part
glthread        =OpenGLThread ("glthread")
gl_in_filter    =glthread.getFrameFilter()

# decoding part
avthread        =AVThread("avthread",gl_in_filter)
av_in_filter    =avthread.getFrameFilter()

# streaming part
livethread      =LiveThread("livethread")

# define connection to camera
ctx =LiveConnectionContext(LiveConnectionType_rtsp, "rtsp://admin:nordic12345@192.168.1.41", 1, av_in_filter)

# start threads
glthread.startCall()
avthread.startCall()
livethread.startCall()

# start decoding
avthread.decodingOnCall()

livethread.registerStreamCall(ctx)
livethread.playStreamCall(ctx)
#</hide>

"""<rtf>
Streaming the same camera to several X windows is trivial; we just need to add more render groups (aka x windows) and render contexes (mappings):
<rtf>"""
id_list=[]

for i in range(10):
  window_id =glthread.createWindow()
  glthread.newRenderGroupCall(window_id)
  context_id=glthread.newRenderContextCall(1,window_id,0)
  id_list.append((context_id,window_id)) # save context and window ids

time.sleep(10)

for ids in id_list:
  glthread.delRenderContextCall(ids[0])
  glthread.delRenderGroupCall(ids[1])

#<hide>
# stop decoding
avthread.decodingOffCall()

# stop threads
livethread.stopCall()
avthread.stopCall()
glthread.stopCall()

print("bye")
#</hide>



