import time, sys
from valkka.multiprocess import MessageProcess, MessageObject, safe_select
from valkka.api2 import ShmemRGBClient, ShmemRGBServer, ShmemClient
from skeleton.singleton import getEventFd, reserveEventFd, releaseEventFd, eventFdToIndex, reserveIndex
from skeleton.multiprocess.rgb import RGB24Process


class ClientProcess(RGB24Process):
    """Gets RGB24 frames from libValkka c++ side, inspects them & then forwards them to a master process

    = needs to establish an RGB24 shmem server

    Receives a message (byte payload also possible) from the master process
    """
    def __init__(self, 
        mstimeout = 1000, 
        server_img_width = 100, 
        server_img_height = 100):
        super().__init__(mstimeout = mstimeout)
        self.event_fd = reserveEventFd() # event fd for the RGB24 shmem server

        self.server_name = str(id(self))
        self.server_n_ringbuffer = 10
        self.server_width = server_img_width
        self.server_height = server_img_height

        self.intercom_ipc_index = None # eventfd index for sending messages to master process
        self.intercom_client = None
        self.intercom_fd = None


    def __del__(self):
        releaseEventFd(self.event_fd)


    """BACKEND methods

    Never call these methods from the main python process: 
    they are internal for the multiprocess backend
    """
    def preRun__(self):
        super().preRun__()
        # shmem servers could also be created on-demand for various master processes..
        self.server = ShmemRGBServer(
            name = self.server_name,
            n_ringbuffer = self.server_n_ringbuffer,
            width = self.server_width,
            height = self.server_height
        )
        self.server.useEventFd(self.event_fd)
        print("ClientProcess: using event_fd for serving frames fd=", self.event_fd.getFd())


    def postRun__(self):
        super().postRun__()


    def readPipes__(self, timeout):
        """Multiplex all intercom pipes / events

        This is used by your multiprocesses run() method
        (which you don't need to touch)

        Multiplexing file-descriptor is actually more neat in asyncio: 
        see the fragmp4 process

        For a tutorial for multiplexing communication pipes and sockets
        in normal (not asyncio) python, see: https://docs.python.org/3/howto/sockets.html
        """
        rlis = [self.back_pipe]
        # self.back_pipe is the intercom pipe with the main python process

        # listen to all rgb frame sources

        frame_fds = list(self.client_by_fd.keys())

        rlis += frame_fds
        
        if self.intercom_fd is not None:
            rlis.append(self.intercom_fd)

        rs, ws, es = safe_select(rlis, [], [], timeout = timeout)

        # rs is a list of event file descriptors that have been triggered
        for fd in rs:
            # 1. handle the main intercom pipe
            if fd == self.back_pipe:
                self.handleBackPipe__(self.back_pipe)
            # 2. handle frame coming from libValkka c++ side
            if fd in frame_fds:
                client = self.client_by_fd[fd]
                index, meta = client.pullFrame()
                if (index == None):
                    print("weird.. rgb client got none")
                else:
                    data = client.shmem_list[index][0:meta.size]
                    data = data.reshape((meta.height, meta.width, 3))
                    self.handleFrame__(data, meta)
            # 3. handle messages from master process
            if fd == self.intercom_fd:
                obj = self.intercom_client.pullObject()
                self.handleMessage__(obj)


    def handleFrame__(self, frame, meta):
        print("ClientProcess: handleFrame__ : got frame", frame.shape, "from slot", meta.slot)
        """metadata has the following members:
        size 
        width
        height
        slot
        mstimestamp
        """
        # do something with the frame
        # then forward it to the master process:
        ## TODO: if too big a frame is sent, the client will hang!  check this!
        self.server.pushFrame(frame[0:10, 0:10, :], meta.slot, meta.mstimestamp)
        # send a message to the main process like this:
        # self.send_out__({})


    def handleMessage__(self, obj):
        print("ClientProcess: handleMessage__ : got a message from master", obj)


    def c__listenIntercom(self,
        name = None,
        n_ringbuffer = None,
        n_bytes = None,
        ipc_index = None,
        ):
        client = ShmemClient(
            name = name,
            n_ringbuffer = n_ringbuffer,
            n_bytes = n_bytes,
            mstimeout = self.mstimeout
        )
        eventfd = getEventFd(ipc_index)
        client.useEventFd(eventfd)
        fd = eventfd.getFd()
        # self.intercom_client_by_fd[fd] = client # if you would be listening many clients at a time
        self.intercom_client = client
        self.intercom_fd = fd


    def c__dropIntercom(self
        # ipc_index = None,
        ):
        # fd = getFdFromIndex(ipc_index)
        # self.intercom_client_by_fd.pop(fd) # if you would be listening many clients at a time
        self.intercom_client = None
        self.intercom_fd = None


    """FRONTEND
    
    These methods are called by your main python process
    """

    def getRGB24ServerPars(self):
        pars = {
            "name" : self.server_name,
            "n_ringbuffer" : self.server_n_ringbuffer,
            "width" : self.server_width,
            "height" : self.server_height,
            "ipc_index" : eventFdToIndex(self.event_fd)
        }
        print("getRGB24ServerPars:", pars)
        return pars
           

    def listenIntercom(self,
        name = None,
        n_ringbuffer = None,
        n_bytes = None,
        ipc_index = None
        ):
        if self.intercom_ipc_index is not None:
            print("listenIntercom: already listening to master")
            return

        self.sendMessageToBack(MessageObject(
            "listenIntercom",
            name = name,
            n_ringbuffer = n_ringbuffer,
            n_bytes = n_bytes,
            ipc_index = ipc_index # event fd index for the intecom channel
        ))
        self.intercom_ipc_index = ipc_index


    def dropIntercom(self):
        if self.intercom_ipc_index is None:
            print("dropIntercom: no intercom")
            return
        self.sendMessageToBack(MessageObject(
            "dropIntercom"
            # ipc_index = ipc_index # event fd index for the intecom channel
        ))
        self.intercom_ipc_index = None



def test1():
    ipc_index = reserveIndex()
    p = ClientProcess()
    p.start()
    time.sleep(1)
    print("exiting")
    p.stop()
    print("bye!")


if __name__ == "__main__":
    test1()

