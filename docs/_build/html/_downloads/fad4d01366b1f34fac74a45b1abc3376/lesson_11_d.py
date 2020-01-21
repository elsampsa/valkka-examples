#<hide>
"""
filtergraph:                                                              +--> ...
                                                                          |
(ValkkaFSWriterThread:readerthread) --> {ForkFrameFilterN:fork_filter} ---+
main branch                                                               |
                                                                          +--> branch 1

branch 1 : {PassSlotFrameFilter:slot_filter} --> {InitStreamFrameFilter:init_stream} --> {FileFrameFilter:file_filter} --> output file
"""
#</hide>

"""<rtf>
Same imports as before:
<rtf>"""
import time
from valkka.core import *
from valkka.api2 import ValkkaFS, loglevel_debug, loglevel_normal

setLogLevel_filelogger(loglevel_debug)

"""<rtf>
Load ValkkaFS metadata:
<rtf>"""
valkkafs = ValkkaFS.loadFromDirectory(dirname="/home/sampsa/tmp/testvalkkafs")

"""<rtf>
Let's take a look at the blocktable:
<rtf>"""
a = valkkafs.getBlockTable()
print(a[:,0:10])

"""<rtf>
Next, construct the filterchain.  It looks like this:

::

                                                                              +--> ...
    main branch                                                               |
    (ValkkaFSWriterThread:readerthread) --> {ForkFrameFilterN:fork_filter} ---+
                                                                              |
                                                                              +--> branch 1

    branch 1 : {PassSlotFrameFilter:slot_filter} --> {InitStreamFrameFilter:init_stream} --> {FileFrameFilter:file_filter} --> output file
    
    
Here we have introduced yet another FrameFilter that performs forking.  An arbitrary number of terminals can be connected to **ForkFrameFilterN**.  Terminals can be connected and disconnected also while threads are running. 

The PassSlotFrameFilter passes frames with a certain slot number as we want frames only from a single stream to the final output file.
<rtf>"""

# main branch
fork_filter = ForkFrameFilterN("fork")
readerthread = ValkkaFSReaderThread("reader", valkkafs.core, fork_filter)

# branch 1
file_filter = FileFrameFilter("file_filter")
init_stream = InitStreamFrameFilter("init_filter", file_filter)
slot_filter = PassSlotFrameFilter("", 1, init_stream)

# connect branch 1
fork_filter.connect("info", slot_filter)

# activate file write
file_filter.activate("kokkelis.mkv")

"""<rtf>
Start the reader thread:
<rtf>"""
readerthread.startCall()

"""<rtf>
Frames with id number 925412 are mapped into slot 1:
<rtf>"""
readerthread.setSlotIdCall(1, 925412)

"""<rtf>
Request blocks 0-4 from the reader thread.  Information of frames from these blocks are dumped on the terminal
<rtf>"""
readerthread.pullBlocksPyCall([0,1,3,4])
time.sleep(1)

"""<rtf>
Exit the thread:
<rtf>"""
readerthread.stopCall()
print("bye")

