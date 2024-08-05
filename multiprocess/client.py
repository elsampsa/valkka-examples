import time, sys, logging
from multiprocessing import Event
from valkka.multiprocess import MessageProcess, MessageObject, safe_select
from valkka.api2 import ShmemRGBClient, ShmemRGBServer, ShmemClient, ShmemServer
from singleton import event_fd_group_1 # from local file
from rgb import RGB24Process # from local file

class ClientProcess(RGB24Process):
    """
    - Receives RGB24 frames from N libValkka C++ frame servers (and from other processes if necessary)
      --> has rgb24 frame clients: RGBCLIENT-N.  NOTE: these were instantiated in the base class RGB24Process
    - Inspects received frames & forwards them to a master process
      --> Has an RGB24 shmem server  == RGB24SERVER
    - Receives a messages (byte payload also possible) from the master process
      --> Has an shmem data client == DATACLIENT
    - Shmem data server for sending data results to a downstream
      websocket process == DATASERVER

    :param server_img_width: Max image width for RGB24SERVER
    :param server_img_height: Max image height for RGB24SERVER
    :param datasize: Max serialized data size for DATASERVER
    """
    def __init__(self,
        mstimeout = 1000, # internal semaphore timeout
        server_img_width = 1920,
        server_img_height = 1080,
        datasize = 1024*1024*1, # 1MB
        name = "clientprocess"
        ):
        super().__init__(mstimeout = mstimeout, name=name)

        # RGB24SERVER parameters
        ind, self.event_fd = event_fd_group_1.reserve()
        self.server_name = str(id(self))
        self.logger.debug("init: rgb server: name=%s, eventfd index=%i, fd=%i", self.server_name, ind, self.event_fd.getFd())
        self.server_n_ringbuffer = 10
        self.server_width = server_img_width
        self.server_height = server_img_height

        # DATACLIENT parameters
        self.dataclient_ipc_index = None # eventfd index for sending messages to master process
        self.dataclient_client = None
        self.dataclient_fd = None

        # DATASERVER parameters - dataserver for a downstream client
        self.data_n_bytes = datasize
        self.data_n_buffer = 10
        self.data_name_server = "data_"+str(id(self))
        ind, self.data_server_ipc = event_fd_group_1.reserve() # index, EventFd
        self.logger.debug("init: data server: eventfd index=%i, fd=%i", ind, self.data_server_ipc.getFd())
        #
        self.rgb_server_ok = Event()
        self.rgb_server_ok.clear()
        #
        self.data_server_ok = Event()
        self.data_server_ok.clear()


    def __del__(self):
        event_fd_group_1.release(self.event_fd) # RGB24SERVER


    """BACKEND methods

    Never call these methods from the main python process: 
    they are internal for the multiprocess backend
    """
    def preRun__(self):
        super().preRun__()
        # shmem servers could also be created on-demand for various master processes..
        # RGB24SERVER:
        self.server = ShmemRGBServer(
            name = self.server_name,
            n_ringbuffer = self.server_n_ringbuffer,
            width = self.server_width,
            height = self.server_height
        )
        self.server.useEventFd(self.event_fd)
        self.logger.debug("using event_fd for serving frames fd=%s", self.event_fd.getFd())

        # DATASERVER:
        self.data_server = ShmemServer(
            name=self.data_name_server,
            n_ringbuffer=self.data_n_buffer,  # size of the ring buffer
            n_bytes=self.data_n_bytes,
            verbose=False
        )
        self.data_server.useEventFd(self.data_server_ipc)
        self.logger.debug("preRun__: %s %s %s",
            self.data_name_server, self.data_n_buffer, self.data_n_bytes)
        self.logger.debug("preRun__: using eventfd index %i for dataserver",
            event_fd_group_1.asIndex(self.data_server_ipc))
        
        # very important, so that downstream clients do not create
        # shmem clients before the servers have been created
        self.rgb_server_ok.set()
        self.data_server_ok.set()


    def postRun__(self):
        super().postRun__()
        event_fd_group_1.release(self.data_server_ipc)
        # evoke garbage collection of rgb & data servers:
        self.server = None
        self.data_server = None
        self.rgb_server_ok.clear()
        self.data_server_ok.clear()

        
    def readPipes__(self, timeout):
        """Multiplex all (inter)com pipes / events
        """
        rlis = [self.back_pipe]
        # self.back_pipe is the intercom pipe with the main python process
        # listen to all rgb frame sources
        frame_fds = list(self.client_by_fd.keys()) # RGBCLIENT

        rlis += frame_fds
        
        if self.dataclient_fd is not None: # DATACLIENT
            rlis.append(self.dataclient_fd)

        rs, ws, es = safe_select(rlis, [], [], timeout = timeout)

        # rs is a list of event file descriptors that have been triggered
        for fd in rs:
            # 1. handle the main intercom pipe
            if fd == self.back_pipe: # MAIN
                self.handleBackPipe__(self.back_pipe)
            # 2. handle frame coming from libValkka c++ side and from other processes (if necessary)
            if fd in frame_fds:
                client = self.client_by_fd[fd] # RGBCLIENT
                index, meta = client.pullFrame()
                if (index == None):
                    self.logger.warning("rgb client got none")
                else:
                    data = client.shmem_list[index][0:meta.size]
                    data = data.reshape((meta.height, meta.width, 3))
                    self.handleFrame__(data, meta)
            # 3. handle messages from master process # DATACLIENT
            if fd == self.dataclient_fd:
                obj = self.dataclient_client.pullObject()
                self.handleMessage__(obj)


    def handleFrame__(self, frame, meta):
        """This will be subclassed/ovewritten by your subclass.
        """
        self.logger.debug("handleFrame__ : got frame %s from slot %s", frame.shape, meta.slot)
        """metadata has the following members:
        size 
        width
        height
        slot
        mstimestamp
        """
        ## do something with the frame
        ## then forward it to the master process:
        ## WARNING: the frame size should match the maximum frame size defined for the rgb shmem server
        ## otherwise bad things will happen
        ## use RGB24SERVER to send (a portion of the) frame to the master process:
        self.server.pushFrame(frame[0:10, 0:10, :], meta.slot, meta.mstimestamp)
        ## send a message to the main process like this:
        # self.send_out__({})


    def handleMessage__(self, obj):
        self.logger.debug("handleMessage__ : got a message from master %s", obj)


    def c__listenDataServer(self,
        name = None,
        n_ringbuffer = None,
        n_bytes = None,
        ipc_index = None,
        ):
        # DATACLIENT
        client = ShmemClient(
            name = name,
            n_ringbuffer = n_ringbuffer,
            n_bytes = n_bytes,
            mstimeout = self.mstimeout
        )
        eventfd = event_fd_group_1.fromIndex(ipc_index)
        client.useEventFd(eventfd)
        fd = eventfd.getFd()
        # self.dataclient_client_by_fd[fd] = client # if you would be listening many clients at a time
        self.dataclient_client = client
        self.dataclient_fd = fd


    def c__dropDataServer(self
        # ipc_index = None,
        ):
        # fd = getFdFromIndex(ipc_index)
        # self.intercom_client_by_fd.pop(fd) # if you would be listening many clients at a time
        self.dataclient_client = None
        self.dataclient_fd = None


    """FRONTEND
    
    These methods are called by your main python process
    """

    def getRGB24ServerPars(self): # RGB24SERVER
        self.rgb_server_ok.wait()
        # --> be sure that the shmem server has been started
        # before giving any information about it
        pars = {
            "name" : self.server_name,
            "n_ringbuffer" : self.server_n_ringbuffer,
            "width" : self.server_width,
            "height" : self.server_height,
            "ipc_index" : event_fd_group_1.asIndex(self.event_fd)
        }
        self.logger.debug("getRGB24ServerPars: %s", pars)
        return pars
           
    def getDataShmemPars(self): # DATASERVER
        """this is used by downstream (say, websocket) multiprocess

        Returns shmem parameters for listening results from this multiprocess through shmem
        """
        self.data_server_ok.wait()
        # --> be sure that the shmem server has been started
        # before giving any information about it
        return {
            "name": self.data_name_server,
            "n_ringbuffer": self.data_n_buffer,
            "n_bytes": self.data_n_bytes,
            "ipc_index": event_fd_group_1.asIndex(self.data_server_ipc)
        }
    

    def listenDataServer(self,
        name = None,
        n_ringbuffer = None,
        n_bytes = None,
        ipc_index = None
        ):
        """Tell this client process to listen to a certain
        master process
        """
        if self.dataclient_ipc_index is not None:
            self.logger.warning("listenDataServer: already listening to master")
            return

        self.sendMessageToBack(MessageObject(
            "listenDataServer",
            name = name,
            n_ringbuffer = n_ringbuffer,
            n_bytes = n_bytes,
            ipc_index = ipc_index # event fd index for the intecom channel
        ))
        self.dataclient_ipc_index = ipc_index


    def dropDataServer(self):
        """Tell this client process to stop listening
        to a certain master process
        """
        if self.dataclient_ipc_index is None:
            self.logger.warning("dropDataServer: no ipc")
            return
        self.sendMessageToBack(MessageObject(
            "dropDataServer"
        ))
        self.dataclient_ipc_index = None



def test1():
    p = ClientProcess()
    p.formatLogger(logging.DEBUG)
    p.start()
    time.sleep(1)
    print("exiting")
    p.stop()
    print("bye!")


if __name__ == "__main__":
    test1()
