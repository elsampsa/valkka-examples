"""Reads camera info from file "streams.yaml" file & informs in terminal the achieved fps rates for each camera.

Nice for testing how libValkka works for your big camera systems.

The reported fps is for decoded YUV frames.  You can add an optional YUV -> RGB interpolation stage to
see how it affects your fps.

For the exact format of the .yaml file, please see below
"""

import os, yaml, time
from valkka.core import *
"""We can express a filterchain as a hierarchical list as well!  (no need for ascii art):

::

    MAIN BRANCH
        SOURCE
            {ForkFrameFilterN: fork1}
                DECODE-BRANCH
                other branches

    DECODE-BRANCH
        (AVThread:avthread) 
            {ForkFrameFilterN: fork2}
                {SwSScaleFrameFilter: sws_filter (optional)}
                    {FPSCountFrameFilter: count_filter}
"""
class Filterchain:

    def __init__(self, livethread = None, address = None, 
            slot = 1, interval = 10, sws = None, verbose = False, n_stack = None,
            affinity = None, n_threads = None
            ):
        self.livethread = livethread
        self.interval = int(interval*1000) # sec to msec
        self.address = address
        self.slot = slot
        self.sws = sws # None or tuple: (width, height)
        self.verbose = verbose
        self.n_stack = n_stack # not used

        # *** DECODE BRANCH ***
        # Create the FPSCountFrameFilter

        name = f"slot: {self.slot}: {self.address}"
        if self.verbose:
            # just in order to see what it is exactly we get from the end
            # of the pipeline..!
            self.info = BriefInfoFrameFilter("info-"+str(self.slot))
            self.counter = FPSCountFrameFilter(name, self.interval, self.info)
        else:
            self.counter = FPSCountFrameFilter(name, self.interval)
        if self.sws:
            # Create the SwScaleFrameFilter (optional)
            width, height = self.sws
            sws_opt = SwScaleFrameFilter("sws-"+str(self.slot), 
                width, height, self.counter)
            self.fork2_in = sws_opt
            print("slot", self.slot,"interpolating to", width, height)
        else:
            self.fork2_in = self.counter

        # Bitmap fork
        self.fork2 = ForkFrameFilterN("fork2")
        self.fork2.connect("bitmap-"+str(self.slot), self.fork2_in)

        #ffc=core.FrameFifoContext() 
        #if self.n_stack is not None:
        #    ffc.n_basic = dic["n_stack_live"]        
    
        self.avthread = AVThread(
            "avthread-" + str(self.slot),
            self.fork2) # feeds the bitmap fork & decoding branch
            # self.framefifo_ctx)

        if n_threads:
            print("setting", n_threads,"threads per libav decoder")
            self.avthread.setNumberOfThreads(n_threads)

        if affinity is not None:
            print("binding stream at slot", slot, "to core", affinity)
            self.avthread.setAffinity(affinity)

        # *** MAIN BRANCH ***
        self.fork1 = ForkFrameFilterN("fork1")
        self.fork1.connect("decoder" + str(self.slot), self.avthread.getFrameFilter())
        self.ctx =\
            LiveConnectionContext(LiveConnectionType_rtsp, 
                self.address, self.slot, self.fork1)


    def __call__(self):
        # start decoding thread
        self.avthread.startCall()
        # start decoding
        self.avthread.decodingOnCall()
        # register and play the live stream
        self.livethread.registerStreamCall(self.ctx)
        self.livethread.playStreamCall(self.ctx)


    def requestStop(self):
        self.livethread.stopStreamCall(self.ctx)
        self.livethread.deregisterStreamCall(self.ctx)
        self.avthread.requestStopCall()


    def waitStop(self):
        self.avthread.waitStopCall()


def makeChains():
    """Create filterchains based on a yaml file that looks like this:

    ::

        streams:
            - name: that camera
              address: rtsp://user:passwd@192.168.1.12
              interpolate: [300,300] # optional
              use: true # optional
              bind: 1 # optional
            - name: that other camera
              address: rtsp://user:passwd@192.168.1.13
              interpolate: [300,300] # optional
              use: true # optional
        interpolate: [300,300] # optional
        interval: 10
        duration: 60
        verbose: false
        n_stack_live: 50 # optional
        # n_stack_decoder: 20 # not used
        bind: 0 # bind livethread to a core # optional
        decoder_threads: 2 # how many libav(ffmpeg) threads per decoder

    If the top-level "interpolate" is present, then all YUVs are interpolated into that
    RGB dimensions

    Per-camera interpolations overwrite the top-level interpolate if they're present

    Interval indicates how often (in secs) the achieved fps is printed to the terminal

    If no interpolation is present, then it's just YUV

    Duration is the tests overall duration in seconds

    If verbose is found and true, info about each and every frame that comes out of the
    pipeline is printed to the terminal (only for debugging this program)

    "use" is an optional attribute: it it is present AND false, then the camera is omitted

    "bind" : (int) optional, bind to a certain core

    TODO: possible test:

    - mux & push H264 somewhere --> does this affect overall framerate?
    - same for pushing into shmem rgb server

    ..can just use buffers that overflow (& should shut up the overflow warning)
    """
    with open('streams.yaml','r') as f:
        dic=yaml.safe_load(f)

    if "interpolate" in dic:
        itp = dic["interpolate"]
    else:
        itp = None

    verbose = False
    if ("verbose" in dic) and (dic["verbose"]):
        verbose = True

    assert "streams" in dic, "needs streams"
    assert "duration" in dic, "needs test duration"
    assert "interval" in dic, "needs print interval frequency"

    ffc=FrameFifoContext() 
    if "n_stack_live" in dic:
        ffc.n_basic = dic["n_stack_live"]        
    livethread =LiveThread("livethread", ffc)

    if "bind" in dic:
        print("binding livethread to", dic["bind"])
        livethread.setAffinity(dic["bind"])

    if "n_stack_decoder" in dic:
        n_stack_decoder = dic["n_stack_decoder"]
    else:
        n_stack_decoder = None
    # not used

    n_threads = dic.get("decoder_threads", None)

    chains = []
    cc = 1
    for stream in dic["streams"]:
        assert "name" in stream
        assert "address" in stream
        if "interpolate" in stream:
            itp_ = stream["interpolate"]
        else:
            itp_ = itp

        if "use" in stream and (not stream["use"]):
           continue  

        bind = stream.get("bind", None)
        
        fc = Filterchain(
            livethread = livethread, 
            address = stream["address"],
            interval = dic["interval"],
            slot = cc, 
            sws = itp_,
            verbose = verbose, 
            n_stack = n_stack_decoder,
            affinity = bind,
            n_threads = n_threads
        )
        chains.append(fc)
        cc+=1

    # start livethread
    livethread.startCall()

    # start live connections and decoders
    print("USING", len(chains), "STREAM(S)")
    for chain in chains:
        chain()

    print("all cams started, running test for", dic["duration"], "seconds")
    time.sleep(dic["duration"])
    print("stopping all connections and decoders")
    for chain in chains:
        chain.requestStop()
    print("waiting for them to stop")
    for chain in chains:
        chain.waitStop()
    print("stopping livethread")
    livethread.stopCall()
    print("have a nice day!")


if __name__ == "__main__":
    from valkka.api2.logging import setFFmpegLogLevel
    setFFmpegLogLevel(0)
    makeChains()
