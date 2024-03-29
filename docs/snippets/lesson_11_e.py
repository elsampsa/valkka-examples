#<hide>
"""
filtergraph:                                                             
                                                                         
(ValkkaFSWriterThread:readerthread) -->> (FileCacheThread:cacherthread) --> {InfoFrameFilter:out_filter}
                                                     |
                                                     $ 
                                       setPyCallback  : [int] current mstime, freq: 500 ms
                                       setPyCallback2 : [tuple] (min mstimestamp, max mstimestamp)
"""
#</hide>

"""<rtf>
Same imports as before:
<rtf>"""
import time, sys
from valkka.core import *
from valkka.api2 import loglevel_debug, loglevel_normal
from valkka.fs import ValkkaSingleFS

setLogLevel_filelogger(loglevel_debug)

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

Filterchain is going to look like this:

::

    (ValkkaFSReaderThread:readerthread) -->> (FileCacheThread:cacherthread) --> {InfoFrameFilter:out_filter}
                                                     |
                                                     $ 
                                       setPyCallback  : [int] current mstime, freq: 500 ms
                                       setPyCallback2 : [tuple] (min mstimestamp, max mstimestamp)

As you can see, where have introduced new notation here.

**$** designates callbacks that are used by FileCacheThread.  It's up to you to define the python code in these callbacks.  The callbacks are registered by using the *setPyCallback* and *setPyCallback2* methods.

Next, we proceed in constructing the filterchain in end-to-beginning order.

ValkkaFSReaderThread will write all it's frames into FileCacheThread's input FrameFilter.
<rtf>"""
out_filter   = InfoFrameFilter("out_filter") # will be registered later with cacherthread
cacherthread = FileCacheThread("cacher")
readerthread = ValkkaFSReaderThread("reader", valkkafs.core, cacherthread.getFrameFilter()) # ValkkaFSReaderThread => FileCacheThread

"""<rtf>
Next, define callbacks for FileCacheThread

Define a global variable: a tuple that holds the min and max millisecond timestamps of cached frames:
<rtf>"""
current_time_limits = None

"""<rtf>
This following function will be called frequently by FileCacheThread to inform us about the current millisecond timestamp:
<rtf>"""
def current_time_callback(mstime: int):
    global current_time_limits
    try:
        print("current time", mstime)
        if current_time_limits is None:
            return
        
        if mstime >= current_time_limits[1]:
            print("current time over cached time limits!")
            # cacherthread.rewindCall() # TODO
            # # or alternatively, handle the situation as you please
            # # .. for example, request more blocks:
            # readerthread.pullBlocksPyCall(your_list_of_blocks)
            pass
            
    except Exception as e:
        print("current_time_callback failed with ", str(e))
        return

"""<rtf>
The next callback is evoked when FileCacheThread receives new frames for caching.  It informs us about the minimum and maximum millisecond timestamps:
<rtf>"""
def time_limits_callback(times: tuple):
    global current_time_limits
    try:
        print("new time limits", times)
        current_time_limits = times
        
    except Exception as e:
        print("time_limits_callback failed with ", str(e))
        return

"""<rtf>
The callbacks should be kept ASAP (as-simple-as-possible) and return immediately.  You also might wan't them to send a Qt signal in your GUI application.

Typically, they should use only the following methods of the libValkka API:

::

    valkka.fs.ValkkaSingleFS
                        .getBlockTable
                        .getTimeRange
                        
    valkka.core.ValkkaFSReaderThread
                        .pullBlocksPyCall
                        

Register the callbacks into the FileCacheThread
<rtf>"""
cacherthread.setPyCallback(current_time_callback)
cacherthread.setPyCallback2(time_limits_callback)

"""<rtf>
Start the threads
<rtf>"""
cacherthread.startCall()
readerthread.startCall()

"""<rtf>
Frames saved with id number 925412 to ValkkaFS are mapped into slot number 1:
<rtf>"""
readerthread.setSlotIdCall(1, 925412)

"""<rtf>
FileCacheThread will write frames with slot number 1 into InfoFrameFilter:
<rtf>"""
ctx = FileStreamContext(1, out_filter)
cacherthread.registerStreamCall(ctx)

"""<rtf>
Request blocks 0-4 from the reader thread.  The frames will be cached by FileCacheThread.
<rtf>"""
readerthread.pullBlocksPyCall([0,1,3,4])

"""<rtf>
Before frames can be played, a seek must be performed to set a time reference.
<rtf>"""
mstimestamp = int(a[1,0]) # take the first timestamp from the blocktable.  Use int() to convert to normal python integer.
print("seeking to", mstimestamp)
cacherthread.seekStreamsCall(mstimestamp)

"""<rtf>
It's up to the API user to assure that the used mstimestamp is within the correct limits (i.e. requested blocks).

Next, let the stream play for 10 seconds
<rtf>"""
cacherthread.playStreamsCall()
time.sleep(10)

"""<rtf>
Stop threads
<rtf>"""
cacherthread.stopCall()
readerthread.stopCall()

print("bye")

