import time
from valkka import core
from valkka.api2 import ValkkaFS, ValkkaFSManager, setValkkaLogLevel, loglevel_debug, OpenGLThread
from valkka.api2.chains import manager3

"""
TODO: FileCacheThread should send initialization frame
- FileCacheThread .. per slot, two substream SetupFrame(s) .. or what?
- Video jerks a bit .. is this because the play edge is too close to the block edge and it runs empty before new frames arrive?
"""



setValkkaLogLevel(loglevel_debug)

def cb(mstime):
    print("mstime callback", mstime)

# create OpenGLThread (for drawing video) and AVThread (for decoding)
glthread = OpenGLThread(name="gl_thread")
ctx = core.FrameFifoContext()
avthread = core.AVThread(
    "avthread",
    glthread.getInput(),
    ctx)
av_in_filter = avthread.getFrameFilter()

avthread.startCall()
avthread.decodingOnCall()

# create an X-window
window_id = glthread.createWindow()

# map frames with slot 1 to that window
glthread.newRenderGroup(window_id)
context_id = glthread.newRenderContext(1, window_id, 0)

valkkafs = ValkkaFS.loadFromDirectory(dirname="/home/sampsa/tmp/testvalkkafs")
# manager = ValkkaFSManager(valkkafs, cb)
manager = ValkkaFSManager(valkkafs)

# manager.timeCallback__(1547796192621)
# paska

a = valkkafs.getBlockTable()
# print(a[:,0:10])
i=0
for row in a:
    print("%2i : %s" % (i, str(row)))
    i += 1

(t0, t1) = valkkafs.getTimeRange()
print("Min and Max time in milliseconds:", t0, t1)
print("Min time:", time.gmtime(t0/1000))
print("Max time:", time.gmtime(t1/1000))

# output from id 925412 mapped to slot 1 and diverted to out_filter
# out_filter = InfoFrameFilter("out_filter")
# out_filter = BriefInfoFrameFilter("out_filter")
# manager.setOutput(925412, 1, out_filter)
manager.setOutput(925412, 1, av_in_filter)

print("\nwait\n")
time.sleep(1)

print("\nplay without seek\n")
res = manager.play()
print("res=", res)

print("\nseek and wait\n")
# target_mstimestamp = 1547796216646
# target_mstimestamp = int(t0+1000) # from numpy.64 to int
target_mstimestamp = t0

print("target_mstimestamp", target_mstimestamp)
manager.seek(target_mstimestamp)
time.sleep(5)

print("\nplay\n")
res = manager.play()
print("res=",res)
time.sleep(30)

print("\nstop\n")
res = manager.stop()
time.sleep(5)

