#<hide>
"""
filtergraph:

(LiveThread:livethread) -->> (ValkkaFSWriterThread:writerthread)
"""
#</hide>

"""<rtf>

This will be our filtergraph:

::

    (LiveThread:livethread) -->> (ValkkaFSWriterThread:writerthread)

Let's import valkka level 1 API, and ValkkaSingleFS from level 2 API:
<rtf>"""
import time
from valkka.core import *
from valkka.fs import ValkkaSingleFS
from valkka.api2 import loglevel_debug, loglevel_normal, loglevel_crazy

"""<rtf>
Let's set our IP camera's address:
<rtf>"""
rtsp_address="rtsp://admin:12345@192.168.0.157"

"""<rtf>
If you want to see the filesystem writing each frame, enable
these debugging loggers:
<rtf>"""
#setLogLevel_filelogger(loglevel_crazy)
#setLogLevel_valkkafslogger(loglevel_crazy)

"""<rtf>
There are two flavors of ValkkaFS under the valkka.fs namespace, namely
``ValkkaSingleFS`` and ``ValkkaMultiFS``.  In the former, there is one file
per one camera/stream, while in the latter you can dump several streams into the same
file.

The ValkkaSingleFS instance handles the metadata of the filesystem.  
Let's create a new filesystem and save the metadata into directory */tmp/testvalkkafs*
<rtf>"""
valkkafs = ValkkaSingleFS.newFromDirectory(
    dirname = "/tmp/testvalkkafs", 
    blocksize = (2048//8)*1024, # note division by 8: 2048 KiloBITS
    n_blocks = 10,
    verbose = True)

"""<rtf>
Here one block holds 2048 KBits (256 KBytes) of data.  
Let suppose that your camera streams 1024KBits 
per second (kbps): now a block will be finished every 2 seconds.

If you now set your IP camera to key-frame every one second, 
you will have two key frames per each block, 
which is a necessary condition for efficient seeking using the filesystem.

The total size of the device file where frames are streamed, will be (256kB * 10) 2560 kB.

You could also skip the parameter *n_blocks* and instead define the device file size directly 
with *device_size = 2560*1024*.

Now the directory has the following files:

::

    blockfile           Table of block timestamps.  Used for seeking, etc.
    dumpfile            Frames are streamed into this file (the "device file")
    valkkafs.json       Metadata: block size, current block, etc.
    
Next, we create and start (1) the thread responsible for writing the frames into ValkkaFS and (2) LiveThread that is reading the cameras:
<rtf>"""
writerthread = ValkkaFSWriterThread("writer", valkkafs.core)
livethread = LiveThread("livethread")

"""<rtf>
All cameras write to the same FrameFilter, handled by the writing thread:
<rtf>"""
file_input_framefilter = writerthread.getFrameFilter()

"""<rtf>
Read camera and designate it with slot number 1
<rtf>"""
ctx = LiveConnectionContext(LiveConnectionType_rtsp, rtsp_address, 1, file_input_framefilter)

"""<rtf>
Next, start threads
<rtf>"""
writerthread.startCall()
livethread.startCall()

"""<rtf>
Frames with slot number 1 are identified in the filesystem with id number 925412 (which we just invented):
<rtf>"""
writerthread.setSlotIdCall(1, 925412)

livethread.registerStreamCall(ctx)
livethread.playStreamCall(ctx)

"""<rtf>
Idle for some secs while the threads run in the background
<rtf>"""
print("recording!")
time.sleep(3)

"""<rtf>
At this moment, let's take a look at the blocktable
<rtf>"""
a=valkkafs.getBlockTable()
print(a)
if a.max() <= 0:
    print("Not a single block finished so far..")
    valkkafs.core.updateTable(disk_write=True)
    print("Check blocktable again")
    a=valkkafs.getBlockTable()
    if a.max() <= 0:
        print("Not a single frame so far..")
    print(a)

"""<rtf>
Frames in a certain block are saved definitely into the book-keeping only once a block is finished.

In the code above, we force a block write even if the block has not filled up.

Let's continue & let the threads do their stuff for some more time
<rtf>"""
print("recording some more")
time.sleep(30)

livethread.stopCall()
writerthread.stopCall()

"""<rtf>
Let's take a look at the blocktable again:
<rtf>"""
print(a)

print("bye")
