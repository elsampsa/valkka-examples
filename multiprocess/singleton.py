from valkka.core import EventFd
from valkka.multiprocess.sync import EventGroup
from multiprocessing import Lock

event_fd_group_1 = EventGroup(100, EventFd) # unix file descriptors to sync between SHMEM SERVER and CLIENT
