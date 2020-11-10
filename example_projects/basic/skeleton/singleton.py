"""This is a global singleton module that must be imported in the very beginning 
by any other module that wishes to do multiprocess intercommunication.

This way the interprocess-communication (ipc) file descriptors are visible 
to all multiprocesses.

File descriptors allow you to multiplex several frame sources at a single process.  
For multiplexing file descriptors, see this: https://docs.python.org/3/howto/sockets.html

Never call reserveEventFd / releaseEventFd 
from a multiprocess backend as the eventfd file-descriptors 
are maintained by the main python process
(calling them from the multiprocess frontend is ok)
"""

from valkka import core

n = 100 # add more if you really need to
events = []
events_index = []

for i in range(n):
    events.append(core.EventFd())
    #
    # core.EventFd encapsulates an event file descriptor:
    #
    # https://linux.die.net/man/2/eventfd
    # 
    # EventFd has method getFd that returns the numerical value of
    # the file descriptor
    events_index.append(i)

def reserveEventFd():
    global events_index, events
    i = events_index.pop(0)
    return events[i]

def releaseEventFd(eventfd):
    global events_index, events
    i = events.index(eventfd)
    events_index.insert(0, i)
    
def getEventFd(index):
    global events
    return events[index]

def eventFdToIndex(eventfd):
    global events
    i = events.index(eventfd)
    return i

def reserveIndex():
    # reserve eventfd and return directly as an index
    eventfd = reserveEventFd()
    return eventFdToIndex(eventfd)

def getFdFromIndex(index):
    eventfd = getEventFd(index)
    return eventfd.getFd()
