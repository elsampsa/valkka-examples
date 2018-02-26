"""
shmem_test.py : Stream decoded (bitmap) frames from a single rtsp camera to a python process

Copyright 2017, 2018 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    single_stream.py
@author  Sampsa Riikonen
@date    2017
@version 0.1
@brief   Stream decoded (bitmap) frames from a single rtsp camera to a python process
"""

import sys
import time
import multiprocessing
from valkka.valkka_core import *

shmem_name_tag="shmem_bridge"


def client():
  index_p =new_intp()
  isize_p =new_intp()
  
  rb=SharedMemRingBuffer(shmem_name_tag,10,30*1024*1024,False)
  
  print("Getting shmem buffers")
  shmem_list=[]
  for i in range(10):
    shmem_list.append(getNumpyShmem(rb,i))
  
  print("Reading shmem buffers")
  while(True):
    rb.clientPull(index_p, isize_p);
    index=intp_value(index_p); isize=intp_value(isize_p)
    print("Current index, size=",index,isize)
    print("Payload=",shmem_list[index][0:min(isize,10)])
    


class ValkkaContext:
  
  def __init__(self,stream_address):
    self.stream_address=stream_address


  def openValkka(self):
    """Creates thread instances, creates filter chain, starts threads
    
    So, you've learned from
    
    https://elsampsa.github.io/valkka-core/html/process_chart.html
    
    that:
    
    * Concatenating FrameFilters, creates a callback cascade
    * Threads write to a FrameFilter
    * Threads read from a FrameFifo
    * FrameFifos have an internal stack of pre-reserved frames
    * Threads are not python threads, so there are no global intepreter lock (GIL) problems in this code
    
    The filtergraph (**) for this case:
    
    (LiveThread:livethread) --> {InfoFrameFilter:live_out_filter} --> {FifoFrameFilter:av_in_filter} --> [FrameFifo:av_fifo] -->> (AVThread:avthread) --> {SwsScaleFrameFilter:sws_scale_filter} --> {SharedMemFrameFilter:shmem_filter}
    """
    
    self.livethread      =LiveThread         ("livethread", # name 
                                              0,            # size of input fifo
                                              -1            # thread affinity: -1 = no affinity, n = id of processor where the thread is bound
                                              )
    """
    Start constructing the filter chain.  Follow the filtergraph (**) from end to beginning.
    """
    # reserve 10 frames, 30 MB each
    self.shmem_filter   =SharedMemFrameFilter (shmem_name_tag,10,30*1024*1024)
    # SharedMemFrameFilter instantiates the server side of shmem bridge
    # in a separate process do:
    # rb=SharedMemRingBuffer(shmem_name_tag,10,30*1024*1024,False) # shmem ring buffer on the client side
    
    self.sws_scale_filter=SwsScaleFrameFilter ("sws_scale",self.shmem_filter)
    
    self.av_fifo         =FrameFifo          ("av_fifo",10)        # FrameFifo is 10 frames long.  Payloads in the frames adapt automatically to the streamed data.
    
    # [av_fifo] -->> (avthread) --> {gl_in_filter}
    self.avthread        =AVThread           ("avthread",              # name    
                                              self.av_fifo,            # read from
                                              self.sws_scale_filter,   # write to
                                              -1                       # thread affinity: -1 = no affinity, n = id of processor where the thread is bound
                                              ) 
    
    self.av_in_filter    =FifoFrameFilter    ("av_in_filter",   self.av_fifo)
    self.live_out_filter =InfoFrameFilter    ("live_out_filter",self.av_in_filter)
    
    # Start all threads
    self.livethread.startCall()
    self.avthread  .startCall()


  def closeValkka(self):
    """Stop all valkka threads
    """
    self.avthread  .stopCall()
    self.livethread.stopCall()
    

  def start_streams(self):
    print("start decoding")
    self.avthread.decodingOnCall() # signal AVThread that it may start decoding

    # define stream source, how the stream is passed on, etc.
    self.ctx=LiveConnectionContext()
    self.ctx.slot=1                                  # slot number identifies the stream source
    self.ctx.connection_type=LiveConnectionType_rtsp # this is an rtsp connection
    self.ctx.address=self.stream_address             # stream address, i.e. "rtsp://.."
    self.ctx.framefilter=self.live_out_filter        # where the received frames are written to.  See filterchain (**)
    self.ctx.msreconnect=0                           # do not attemp to reconnect of the stream dies out
        
    # send the information about the stream to LiveThread
    print("registering stream")
    self.livethread.registerStreamCall(self.ctx)
    
    # request frames from the stream
    print("playing stream !")
    self.livethread.playStreamCall(self.ctx)
    
    
  def stop_streams(self):
    print("stopping streams")
    self.avthread.decodingOffCall()
    
    
    
def main():
  if (len(sys.argv)<2):
    print("Give rtsp stream address, i.e. rtsp://passwd:user@ip")
    return

  vc=ValkkaContext(sys.argv[1])
  vc.openValkka()
  
  p=multiprocessing.Process(target=client) # create a multiprocess that runs method "client"
  p.start()
  # .. so, here we have forked a multiprocess.  You could also start method "client" from a completely independent process
  
  vc.start_streams()
  time.sleep(10)
  vc.stop_streams()
  vc.closeValkka()
  
  p.stop()


if (__name__=="__main__"):
  main()

  
