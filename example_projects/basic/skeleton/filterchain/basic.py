import time
import sys
from valkka import core
# The objects in that "core" namespace are just wrapped cpp code.  You can find the documentation here: https://elsampsa.github.io/valkka-core/html/annotated.html
from skeleton.singleton import releaseEventFd, reserveEventFd, eventFdToIndex


class BasicFilterChain:
    """A filterchain is a graph that defines your video streaming structure:

    - Origin of the video
    - How the stream is branched, decoded and muxed
    - The final terminals.  These are typically shared memory arrays that are seen by other python processes

    Filterchains can get rather complicated.  See for example this one: https://elsampsa.github.io/valkka-examples/_build/html/lesson_7.html

    This is class encapsulates the filterchain, threads, muxers, interpolators and shared memory servers.

    It's a good idea to draw the filterchain here.

    This is an extended version of: https://elsampsa.github.io/valkka-examples/_build/html/lesson_4.html#receiving-frag-mp4-at-python

    ::

        (LiveThread:livethread) -->----------------------------------+  main_fork (forks into two: A and B)
                                                                     |     
                                                                     +----->  decoding branch (A) 
                                                                     |
             +-----------------------------------------<-------------+  mux branch (B)
             |
             +--> {FragMP4MuxFrameFilter:fmp4_muxer} --> {FragMP4ShmemFrameFilter:fmp4_shmem} 

                - This branch dumps frag-mp4 stream frames into shared memory.  From there it can be read at the python side.

        decoding branch (A):

        +------>> (AVThread:avthread) +
                                      |
                                      | decode_fork (on-demand fork)
                                      |
                                      +---- RGB24 branch (A.1)
                                      |
                                      +---- OpenGL branch (A.2)
                                      |
                                      +---- ....

        RGB branch (A.1):

        based on: https://elsampsa.github.io/valkka-examples/_build/html/lesson_4.html#server-side

        +--> {IntervalFrameFilter: interval_filter} --> {SwScaleFrameFilter: sws_filter} --> {RGBSharedMemFrameFilter: shmem_filter}

        - RGB24 frames into shared memory.  Client process reads them at the python side
        - Frames are interpolated and dumped into shared memory once a second

        OpenGL branch (A.2):

        +-->> (OpenGLThread:glthread)

        - This one dumps video into the screen

    - RGB24 frames frag-mp4 fragments are dumped into posix shared memory as defined in this class.
    - They are typically read using another multiprocess elsewhere in your streaming system.
    """

    def __init__(self, address = None, slot = None, rgb_sync_event = None, fmp4_sync_event = None):
        assert(isinstance(address, str))
        assert(isinstance(slot, int))
        assert(isinstance(rgb_sync_event, core.EventFd))
        assert(isinstance(fmp4_sync_event, core.EventFd))

        id_ = str(id(self))        
        self.active = True
        self.rtsp_address = address
        self.slot = slot
        self.rgb_sync_event = rgb_sync_event
        self.fmp4_sync_event = fmp4_sync_event

        # RGB interpolation interval and shared memory definitions
        # define yuv=>rgb interpolation interval
        self.image_interval=1000  # YUV => RGB interpolation to the small size is done each 1000 milliseconds and passed on to the shmem ringbuffer
        # define rgb image dimensions, based on your needs
        self.width  =1920 
        self.height =1080
        # posix shared memory
        self.rgb_shmem_name = id_ + "_rgb"    # Unique posix shared memory identifier
        self.rgb_shmem_buffers = 10           # number of cells in the ringbuffer

        # shared memory definitions for frag-mp4
        self.fmp4_shmem_buffers = 10 # 10 element in the ring-buffer
        self.fmp4_shmem_name = id_ + "_fragmp4" # unique name identifying this shared memory
        self.fmp4_shmem_cellsize = 1024*1024*1 # max size for each MP4 fragment.  Feel free to make bigger

        
    def __del__(self):
        if self.active:
            self.close()


    def __call__(self, livethread = None, openglthread = None):
        """Register running live & openglthreads, construct filterchain, start threads

        For more information about all this, see the tutorial in 
        https://elsampsa.github.io/valkka-examples/_build/html/tutorial.html

        """
        assert(livethread is not None)
        self.livethread = livethread
        self.openglthread = openglthread

        """Filtergraphs are always constructed from end to beginning
        """
        # main branch
        self.main_fork = core.ForkFrameFilterN("main_fork_"+str(self.slot))
        # connect livethread to main branch
        self.live_ctx = core.LiveConnectionContext(core.LiveConnectionType_rtsp, self.rtsp_address, self.slot, self.main_fork) # stream writes to main_fork
        ## some parameters you can give to the live streaming context:
        #self.live_ctx.request_tcp = True
        #self.live_ctx.time_correction = core.TimeCorrectionType_smart
        ## see more here: https://elsampsa.github.io/valkka-core/html/structLiveConnectionContext.html
        self.livethread.registerStreamCall(self.live_ctx)

        # Mux branch (B)
        self.fmp4_shmem = core.FragMP4ShmemFrameFilter(self.fmp4_shmem_name, self.fmp4_shmem_buffers, self.fmp4_shmem_cellsize)
        # print(">", self.fmp4_sync_event)
        self.fmp4_shmem.useFd(self.fmp4_sync_event)
        self.fmp4_muxer = core.FragMP4MuxFrameFilter("mp4_muxer", self.fmp4_shmem)
        # self.fmp4_muxer.activate() # don't forget!
        # connect main branch ==> mux branch
        self.main_fork.connect("fragmp4_terminal_"+str(self.slot), self.fmp4_muxer)
        # muxer must be connected from the very beginning, so that it receives setupframes, sent only in the beginning of the streaming process

        # decoding branch A
        self.decode_fork = core.ForkFrameFilterN("decode_fork_"+str(self.slot))
        self.avthread = core.AVThread("avthread_"+str(self.slot), self.decode_fork) # AVThread feeds decode_fork
        # connect main branch ==> AVThread => decode_fork
        self.avthread_in_filter = self.avthread.getFrameFilter()
        self.main_fork.connect("decoder_"+str(self.slot), self.avthread_in_filter)

        # RGB24 branch (A.1)
        self.rgb_shmem_filter =core.RGBShmemFrameFilter(self.rgb_shmem_name, self.rgb_shmem_buffers, self.width, self.height)
        self.rgb_shmem_filter.useFd(self.rgb_sync_event)
        self.sws_filter      =core.SwScaleFrameFilter("sws_filter", self.width, self.height, self.rgb_shmem_filter)
        self.interval_filter =core.TimeIntervalFrameFilter("interval_filter", self.image_interval, self.sws_filter)
        self.decode_fork.connect("rgb_shmem_terminal"+str(self.slot), self.interval_filter)

        # OpenGL branch (A.2)
        if self.openglthread is not None:
            # connect decode frames into the opengl thread
            self.opengl_input_filter = self.openglthread.getFrameFilter()
            self.decode_fork.connect("gl_terminal_"+str(self.slot), self.opengl_input_filter)
            # create an X-window
            self.window_id = self.openglthread.createWindow()
            self.openglthread.newRenderGroupCall(self.window_id)
            # maps stream with slot 1 to window "window_id"
            self.context_id = self.openglthread.newRenderContextCall(self.slot, self.window_id, 0)
        
        self.livethread.playStreamCall(self.live_ctx)
        self.avthread.startCall()
        self.avthread.decodingOnCall()


    def activateFragMP4(self):
        print("connecting fragmp4")
        self.fmp4_muxer.activate()

    def deactivateFragMP4(self):
        self.fmp4_muxer.deActivate()

    def resendMP4Meta(self):
        self.fmp4_muxer.sendMeta()


    def getRGBParameters(self):
        """Returns shared memory parameters.  Use this function to get them for the client
        """
        return {
            "name": self.rgb_shmem_name,
            "n_ringbuffer": self.rgb_shmem_buffers,
            "width": self.width,
            "height": self.height
        }


    def getRGBSyncEvent(self):
        """Eventfd for synchronization with the process that reads the RGB24 frames from shared memory
        """
        return self.rgb_sync_event


    def getFragMP4Parameters(self):
        """Returns shared memory parameters.  Use this function to get them for the client
        """
        return {
            "name": self.fmp4_shmem_name,
            "n_ringbuffer": self.fmp4_shmem_buffers,
            "n_size": self.fmp4_shmem_cellsize
        }


    def getFMP4SyncEvent(self):
        """Like get RGBEvent but for frag-mp4
        """
        return self.fmp4_sync_event


    def close(self):
        # stop muxing
        self.fmp4_muxer.deActivate() # TODO: remove (in core)
        # stop streaming
        self.livethread.stopStreamCall(self.live_ctx)
        self.avthread.stopCall()
        if self.openglthread is not None:
            self.openglthread.delRenderContextCall(self.context_id)
            self.openglthread.delRenderGroupCall(self.window_id)
        releaseEventFd(self.rgb_sync_event)
        releaseEventFd(self.fmp4_sync_event)
        self.active = False


    

def main():
    """Simple filterchain creation test
    """
    openglthread = core.OpenGLThread("openglthread")
    openglthread.startCall()
    livethread = core.LiveThread("livethread")
    livethread.startCall()

    if len(sys.argv) < 2:
        print("please give rtsp camera address as the first argument")

    filterchain = BasicFilterChain(
        address = sys.argv[1],
        slot = 1,
        rgb_sync_event = reserveEventFd(),
        fmp4_sync_event = reserveEventFd()
    )

    ## runs the filterchain
    filterchain(livethread = livethread, openglthread = openglthread)
    print("server is running for some time")
    filterchain.activateFragMP4()
    time.sleep(12)
    print("livethread stop")
    # preferably shutdown the system from beginning-to-end
    livethread.stopCall()
    filterchain.close()
    print("openglthread stop")
    openglthread.stopCall()
    print("bye!")


if __name__ == "__main__":
    main()

