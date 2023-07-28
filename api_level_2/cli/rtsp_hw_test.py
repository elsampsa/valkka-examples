"""Pulls frame from a single rtsp camera, multiplies the stream N times and passes it to N VAAPI hw decoders.  

Reports final FPS in each replicated stream.

Yaml configuration through "vaapi_streams.yaml"
"""

import os, yaml, time
from valkka.core import *
"""We can express a filterchain as a hierarchical list as well!  (no need for ascii art):

::

    MAIN BRANCH
        SOURCE
            {ForkFrameFilterN: fork1}
                DECODE-BRANCH 1
                DECODE-BRANCH 2

    DECODE-BRANCH
        (VAAPIThread:avthread) 
            {ForkFrameFilterN: fork2}
                    {SwSScaleFrameFilter: sws_filter (optional)}
                        {FPSCountFrameFilter: count_filter}
"""
class DecodeBranch:

    def __init__(self, n, verbose = False, sws = None, n_threads = None, affinity = None, interval=1000):
        self.verbose = verbose
        self.sws = sws
        self.interval = interval
        name = f"branch {n}"
        if self.verbose:
            # just in order to see what it is exactly we get from the end
            # of the pipeline..!
            self.info = BriefInfoFrameFilter("info-"+str(n))
            self.counter = FPSCountFrameFilter(name, self.interval, self.info)
        else:
            self.counter = FPSCountFrameFilter(name, self.interval)

        next_ff = self.counter # chain this further or passs to ForkFrameFilterN

        if self.sws:
            # Create the SwScaleFrameFilter (optional)
            width, height = self.sws
            self.sws_opt = SwScaleFrameFilter("sws-"+str(self.slot), 
                width, height, next_ff)
            next_ff = self.sws_opt
            print("branch", n,"interpolating to", width, height)
        
        ms_pass = None
        if ms_pass:
            print("WARNING: will pass frames only each", ms_pass, "milliseconds after decoding to YUV")
            self.time_filter=TimeIntervalFrameFilter("interval-"+str(n), ms_pass, next_ff)
            next_ff = self.time_filter
        
        # Bitmap fork
        self.fork2 = ForkFrameFilterN("fork2")
        self.fork2.connect("bitmap-"+str(n), next_ff)

        self.avthread = VAAPIThread(
            "avthread-" + str(n),
            self.fork2) # feeds the bitmap fork & decoding branch
            # self.framefifo_ctx)

        if n_threads:
            print("setting", n_threads,"threads per libav decoder")
            self.avthread.setNumberOfThreads(n_threads)

        if affinity is not None:
            print("binding stream replicate", n, "to core", affinity)
            self.avthread.setAffinity(affinity)

    def getInputFilter(self):
        return self.avthread.getFrameFilter()

    def __call__(self):
        # start decoding thread
        self.avthread.startCall()
        # start decoding
        self.avthread.decodingOnCall()

    def requestStop(self):
        self.avthread.requestStopCall()

    def waitStop(self):
        self.avthread.waitStopCall()



class MainBranch:

    def __init__(self, slot, livethread, address):
        self.slot = slot
        self.livethread = livethread
        self.address = address
        self.fork1 = ForkFrameFilterN("fork1")
        self.ctx =\
            LiveConnectionContext(LiveConnectionType_rtsp, 
                self.address, self.slot, self.fork1)
        self.n_fork = 0

    def connect(self, filter):
        """Get a fork from main branch to a filter
        """
        self.n_fork += 1
        self.fork1.connect("decoder" + str(self.n_fork), filter)

    def __call__(self):
        # print("MainBrach: __call__")
        # register and play the live stream
        self.livethread.registerStreamCall(self.ctx)
        self.livethread.playStreamCall(self.ctx)

    def requestStop(self):
        self.livethread.stopStreamCall(self.ctx)
        self.livethread.deregisterStreamCall(self.ctx)

    def waitStop(self):
        pass

    def getNumReplicas(self):
        return self.n_fork



class Filterchain:

    def __init__(self, livethread = None, address = None, 
            slot = 1, interval = 10, sws = None, verbose = False, n_stack = None,
            n_threads = None, replicates = 1
            ):
        self.livethread = livethread
        self.interval = int(interval*1000) # sec to msec
        self.address = address
        self.slot = slot
        self.sws = sws # None or tuple: (width, height)
        self.verbose = verbose
        self.n_threads = n_threads

        self.main_branch = MainBranch(1, livethread, address)
        self.decode_branches = []
        for n in range(0, replicates):
            decode_branch = DecodeBranch(
                n,
                verbose = self.verbose,
                sws = self.sws,
                n_threads = self.n_threads,
                # affinity = affinity,
                interval = self.interval
            )
            self.main_branch.connect(decode_branch.getInputFilter())
            self.decode_branches.append(decode_branch)


    def __call__(self):
        """Start threads
        """
        for decode_branch in self.decode_branches:
            decode_branch()
        self.main_branch()


    def stop(self):
        for decode_branch in self.decode_branches:
            decode_branch.requestStop()
        self.main_branch.requestStop()
        for decode_branch in self.decode_branches:
            decode_branch.waitStop()
        self.main_branch.waitStop()
    

    def getNumReplicas(self):
        return self.main_branch.getNumReplicas()


def makeChains():
    """Create filterchains based on a yaml file that looks like this:

    ::

        address: rtsp://user:passwd@192.168.1.12
        interpolate: [300,300] # optional
        interval: 1 # in secs
        replicate: 10 # replicate stream this many times
        duration: 60
        verbose: false # optional
        decoder_threads: 2 # optional # how many libav(ffmpeg) threads per decoder

    If the top-level "interpolate" is present, then all YUVs are interpolated into that
    RGB dimensions

    Interval indicates how often (in secs) the achieved fps is printed to the terminal

    If no interpolation is present, then it's just YUV

    Duration is the tests overall duration in seconds

    If verbose is found and true, info about each and every frame that comes out of the
    pipeline is printed to the terminal (only for debugging this program)
    """
    with open('vaapi_streams.yaml','r') as f:
        dic=yaml.safe_load(f)

    itp = dic.get("interpolate", None)
    n_threads = dic.get("decoder_threads", None)
    verbose = dic.get("verbose", False)

    assert "address" in dic, "needs stream address"
    assert "duration" in dic, "needs test duration"
    assert "interval" in dic, "needs print interval frequency"
    assert "replicate" in dic, "needs number of replicates"

    ffc=FrameFifoContext() 
    if "n_stack_live" in dic:
        ffc.n_basic = dic["n_stack_live"]        
    livethread =LiveThread("livethread", ffc)
    
    fc = Filterchain(
        livethread = livethread, 
        address = dic["address"],
        interval = dic["interval"],
        slot = 1,
        sws = itp,
        verbose = verbose, 
        n_threads = n_threads,
        replicates = dic["replicate"]
    )
    # start live connections and decoders
    print("USING", fc.getNumReplicas(), "REPLICAS")
    # start livethread
    livethread.startCall()
    fc() # activate rtsp connection, start decoders
    print("stream started, running test for", dic["duration"], "seconds")
    time.sleep(dic["duration"])
    print("stopping connection and decoders")
    fc.stop()
    print("stopping livethread")
    livethread.stopCall()
    print("have a nice day!")


if __name__ == "__main__":
    from valkka.api2.logging import setFFmpegLogLevel, setValkkaLogLevel, loglevel_normal
    # setFFmpegLogLevel(1)
    setValkkaLogLevel(loglevel_normal)
    makeChains()
