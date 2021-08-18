"""A global singleton module with synchronization primitives visible for all forked multiprocesses
"""
from demo_sync import EventFdGroup

event_fd_group_1 = EventFdGroup(100)
