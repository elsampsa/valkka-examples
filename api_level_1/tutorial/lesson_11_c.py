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
Instantiate ValkkaFSTool that allows us to peek into the written data
<rtf>"""
tool = ValkkaFSTool(valkkafs.core)

"""<rtf>
Contents of individual blocks can now be inspected like this:
<rtf>"""
tool.dumpBlock(0)
tool.dumpBlock(1)

"""<rtf>

You'll get output like this:

::

    ----- Block number : 0 -----
    [925412] <BasicFrame: timestamp=1543314164986 subsession_index=0 slot=0 / payload size=29 / H264: slice_type=7> *     0 0 0 1 103 100 0 31 172 17 22 160 80 5 186 16 0 1 25 64 
    [925412] <BasicFrame: timestamp=1543314164986 subsession_index=0 slot=0 / payload size=8 / H264: slice_type=8>    0 0 0 1 104 238 56 176 
    [925412] <BasicFrame: timestamp=1543314165135 subsession_index=0 slot=0 / payload size=32 / H264: slice_type=7> *     0 0 0 1 103 100 0 31 172 17 22 160 80 5 186 16 0 1 25 64 
    [925412] <BasicFrame: timestamp=1543314165135 subsession_index=0 slot=0 / payload size=8 / H264: slice_type=8>    0 0 0 1 104 238 56 176 
    [925412] <BasicFrame: timestamp=1543314165135 subsession_index=0 slot=0 / payload size=19460 / H264: slice_type=5>    0 0 0 1 101 136 128 8 0 1 191 180 142 114 29 255 192 79 52 19 
    [925412] <BasicFrame: timestamp=1543314165215 subsession_index=0 slot=0 / payload size=32 / H264: slice_type=7> *     0 0 0 1 103 100 0 31 172 17 22 160 80 5 186 16 0 1 25 64 
    [925412] <BasicFrame: timestamp=1543314165215 subsession_index=0 slot=0 / payload size=8 / H264: slice_type=8>    0 0 0 1 104 238 56 176 
    [925412] <BasicFrame: timestamp=1543314165215 subsession_index=0 slot=0 / payload size=19408 / H264: slice_type=5>    0 0 0 1 101 136 128 8 0 1 191 180 142 114 29 255 193 80 200 71 
    [925412] <BasicFrame: timestamp=1543314165335 subsession_index=0 slot=0 / payload size=4928 / H264: slice_type=1>    0 0 0 1 65 154 0 64 2 19 127 208 117 223 181 129 22 206 32 84 
    ...

Frame id number is indicated in the first column.  Asterix (*) marks the seek points.  In the final rows, first few bytes of the actual payload are shown.
<rtf>"""

"""<rtf>
Let's see the min and max time of frames written in this ValkkaFS
<rtf>"""
(t0, t1) = valkkafs.getTimeRange()
print("Min and Max time in milliseconds:", t0, t1)

"""<rtf>
These are milliseconds, so to get *struct_time* object we need to do this:
<rtf>"""
print("Min time:", time.gmtime(t0/1000))
print("Max time:", time.gmtime(t1/1000))

"""<rtf>
Block numbers corresponding to a certain time range can be searched like this:
<rtf>"""
req = (t0, t1)
block_indices = valkkafs.getInd(req)
print("Block indices =", block_indices)

"""<rtf>
Now you could pass to indices to the ValkkaFSReaderThread method **pullBlocksPyCall** to recover all frames from that time interval.

Another usefull method is *getIndNeigh*.  It returns blocks from the neighborhood of a certain target time:
<rtf>"""
req = (t1+t0)//2
block_indices = valkkafs.getIndNeigh(n=2, time=req)
print("Block indices =", block_indices)

"""<rtf>
That will return the target block plus two blocks surrounding it.  

You would call this method when a user requests a seek to a certain time and you want to be sure that there are enough frames surrounding that time instant
<rtf>"""
