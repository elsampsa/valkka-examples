import time
from valkka.core import *
from valkka.api2 import ValkkaFS

rtsp = "rtsp://admin:12345@192.168.0.157"
rtime = 30

valkkafs = ValkkaFS.newFromDirectory(
    dirname = "/home/sampsa/tmp/testvalkkafs", 
    blocksize = 512*512,
    n_blocks = 25,
    verbose = True)

writerthread = ValkkaFSWriterThread("writer", valkkafs.core)
livethread = LiveThread("livethread")

file_input_framefilter = writerthread.getFrameFilter()
ctx = LiveConnectionContext(LiveConnectionType_rtsp, rtsp, 1, file_input_framefilter)

writerthread.startCall()
livethread.startCall()

writerthread.setSlotIdCall(1, 925412)

livethread.registerStreamCall(ctx)
livethread.playStreamCall(ctx)

time.sleep(rtime)

livethread.stopCall()
writerthread.stopCall()

a = valkkafs.getBlockTable()
print(a[:,0:10])

print("bye")
