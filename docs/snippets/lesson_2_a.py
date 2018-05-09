#<hide>
"""
filtergraph:

Streaming part               | Decoding part
                             |
(LiveThread:livethread) -->> (AVThread:avthread) --> {InfoFrameFilter:info_filter}
"""
#</hide>
#<hide>
import time
from valkka.valkka_core import *
#</hide>
"""<rtf>
Let's consider the following filtergraph:

::

    Streaming part               | Decoding part
                                 |
    (LiveThread:livethread) -->> (AVThread:avthread) --> {InfoFrameFilter:info_filter}
    
    
Like in the previous lessons, we are reading frames from an IP camera.  Instead of churning them through a series of filters, we pass them to another, independently running thread that performs decoding (AVThread).

Let's list all the symbols used until now and the corresponding objects:

====== ============ ==================================
Symbol Base class   Explanation
====== ============ ==================================
()     Thread       An independently running thread
>>                  Crossover between two threads
{}     FrameFilter  A framefilter
====== ============ ==================================

That's all you need to create complex filtergraphs with Valkka.

We start as usual, by constructing the filterchain from end-to-beginning:
<rtf>"""
# decoding part
info_filter     =InfoFrameFilter("info_filter")
avthread        =AVThread("avthread",info_filter)

"""<rtf>
We need a framefilter to feed the frames into AVThread.  This framefilter is requested from the AVThread itself:
<rtf>"""
# streaming part
av_in_filter    =avthread.getFrameFilter()
livethread      =LiveThread("livethread")

"""<rtf>
Finally, proceed as before: pass *av_in_filter* as a parameter to the connection context, start threads, etc.
<rtf>"""                                              
ctx =LiveConnectionContext(LiveConnectionType_rtsp, "rtsp://admin:nordic12345@192.168.1.41", 1, av_in_filter)

"""<rtf>
Start threads
<rtf>"""
avthread.startCall()
livethread.startCall()

# start decoding
avthread.decodingOnCall()

livethread.registerStreamCall(ctx)
livethread.playStreamCall(ctx)
time.sleep(5)

# stop decoding
# avthread.decodingOffCall()

"""<rtf>
Stop threads
<rtf>"""
livethread.stopCall()
avthread.stopCall()

print("bye")


"""<rtf>
You will see output like this:

::

    InfoFrameFilter: info_filter start dump>> 
    InfoFrameFilter: FRAME   : <AVBitmapFrame: timestamp=1525870759898 subsession_index=0 slot=1 / h=1080; w=1920; l=(1920,960,960); f=12>
    InfoFrameFilter: PAYLOAD : [47 47 47 47 47 47 47 47 47 47 ]
    InfoFrameFilter: timediff: -22
    InfoFrameFilter: info_filter <<end dump   
    InfoFrameFilter: info_filter start dump>> 
    InfoFrameFilter: FRAME   : <AVBitmapFrame: timestamp=1525870759938 subsession_index=0 slot=1 / h=1080; w=1920; l=(1920,960,960); f=12>
    InfoFrameFilter: PAYLOAD : [47 47 47 47 47 47 47 47 47 47 ]
    InfoFrameFilter: timediff: -11
    InfoFrameFilter: info_filter <<end dump   
    ...
    ...
    

So, instead of H264 packets, we have decoded bitmap frames here.

In the next lesson, we'll dump them on the screen.
<rtf>"""

