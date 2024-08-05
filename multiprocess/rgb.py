import time, sys, logging
from setproctitle import setproctitle
from valkka.multiprocess import MessageProcess, MessageObject, safe_select
from valkka.api2 import ShmemRGBClient
from valkka.multiprocess.sync import EventGroup, SyncIndex
from singleton import event_fd_group_1

class RGB24Process(MessageProcess):
    """A multiprocess that reads RGB24 frames from shared memory and does something with them

    You can use this process to read several libValkka RGB24 frame servers simultaneously.

    Let's call the shmem rgb24 clients with RGBCLIENT-N
    """
    def __init__(self, mstimeout = 1000, name="rgb24process"):
        super().__init__(name=name)
        self.mstimeout = mstimeout
        # events to synchronize some multiprocessing frontend calls
        # with the backend excecution:
        self.eg = EventGroup(10)
        self.uuid = None

    """BACKEND methods
    """
    def preRun__(self):
        """This should be subclassed for your multiprocess class.  It is executed just after the fork (i.e. in the backend)
        
        Use this to do variable initialization etc. before the execution starts and for naming your multiprocess
        """    
        self.logger.debug("preRun__")
        # name your multiprocess: now you can easily find it with linux process and memory
        # monitoring tools
        # I recommend using smem and/or htop
        setproctitle("Valkka-example-RGB24Process")
        self.client_by_fd = {}
        self.shmem_pars_by_slot = {}


    def postRun__(self):
        """Last thing executed before multiprocess exits
        """
        self.logger.debug("postRun__")
        # clear & garbage collect rgb clients before process exit:
        self.client_by_fd = {}


    # backend methods: do not call these from the frontend 
    # (i.e. from the main python process)
    
    def readPipes__(self, timeout):
        """Multiplex all intercom pipes / events

        This is used by your multiprocesses run() method
        
        For a tutorial for multiplexing communication pipes and sockets
        in normal (not asyncio) python, see: https://docs.python.org/3/howto/sockets.html
        """
        rlis = [self.back_pipe]
        # self.back_pipe is the intercom pipe with the main python process
        # listen to all rgb frame sources
        frame_fds = list(self.client_by_fd.keys())

        rlis += frame_fds
        
        rs, ws, es = safe_select(rlis, [], [], timeout = timeout)

        # rs is a list of event file descriptors that have been triggered
        for fd in rs:
            # 1. handle the main intercom pipe # MAIN
            if fd == self.back_pipe:
                self.handleBackPipe__(self.back_pipe)
            # 2. handle frame coming from libValkka c++ side # RGBCLIENT
            if fd in frame_fds:
                client = self.client_by_fd[fd]
                index, meta = client.pullFrame()
                if (index == None):
                    self.logger.warning("handleFrame__ : rgb client got none")
                else:
                    data = client.shmem_list[index][0:meta.size]
                    data = data.reshape((meta.height, meta.width, 3))
                    self.handleFrame__(data, meta)


    def handleFrame__(self, frame, meta):
        """This will be subclassed/overwritten by the derived class"""
        self.logger.debug("handleFrame__ : rgb client got frame % from slot %s", frame.shape, meta.slot)
        """metadata has the following members:
        size 
        width
        height
        slot
        mstimestamp
        """
        # send a message to the main process like this:
        self.send_out__({"results from" : "RGB24Process"})


    # commands that come from the main python process (aka frontend)
    def c__activateRGB24Client(self, 
            name = None, 
            n_ringbuffer = None, 
            width = None , 
            height = None,
            ipc_index = None
            ):
        """This will activate a shared memory client that reads RGB24 frames
        from shared memory libValkka c++ side (as defined in your filterchain)
        
        NOTE: the sync primitives are not sent between front/backend as such, but an index
        of pre-preserved sync primitive is sent instead (that's something that can be serialized)
        """
        self.logger.debug("c__activateRGB24Client called with %s %s %s %s", name, n_ringbuffer, width, height)
        client = ShmemRGBClient( # RGBCLIENT-N
            name = name,
            n_ringbuffer = n_ringbuffer,
            width = width,
            height = height,
            mstimeout = self.mstimeout,
            verbose = False
        )
        eventfd = event_fd_group_1.fromIndex(ipc_index)
        client.useEventFd(eventfd) # do not forget!
        # let's get a posix file descriptor, i.e. a plain integer:
        fd = eventfd.getFd()
        self.client_by_fd[fd] = client
        

    def c__deactivateRGB24Client(self,
        ipc_index = None,
        event_index = None
        ):
        """
        NOTE: the sync primitives are not sent between front/backend as such, but an index
        of pre-preserved sync primitive is sent instead (that's something that can be serialized)
        """
        eventfd = event_fd_group_1.fromIndex(ipc_index)
        # let's get a posix file descriptor, i.e. a plain integer
        fd = eventfd.getFd()
        try:
            self.client_by_fd.pop(fd)
        except KeyError:
            self.logger.warning("c__deactivateRGB24Client : no client at ipc_index %s", ipc_index)
        # inform multiprocessing frontend (= main python process)
        # that this command has been finalized:
        self.eg.set(event_index)


    def c__customCall(self, parameter = 1):
        """The backend part of some custom call

        In asyncio, always encapsulate your methods with try/except
        """
        try:
            print("some asynchronous custom call with parameter", parameter)
        except Exception as e:
            print("c__customCall failed with", e)


    """FRONTEND
    
    These methods are called by your main python process
    """

    def activateRGB24Client(self, 
            name = None,
            n_ringbuffer = None,
            width = None,
            height = None,
            ipc_index = None
        ):
        """Tells process to start getting frames from libValkka cpp side
        """
        self.sendMessageToBack(MessageObject(
            "activateRGB24Client",
            name = name,
            n_ringbuffer = n_ringbuffer,
            width = width,
            height = height,
            ipc_index = ipc_index
        ))
        # that intercommunicates with backend and looks
        # for method "c__activateRGB24Client" there in
        

    def deactivateRGB24Client(self, ipc_index):
        """This frontend method returns only after the backend 
        method "c__deactivateRGB24Client" exits.

        It's a good idea to do this, for example, when adding/removing rgb shmem
        servers and clients.  

        This is done using the SyncIndex context manager:
        """
        with SyncIndex(self.eg) as i:
            # this section exits once the backend
            # call is ready
            self.sendMessageToBack(MessageObject(
                "deactivateRGB24Client",
                ipc_index = ipc_index,
                event_index = i
            ))
        self.logger.debug("deactivateRGB24Client OK %s", ipc_index)


    def setUUID(self,uuid):
        """NOTE: about the uuid:

        In principle, there could be serveral client processes per camera: for example,
        several analyzer processes can be watching different areas (as defined per bboxes) of the same stream, 
        each area/bbox, identified by an uuid
        """
        self.uuid = uuid


    def getUUID(self):
        return self.uuid


    def customCall(self, parameter = 1):
        # your demo custom call :)
        self.sendMessageToBack(MessageObject(
            "customCall",
            parameter = parameter
        ))
        # that intercommunicates with backend and looks
        # for method "c__customCall" there in

