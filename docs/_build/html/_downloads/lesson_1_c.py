import time
from valkka.valkka_core import *
"""  
                                                                    branch 1
                                                                   +------------> {GateFrameFilter: gate_filter}
main branch                                                        |                 | 
(LiveThread:livethread) --> {ForkFrameFilter:live_out_filter}  --> |                 +--- {InfoFrameFilter: info_filter}
                                                                   |
                                                                   +-------------> {FileFrameFilter: file_filter}
                                                                   branch 2         
                                                                                                                                                                          
"""

# branch 1
info_filter     =InfoFrameFilter("info_filter")
gate_filter     =GateFrameFilter("gate_filter",info_filter)

# branch 2
file_filter     =FileFrameFilter("file_filter")

# main branch
live_out_filter =ForkFrameFilter("live_out_filter",gate_filter,file_filter)
livethread      =LiveThread("livethread")

# define the connection
ctx =LiveConnectionContext(LiveConnectionType_rtsp, "rtsp://admin:nordic12345@192.168.1.41", 1, live_out_filter)

# close the gate before streaming
gate_filter.unSet()

livethread.startCall()
livethread.registerStreamCall(ctx)
livethread.playStreamCall(ctx)
time.sleep(5)

print("start writing to disk")
file_filter.activate("stream.mkv")
time.sleep(5)

print("let's get verbose")
gate_filter.set()
time.sleep(2)

print("close file and exit")
file_filter.deActivate()

livethread.stopCall()

print("bye")