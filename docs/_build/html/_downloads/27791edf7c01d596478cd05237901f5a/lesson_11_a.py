#<hide>
"""
filtergraph:

(LiveThread:livethread) -->> (ValkkaFSWriterThread:writerthread)
"""
#</hide>

"""<rtf>
Import valkka level 1 API, and ValkkaFS from level 2 API
<rtf>"""
import time
from valkka.core import *
from valkka.api2 import ValkkaFS

"""<rtf>
ValkkaFS instance handles the metadata of the filesystem.  Let's create a new filesystem and save the metadata into directory */home/sampsa/tmp/testvalkkafs*
<rtf>"""
valkkafs = ValkkaFS.newFromDirectory(
    dirname = "/home/sampsa/tmp/testvalkkafs", 
    blocksize = 512*512,
    n_blocks = 10,
    verbose = True)

"""<rtf>
One block holds 512 KBytes of data.  For a camera streaming 2048KBits per second, that'll be 2 seconds worth of frames.

The total size of the device file where frames are streamed, will be (512kB * 10) 5120 kB.

You could also skip the parameter *n_blocks* and instead define the device file size directly with *device_size = 5120*1024*.

For calculating device file sizes, see :ref:`ValkkaFS section <valkkafs>`

Now the directory has the following files:

::

    blockfile           Table of block timestamps.  Used for seeking, etc.
    dumpfile            Frames are streamed into this file (the "device file")
    valkkafs.json       Metadata: block size, current block, etc.
    
    
If you want to use an entire partition for saving the video streams, you would be using:

::

    valkkafs = ValkkaFS.newFromDirectory(
        dirname="/home/sampsa/tmp/testvalkkafs", 
        partition_uuid="626c5523-2979-fd4d-a169-43d818fb0ffe", 
        blocksize=300*1024, 
        device_size=1024*1024*1024*100) # 100 GB

That uses 100 GB from a partition identified with its uuid.

For details on handling partitions and disks, see :ref:`ValkkaFS section <valkkafs>`

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
ctx = LiveConnectionContext(LiveConnectionType_rtsp, "rtsp://admin:12345@192.168.0.157", 1, file_input_framefilter)

"""<rtf>
Any additional cameras would use the same framefilter:

::

    ctx = LiveConnectionContext(LiveConnectionType_rtsp, "rtsp://admin:nordic12345@192.168.1.41", 1, file_input_framefilter)

Next, start threads
<rtf>"""
writerthread.startCall()
livethread.startCall()

"""<rtf>
Frames with slot number 1 are identified in the filesystem with id number 925412:
<rtf>"""
writerthread.setSlotIdCall(1, 925412)

livethread.registerStreamCall(ctx)
livethread.playStreamCall(ctx)

"""<rtf>
Idle for 10 secs while the threads run in the background
<rtf>"""
time.sleep(10)

"""<rtf>
At this moment, let's take a look at the blocktable
<rtf>"""
a = valkkafs.getBlockTable()
print(a[:,0:10])

"""<rtf>
Let the threads do their stuff for 10 secs more
<rtf>"""
time.sleep(10)

livethread.stopCall()
writerthread.stopCall()

"""<rtf>
Let's take a look at the blocktable again:
<rtf>"""
a = valkkafs.getBlockTable()
print(a[:,0:10])

print("bye")
