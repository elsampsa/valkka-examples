import time
from valkka.core import *
from valkka.api2 import ValkkaFS, ValkkaFSManager, setValkkaLogLevel, loglevel_debug

setValkkaLogLevel(loglevel_debug)

def cb(mstime):
    print("mstime callback", mstime)
        
valkkafs = ValkkaFS.loadFromDirectory(dirname="/home/sampsa/tmp/testvalkkafs")
manager = ValkkaFSManager(valkkafs, cb)

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
out_filter = InfoFrameFilter("out_filter")
manager.setOutput(925412, 1, out_filter)

target_mstimestamp = 1547796216646
manager.seek(target_mstimestamp)

time.sleep(5)

"""
# TODO
manager.play()
time.sleep(10)
manager.stop()
"""
# TODO: first stage: just dump frames to terminal
# second stage: plug this into OpenManagedFilterChain
# TODO: call time callback from cpp .. each second if time is available ..? or always (with 0 if no time)


