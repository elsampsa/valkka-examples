import time, sys, asyncio, copy
from valkka.multiprocess import MessageProcess, AsyncBackMessageProcess,\
    MessageObject, safe_select
from valkka.api2 import FragMP4ShmemClient
from skeleton.singleton import getEventFd, reserveIndex
"""NOTE:
Never call reserveEventFd / releaseEventFd from a child multiprocess
eventfd file-descriptors are maintained by the main process
"""


class FragMP4Process(AsyncBackMessageProcess):
    """This class implements the frontend/backend model of multiprocessing (not to be confused with web-apps!)

    ::

        Backend methods (designated with __ or with c__) <=PIPE=> Frontend methods
          Backend reads the pipe and multiplexes                    You just call these
          also any other communication channels                     from your python main process


    Backend is _the_ multiprocess running in its own virtual memory space, isolated from the rest of the processes.

    Intercommunication is handled under-the-hood, making life easier for the API programmer that just calls Frontend methods.

    Backend method can be "normal" or asynchronous python

    In this example we have normal frontend & asynchronous backend

    Some tips for creating your websocket server in the backend

    - Start a websocket server in asyncPre__
    - ..or in c__customCall
    - When your websocket server receives a request 
    for a video channel, launch activateClient__

    """

    def __init__(self, mstimeout = 1000):
        super().__init__()
        self.mstimeout = mstimeout

    """BACKEND methods

    Never call these methods from the main python process: they are internal for the backend
    """

    def preRun__(self):
        """Do variable initialization etc. before the async execution starts
        """    
        print("preRun__")
        self.client_by_fd = {}
        self.shmem_pars_by_slot = {}


    def postRun__(self):
        """Last thing executed before multiprocess exits
        """
        print("postRun__")


    async def asyncPre__(self):
        """First thing executed in the async event loop
        """
        print("asyncPre__")


    async def asyncPost__(self):
        """This is the final thing executed in the asynchronous event loop before process exit
        """
        print("asyncPost__")
        self.client_by_fd = {}


    async def c__activateFMP4Client(self, 
            name = None, 
            n_ringbuffer = None, 
            n_size = None,
            ipc_index = None
            ):
        """This will activate a shared memory client that reads the frag-mp4 fragments
        from shared memory
        """
        try:
            print("activateFMP4Client__: ", name, n_ringbuffer, n_size, ipc_index)
            client = FragMP4ShmemClient(
                name = name,
                n_ringbuffer = n_ringbuffer,
                n_size = n_size,
                mstimeout = self.mstimeout
            )
            eventfd = getEventFd(ipc_index)
            # let's get a posix file descriptor, i.e. a plain integer:
            fd = eventfd.getFd()
            self.client_by_fd[fd] = client
            # tell asyncio to listen to a file-descriptor and 
            # launch a callback when that file-descriptor triggers
            asyncio.get_event_loop().add_reader(fd, self.fmp4callback__, fd)
            # .. that callback must be normal (not asyncio) python
            # finally, let's send a message to the main python process:
        except Exception as e:
            print("activateFMP4Client__: failed with", e)
            raise


    async def c__deactivateFMP4Client(self,
        ipc_index = None):
        eventfd = getEventFd(ipc_index)
        fd = eventfd.getFd()
        try:
            self.client_by_fd.pop(fd)
        except KeyError:
            print("deactivateFMP4Client__ : no client at ipc_index", ipc_index)
            raise
    

    def fmp4callback__(self, fd):
        """NOTE:
        - "normal" (i.e. not asyncio) python
        - use only non-blocking calls!
        """
        client = self.client_by_fd[fd]
        index, meta = client.pullFrame()
        if (index == None):
            print("frag-mp4 client timeout")
        else:
            print("got fmp4 fragment of size", meta.size)
            print("of type", meta.name)
            data = client.shmem_list[index][0:meta.size]
            """
            ..thats a numpy array of your fmp4 fragment

            Food for thought:
            
            - place that fragment (and metadata) into an asyncio.Queue
            - ..which can then be read by a task (maybe one per video stream)
            """

    # commands that come from the main python process (aka frontend)

    async def c__customCall(self, parameter = 1):
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

    def activateFMP4Client(self,
        name = None, 
        n_ringbuffer = None, 
        n_size = None,
        ipc_index = None
        ):
        self.sendMessageToBack(MessageObject(
            "activateFMP4Client",
            name = name, 
            n_ringbuffer = n_ringbuffer, 
            n_size = n_size,
            ipc_index = ipc_index
        ))
        # that intercommunicates with backend and looks
        # for method "c__activateMP4Client" there in
        # in a more realistic application, fmp4 clients
        # are activated, based on the websocket server
        # callbacks (as client connects to your websocket server)
        # in the backend only


    def deactivateFMP4Client(self, ipc_index = None):
        self.sendMessageToBack(MessageObject(
            "deactivateFMP4Client",
            ipc_index = ipc_index
        ))


    def customCall(self, parameter = 1):
        # your demo custom call :)
        self.sendMessageToBack(MessageObject(
            "customCall",
            parameter = parameter
        ))
        # that intercommunicates with backend and looks
        # for method "c__customCall" there in



def main():
    """A trivial test
    """
    p = FragMP4Process()
    p.start()
    time.sleep(1)
    print("activate")
    ipc_index = reserveIndex()
    p.activateFMP4Client(
        name = "kokkelis",
        n_ringbuffer = 10,
        n_size = 1024*1024,
        ipc_index = ipc_index
    )
    time.sleep(1)
    p.deactivateFMP4Client(
        ipc_index = ipc_index
    )
    time.sleep(1)
    print("exiting")
    p.stop()


if __name__ == "__main__":
    main()
 
