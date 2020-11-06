import sys, os, uuid, time
from valkka.multiprocess import MessageProcess, MessageObject, safe_select
from valkka.api2 import ShmemRGBClient, ShmemRGBServer, ShmemClient, ShmemServer
from skeleton.singleton import getEventFd, reserveEventFd, releaseEventFd, eventFdToIndex, reserveIndex, getFdFromIndex


class MasterProcess(MessageProcess):
    """Receives RGB24 frames from a client process & responds with a message and some other data
    """
    def __init__(self, mstimeout = 1000):
        super().__init__()
        self.registered_clients = []
        self.mstimeout = mstimeout
        self.intercom_n_bytes = 1024*1024*1 # 1 MB
        self.intercom_n_buffer = 10
        

    def preRun__(self):
        super().preRun__()
        self.client_by_fd = {}
        self.intercom_server_by_fd = {}
        self.intercom_server_by_client_fd = {}
        # here you would also create your heavy neural net detector instance


    def postRun__(self):
        super().postRun__()
        self.client_by_fd = {}
        self.intercom_server_by_fd = {}
        self.intercom_server_by_client_fd = {}


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
        rs, ws, es = safe_select(rlis, [], [], timeout = timeout)
        # rs is a list of event file descriptors that have been triggered
        for fd in rs:
            # 1. handle the main intercom pipe
            if fd == self.back_pipe:
                self.handleBackPipe__(self.back_pipe)
            # 2. handle frame coming from the client processes
            if fd in frame_fds:
                client = self.client_by_fd[fd]
                index, meta = client.pullFrame()
                if (index == None):
                    print("weird.. rgb client got none")
                else:
                    data = client.shmem_list[index][0:meta.size]
                    data = data.reshape((meta.height, meta.width, 3))
                    self.handleFrame__(data, meta, fd)


    def handleFrame__(self, frame, meta, fd):
        print("got frame", frame.shape)
        server = self.intercom_server_by_client_fd[fd]
        # here you would use your heavy neural net detector instance
        # and create a message with, for example, the bounding box coordinates
        obj = {
            "this is" : "a message"
        }
        # send a message to the correct client:
        server.pushObject(obj)


    def c__registerClientProcess(self,
            name = None,
            n_ringbuffer = None,
            width = None,
            height = None,
            ipc_index = None,
            intercom_ipc_index = None
        ):
        print("c__registerClientProcess called with", name, n_ringbuffer, width, height)
        client = ShmemRGBClient(
            name = name,
            n_ringbuffer = n_ringbuffer,
            width = width,
            height = height,
            mstimeout = self.mstimeout,
            verbose = False
        )
        eventfd = getEventFd(ipc_index)
        client.useEventFd(eventfd) # do not forget!
        # let's get a posix file descriptor, i.e. a plain integer:
        fd = eventfd.getFd()
        self.client_by_fd[fd] = client
        # establish a shmem channel for communicating the results back to the client process

        name = uuid.uuid1().hex
        intercom_pars = {
            "name"            :name,
            "n_ringbuffer"    :self.intercom_n_buffer,   # size of ring buffer
            "n_bytes"         :self.intercom_n_bytes,
        }
        eventfd = getEventFd(intercom_ipc_index)
        server = ShmemServer(**intercom_pars)
        server.useEventFd(eventfd)
        intercom_fd = eventfd.getFd()
        self.intercom_server_by_fd[intercom_fd] = server
        self.intercom_server_by_client_fd[fd] = server
        intercom_pars["ipc_index"] = intercom_ipc_index
        self.return_out__(intercom_pars) # return results to frontend


    def c__deregisterClientProcess(self,
            ipc_index = None,
            intercom_ipc_index = None
        ):
        fd = getFdFromIndex(ipc_index)
        try:
            self.client_by_fd.pop(fd)
            self.intercom_server_by_client_fd.pop(fd)
        except KeyError:
            print("c__deregisterClientProcess : no client at ipc_index", ipc_index)

        fd = getFdFromIndex(intercom_ipc_index)
        try:
            self.intercom_server_by_fd.pop(fd)
        except KeyError:
            print("c__deregisterClientProcess : no intercom client at ipc_index", intercom_ipc_index)


    # *** frontend ***

    def registerClientProcess(self, client_process):
        """
        - A client process has sharedmem channel for receiving RGB24 frames from libValkka c++ side
        - ..then the client process forwards that RGB24 frame (or a part of it) to this master process
        -  .. so the client process establishes it's own shared memory RGB24 server that is listened by the master process
        """
        if client_process in self.registered_clients:
            print("registerClientProcess: process already registered", client_process)
            return

        intercom_ipc_index = reserveIndex() # reserving eventFd always at the frontend
        pars = client_process.getRGB24ServerPars()
        pars["intercom_ipc_index"] = intercom_ipc_index
        self.sendMessageToBack(MessageObject( # tell master process to start listening to the RGB24 shmem server
            "registerClientProcess",
            **pars
        )) # TODO: we need a blocking call that can give a reply
        # as a reply, we receive the shmem server parameters we need to listen for result messages
        # tell client that it can start listening the shmem intercom channel
        intercom_pars = self.returnFromBack()
        print("registerClientProcess: backend returned with", intercom_pars)
        client_process.listenIntercom(**intercom_pars)
        self.registered_clients.append(client_process)


    def deregisterClientProcess(self, client_process):
        """Sends client's Shmem Server parameters to this process & 
        """
        try:
            self.registered_clients.remove(client_process)
        except ValueError:
            print("deregisterClientProcess: no such client process registered", client_process)
            return

        ipc_index = client_process.getRGB24ServerPars()["ipc_index"]
        intercom_ipc_index = client_process.intercom_ipc_index

        self.sendMessageToBack(MessageObject(
            "deregisterClientProcess",
            ipc_index = ipc_index,
            intercom_ipc_index = intercom_ipc_index
        ))
        


def test1():
    print("starting")
    p = MasterProcess()
    p.start()
    time.sleep(1)
    print("stopping")
    p.stop()
    print("bye!")


def test2():
    from skeleton.multiprocess.client import ClientProcess

    print("starting")
    p = MasterProcess()
    p.start()
    time.sleep(1)
    print("creating client process")
    client = ClientProcess()
    client.start()
    print("registering client process")
    p.registerClientProcess(client)
    print("deregistering client process")
    p.deregisterClientProcess(client)
    print("stopping client")
    client.stop()
    print("stopping")
    p.stop()
    print("bye!")


if __name__ == "__main__":
    # test1()
    test2()
