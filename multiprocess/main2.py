"""Send decoded frames from N rtsp cameras to N python multiprocesses

If this program crashes, remember to do "killall -9 python3" and to clear /dev/shm/*valkka*

Run with "python3 main2.py"
"""
import logging, time
from valkka.core import *
from rgb import RGB24Process # from local file
from singleton import event_fd_group_1 # from local file

class MyProcess(RGB24Process):
    # in this example, there is one multiprocess per one camera
    
    def preRun__(self):
        super().preRun__()
        ## import libraries that use multithreading
        ## create instances from those libraries
        # self.redis_instance = etc

    def handleFrame__(self, frame, meta):
        ## please test first just with printing this debug message:
        self.logger.debug("handleFrame__ : rgb client got frame %s from slot %s", frame.shape, meta.slot)
        """metadata has the following members:
        size 
        width
        height
        slot
        mstimestamp
        """
        ## NOTES:
        ## - slot number identifies uniquely the camera
        ## - if you do any complex/heavy stuff here, you should measure how much time
        ##   it takes -> what is the max. framerate you may achieve
        
    def postRun__(self):
        super().postRun__()
        ## enforce garbace collection:
        # self.redis_instance = None


class LiveStream:
    def __init__(self, shmem_buffers, shmem_name, address, slot, width, height):
        self.shmem_buffers = shmem_buffers
        self.shmem_name = shmem_name
        self.address = address
        self.slot = slot 
        self.width = width
        self.height = height

        # reserve a unix event fd file descriptor for synchronization
        _, self.event = event_fd_group_1.reserve()
		# RBGShmem Filter
        self.shmem_filter = RGBShmemFrameFilter(self.shmem_name, self.shmem_buffers, self.width, self.height)
		# self.shmem_filter = BriefInfoFrameFilter(self.shmem_name)  # For Debugging
        self.shmem_filter.useFd(self.event)
        
        # SWS Filter
        self.sws_filter = SwScaleFrameFilter(f"sws_{self.shmem_name}", self.width, self.height, self.shmem_filter)
		# self.interval_filter = TimeIntervalFrameFilter("interval_filter", 0, self.sws_filter)

		# decoding part
        self.avthread = AVThread("avthread", self.sws_filter)
        self.av_in_filter = self.avthread.getFrameFilter()

		# define connection to camera
        self.ctx = LiveConnectionContext(LiveConnectionType_rtsp, self.address, self.slot, self.av_in_filter)

        self.avthread.startCall()
        self.avthread.decodingOnCall()

    def close(self):
        self.avthread.decodingOffCall()
        self.avthread.stopCall()

    def close(self):
        self.avthread.decodingOffCall()
        self.avthread.stopCall()
        self.event.release() # release the unix event file descriptor
        
# had here gradually more cameras - please - and report when the thing goes belly up
cams = {
    1: "rtsp://admin:123456@10.0.0.25:554/stream1",
    2: "rtsp://admin:123456@10.0.0.3"
}

# create a python multiprocess per each camera
MyProcess.formatLogger(logging.DEBUG)
processes = {}
for i, cam in cams.items():
    p = MyProcess()
    p.ignoreSIGINT()
    p.start()
    processes[i] = p
    
# create & start threads after processes    
livethread = LiveThread("live")

livestreams = {}
for i, cam in cams.items():
    print(">", i, cam)
    livestreams[i] = LiveStream( # NOTE: CREATES THE SHMEM SERVER
        shmem_buffers=10,
        shmem_name=f"my-cam-project-{i}", # would be better to use uuid, but..
        address=cam,
        slot=i,
        width=300,
        height=300
    )

# Start livethread
livethread.startCall()

# Register context to livethread
for i, livestream in livestreams.items():
    p = processes[i]
    livethread.registerStreamCall(livestream.ctx)
    livethread.playStreamCall(livestream.ctx)
    # THIS CALL CREATES THE SHMEM CLIENT:
    p.activateRGB24Client(
            # client side parameters must match server side:
            name = livestream.shmem_name,
            n_ringbuffer = livestream.shmem_buffers,
            width = livestream.width,
            height = livestream.height,
            # unix event fd sync primitive must match at SERVER and CLIENT sides: 
            ipc_index = event_fd_group_1.asIndex(livestream.event)
        )

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        print("SIGTERM or CTRL-C: will exit asap")
        break
        
livethread.stopCall()

for i, p in processes.items():
    p.stop()
