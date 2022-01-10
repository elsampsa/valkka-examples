#<hide>
"""
filtergraph:

(ValkkaFSWriterThread:readerthread) -> {InfoFrameFilter:out_filter}
"""
#</hide>

"""<rtf>
Same imports as before:
<rtf>"""
import time, sys
from valkka.core import *
from valkka.fs import ValkkaSingleFS

"""<rtf>
Load ValkkaFS metadata:
<rtf>"""
valkkafs = ValkkaSingleFS.loadFromDirectory(dirname="/tmp/testvalkkafs")

"""<rtf>
Let's take a look at the blocktable:
<rtf>"""
a = valkkafs.getBlockTable()
print(a)

"""<rtf>
Construct the filterchain: write from the reader thread into the verbose InfoFrameFilter
<rtf>"""
out_filter =InfoFrameFilter("reader_out_filter")
readerthread = ValkkaFSReaderThread("reader", valkkafs.core, out_filter)

"""<rtf>
Start the reader thread:
<rtf>"""
readerthread.startCall()

"""<rtf>
Frames with id number 925412 are mapped into slot 1:
<rtf>"""
readerthread.setSlotIdCall(1, 925412)

"""<rtf>
Request blocks 0, 1 from the reader thread.  Information of frames from these blocks are dumped on the terminal
<rtf>"""
readerthread.pullBlocksPyCall([0,1])
time.sleep(1)

"""<rtf>
Exit the thread:
<rtf>"""
readerthread.stopCall()
print("bye")
