import traceback
from multiprocessing import Event

"""Create a group of Events (EventGroup) and a context manager (SyncIndex) to wait
in the main python process for operation completion in the multiprocessing backend 
(i.e. "on the other side" of the fork)

At your main python process' ctor, do this:

::

    def __init__(self, ...):
        ...
        self.eg = EventGroup(20)
        ...


In your main python process (aka "multiprocessing frontend"), you can now do this:

::

    with SyncIndex(self.eg) as i:
        # send some message to the backend, communicating
        # the index i therein
        # this section waits until the event corresponding
        # to i has been set by the backend


In the other side of the fork (aka "multiprocessing backend"), do this:

::

    # backend has been given the index i
    # does the blocking operation, and after that call this:
    self.eg.set(i)

"""


class NotEnoughEvents(BaseException):
    pass


class EventGroup:

    def __init__(self, n):
        self.events = []
        self.events_index = []
        for i in range(n):
            self.events.append(Event())
            self.events_index.append(i)

    def __str__(self):
        st = "<EventGroup: "
        for i in range(len(self.events)):
            if i in self.events_index:
                st += "f"+str(i)+" "
            else:
                st += "R"+str(i)+" "
        st += ">"
        return st

    def __len__(self):
        return len(self.events)

    
    def set(self, i):
        self.events[i].set()


class SyncIndex:

    def __init__(self, event_group: EventGroup):
        self.eg = event_group
        self.i = None

    def __enter__(self):
        try:
            self.i = self.eg.events_index.pop(0) # reserve an avail event as per index
        except IndexError:
            raise(NotEnoughEvents("init your event group with more events"))
        self.eg.events[self.i].clear() # clear the event before usage
        return self.i

    def __exit__(self, type, value, tb):
        if tb:
            print("SyncIndex failed with:")
            traceback.print_tb(tb)
        self.eg.events[self.i].wait() # wait until the event has been set
        # ..typically on the multiprocess backend
        self.eg.events_index.insert(0, self.i) # recycle the event

    """
    # async part: TODO
    # for cases when we have async _frontend_
    # (that case has not yet been considered/implemented)
    # with async backend, EventGroup & SyncIndex should work as
    # in the sync backend case

    async def __aenter__(self):
         return self.__enter__()

    async def __aexit__(self, exc_type, exc, tb):
        await self.client.quit()
    """



def main():
    # raise(NotEnoughEvents)
    # eg = EventGroup(0)
    eg = EventGroup(1)
    with SyncIndex(eg) as i:
        print("waiting ", i)
        print(eg)
        # kokkelis

if __name__ == "__main__":
    main()

