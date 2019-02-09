import time
from valkka.core import *
from valkka.api2 import ValkkaFS, ValkkaFSManager, setValkkaLogLevel, loglevel_debug

setValkkaLogLevel(loglevel_debug)

def cb(mstime):
    print("mstime callback", mstime)
        
valkkafs = ValkkaFS.loadFromDirectory(dirname="/home/sampsa/tmp/testvalkkafs")
# manager = ValkkaFSManager(valkkafs, cb)
manager = ValkkaFSManager(valkkafs)

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
out_filter = BriefInfoFrameFilter("out_filter")
manager.setOutput(925412, 1, out_filter)

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

