"""
shmem_test_decoded.py : Stream decoded (bitmap) frames from a single rtsp camera.  Share the bitmap between python processes.

Copyright 2017, 2018 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    shmem_test_decoded.py
@author  Sampsa Riikonen
@date    2017
@version 1.0.1 
@brief   Stream decoded (bitmap) frames from a single rtsp camera.  Share the bitmap between python processes.
"""

import sys
import time
import multiprocessing
from valkka.core import *

shmem_name_tag="shmem_bridge"


def client(stop_event):
  index_p =new_intp()
  isize_p =new_intp()
  
  rb=SharedMemRingBuffer(shmem_name_tag,10,30*1024*1024,1000,False) # name, cells, bytes, mstimeout, not server
  
  print("Getting shmem buffers")
  shmem_list=[]
  for i in range(10):
    shmem_list.append(getNumpyShmem(rb,i))
  
  print("Reading shmem buffers")
  while(True):
    ok=rb.clientPull(index_p, isize_p);
    if ok:
      index=intp_value(index_p); isize=intp_value(isize_p)
      print("Current index, size=",index,isize)
      print("Payload=",shmem_list[index][0:min(isize,10)])
    else:
      print("Semaphore timed out")
    if (stop_event.is_set()): break


class ValkkaContext:
  
  def __init__(self,stream_address):
    self.stream_address=stream_address


  def openValkka(self):
    """Creates thread instances, creates filter chain, starts threads
    
    filtergraph:
    
    (LiveThread:livethread) --> {InfoFrameFilter:live_out_filter} -->> (AVThread:avthread) --> {SwsScaleFrameFilter:sws_scale_filter} --> {RGBShmemFrameFilter:shmem_filter}
    """
    # construct filtergraph from right to the left
    
    # reserve 10 frames for 300x300 pixel images.  Semaphore timeout is 1000 ms
    self.shmem_filter    =RGBShmemFrameFilter(shmem_name_tag, 10, 300, 300, 1000)
    
    # SharedMemFrameFilter instantiates the server side of shmem bridge
    # in a separate process do:
    # rb=SharedMemRingBuffer(shmem_name_tag,10,30*1024*1024,False) # shmem ring buffer on the client side
    self.sws_scale_filter=SwScaleFrameFilter(shmem_name_tag, 300, 300, self.shmem_filter)
    
    self.avthread        =AVThread        ("avthread",self.sws_scale_filter)    
    self.live_out_filter =InfoFrameFilter ("live_out_filter",self.avthread.getFrameFilter()) # request input framefilter from AVThread
    self.livethread      =LiveThread      ("livethread")
    
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
  
  ev=multiprocessing.Event()
  p=multiprocessing.Process(target=client,args=(ev,)) # create a multiprocess that runs method "client"
  p.start()
  # .. so, here we have forked a multiprocess.  You could also start method "client" from a completely independent process
  
  vc.start_streams()
  time.sleep(5)
  vc.stop_streams()
  vc.closeValkka()
  print("valkka threads closed")
  ev.set()
  print("client process exit requested")


if (__name__=="__main__"):
  main()

  
