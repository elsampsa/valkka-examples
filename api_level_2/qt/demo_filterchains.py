"""
demo_filterchains.py : Some custom filterchains for Valkka Python3 examples

Copyright 2018 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    demo_filterchains.py
@author  Sampsa Riikonen
@date    2018
@version 0.5.3 
@brief   
"""
import sys
import time
import random
from valkka import valkka_core as core # so, everything that has .core, refers to the api1 level (i.e. swig wrapped cpp code)
from valkka.api2.threads import LiveThread, OpenGLThread # api2 versions of the thread classes
from valkka.api2.tools import parameterInitCheck, typeCheck
pre_mod="filterchains: "


class MulticastFilterchain:
  """This class implements the following filterchain:
  
  ::
                                            branch 1: bitmap to screen
    (LiveThread:livethread)                 +--->> (AVThread:avthread) -->> (OpenGLThread:glthread)
              |                             |
              |                             |
              +--->> {ForkFrameFilter:fork} +
                                            |
                                            |
                                            +-->> (LiveThread:livethread2) 
                                            branch 2: multicast 
  """
  
  parameter_defs={
    "incoming_livethread"  : LiveThread,
    "outgoing_livethread"  : LiveThread,
    "openglthread" : OpenGLThread,
    "address"      : str,
    "slot"         : int,
    
    "multicast_address" : (str,""),
    "multicast_port"    : (int,0),
    
    # these are for the AVThread instance:
    "n_basic"      : (int,20), # number of payload frames in the stack
    "n_setup"      : (int,20), # number of setup frames in the stack
    "n_signal"     : (int,20), # number of signal frames in the stack
    "flush_when_full" : (bool, False), # clear fifo at overflow
    
    "affinity"     : (int,-1),
    "verbose"      : (bool,False),
    "msreconnect"  : (int,0)
    }
  
  
  def __init__(self, **kwargs):
    self.pre=self.__class__.__name__+" : " # auxiliary string for debugging output
    parameterInitCheck(self.parameter_defs,kwargs,self) # check for input parameters, attach them to this instance as attributes
    self.init()
    
    
  def init(self):
    self.idst=str(id(self))
    self.makeChain()
    self.createContext()
    self.createOutputContext()
    self.startThreads()
    self.active=True
    
    
  def __del__(self):
    self.close()
    
    
  def close(self):
    if (self.active):
      if (self.verbose):
        print(self.pre,"Closing threads and contexes")
      self.decodingOff()
      self.closeContext()
      self.stopThreads()
      self.active=False
    
    
  def makeChain(self):
    """Create the filter chain
    """
    # branch 1
    self.gl_in_filter  =self.openglthread.getInput() # get input FrameFilter from OpenGLThread
    
    self.framefifo_ctx=core.FrameFifoContext()
    self.framefifo_ctx.n_basic           =self.n_basic
    self.framefifo_ctx.n_setup           =self.n_setup
    self.framefifo_ctx.n_signal          =self.n_signal
    self.framefifo_ctx.flush_when_full   =self.flush_when_full
    
    self.avthread      =core.AVThread("avthread_"+self.idst, self.gl_in_filter, self.framefifo_ctx)
    self.avthread.setAffinity(self.affinity)
    self.av_in_filter  =self.avthread.getFrameFilter() # get input FrameFilter from AVThread

    # branch 2
    self.live_out_filter =self.outgoing_livethread.core.getFrameFilter() # writing here writes to outgoing_livethread
    
    # fork
    self.fork =core.ForkFrameFilter("fork",self.av_in_filter,self.live_out_filter) # this one is used by incoming_livethread
    

  def createContext(self):
    """Creates a LiveConnectionContext and registers it to LiveThread.
    """
    # define stream source, how the stream is passed on, etc.
    
    self.ctx=core.LiveConnectionContext()
    self.ctx.slot=self.slot                          # slot number identifies the stream source
    
    if (self.address.find("rtsp://")==0):
      self.ctx.connection_type=core.LiveConnectionType_rtsp
    else:
      self.ctx.connection_type=core.LiveConnectionType_sdp # this is an rtsp connection
    
    self.ctx.address=self.address         
    # stream address, i.e. "rtsp://.."
    
    self.ctx.framefilter=self.fork
    
    self.ctx.msreconnect=self.msreconnect
    
    # send the information about the stream to LiveThread
    self.incoming_livethread.registerStream(self.ctx)
    self.incoming_livethread.playStream(self.ctx)


  def createOutputContext(self):
    """Creates an output context for sending the stream
    """
    if (self.multicast_address!="" and self.multicast_port>0):
      self.out_ctx =core.LiveOutboundContext(core.LiveConnectionType_sdp, self.multicast_address, self.slot, self.multicast_port)
      self.outgoing_livethread.core.registerOutboundCall(self.out_ctx) # TODO: move registering outbound streams to API level 2
    

  def closeContext(self):
    self.outgoing_livethread.stopStream(self.ctx)
    self.outgoing_livethread.deregisterStream(self.ctx)
    
    
  def closeOutboundContext(self):
    if (self.multicast_address!="" and self.multicast_port>0):
      self.outgoing_livethread.core.deregisterOutboundCall(self.out_ctx) # TODO: move deregistering outbound streams to API level 2

  
  def startThreads(self):
    """Starts thread required by the filter chain
    """
    self.avthread.startCall()


  def stopThreads(self):
    """Stops threads in the filter chain
    """
    self.avthread.stopCall()
    

  def decodingOff(self):
    self.avthread.decodingOffCall()


  def decodingOn(self):
    self.avthread.decodingOnCall()
    
    
    
class RTSPFilterchain:
  """This class implements the following filterchain:
  
  ::
                                            branch 1: bitmap to screen
    (LiveThread:livethread)                 +--->> (AVThread:avthread) -->> (OpenGLThread:glthread)
              |                             |
              |                             |
              +--->> {ForkFrameFilter:fork} +
                                            |
                                            |
                                            +-->> (LiveThread:livethread2) 
                                            branch 2: RTSP server
  """
  
  parameter_defs={
    "incoming_livethread"  : LiveThread,
    "outgoing_livethread"  : LiveThread,
    "openglthread" : OpenGLThread,
    "slot"         : int,
    "address"      : str,
    
    "rtsp_substream_name" : str,
    
    # these are for the AVThread instance:
    "n_basic"      : (int,20), # number of payload frames in the stack
    "n_setup"      : (int,20), # number of setup frames in the stack
    "n_signal"     : (int,20), # number of signal frames in the stack
    "flush_when_full" : (bool, False), # clear fifo at overflow
    
    "affinity"     : (int,-1),
    "verbose"      : (bool,False),
    "msreconnect"  : (int,0)
    }
  
  
  def __init__(self, **kwargs):
    self.pre=self.__class__.__name__+" : " # auxiliary string for debugging output
    parameterInitCheck(self.parameter_defs,kwargs,self) # check for input parameters, attach them to this instance as attributes
    self.init()
    
    
  def init(self):
    self.idst=str(id(self))
    self.makeChain()
    self.createContext()
    self.createOutputContext()
    self.startThreads()
    self.active=True
    
    
  def __del__(self):
    self.close()
    
    
  def close(self):
    if (self.active):
      if (self.verbose):
        print(self.pre,"Closing threads and contexes")
      self.decodingOff()
      self.closeContext()
      self.stopThreads()
      self.active=False
    
    
  def makeChain(self):
    """Create the filter chain
    """
    # branch 1
    self.gl_in_filter  =self.openglthread.getInput() # get input FrameFilter from OpenGLThread
    
    self.framefifo_ctx=core.FrameFifoContext()
    self.framefifo_ctx.n_basic           =self.n_basic
    self.framefifo_ctx.n_setup           =self.n_setup
    self.framefifo_ctx.n_signal          =self.n_signal
    self.framefifo_ctx.flush_when_full   =self.flush_when_full
    
    self.avthread      =core.AVThread("avthread_"+self.idst, self.gl_in_filter, self.framefifo_ctx)
    self.avthread.setAffinity(self.affinity)
    self.av_in_filter  =self.avthread.getFrameFilter() # get input FrameFilter from AVThread

    # branch 2
    self.live_out_filter =self.outgoing_livethread.core.getFrameFilter() # writing here writes to outgoing_livethread
    
    # fork
    self.fork =core.ForkFrameFilter("fork",self.av_in_filter,self.live_out_filter) # this one is used by incoming_livethread
    

  def createContext(self):
    """Creates a LiveConnectionContext and registers it to LiveThread.
    """
    # define stream source, how the stream is passed on, etc.
    
    self.ctx=core.LiveConnectionContext()
    self.ctx.slot=self.slot                          # slot number identifies the stream source
    
    if (self.address.find("rtsp://")==0):
      self.ctx.connection_type=core.LiveConnectionType_rtsp
    else:
      self.ctx.connection_type=core.LiveConnectionType_sdp # this is an rtsp connection
    
    self.ctx.address=self.address         
    # stream address, i.e. "rtsp://.."
    
    self.ctx.framefilter=self.fork
    
    self.ctx.msreconnect=self.msreconnect
    
    # send the information about the stream to LiveThread
    self.incoming_livethread.registerStream(self.ctx)
    self.incoming_livethread.playStream(self.ctx)


  def createOutputContext(self):
    """Creates an output context for sending the stream through the rtsp server
    """
    if (self.rtsp_substream_name!=""):
      self.out_ctx =core.LiveOutboundContext(core.LiveConnectionType_rtsp, self.rtsp_substream_name, self.slot, 0)
      self.outgoing_livethread.core.registerOutboundCall(self.out_ctx) # TODO: move registering outbound streams to API level 2
    

  def closeContext(self):
    self.outgoing_livethread.stopStream(self.ctx)
    self.outgoing_livethread.deregisterStream(self.ctx)
    
    
  def closeOutboundContext(self):
    if (self.self.rtsp_substream_name!=""):
      self.outgoing_livethread.core.deregisterOutboundCall(self.out_ctx) # TODO: move deregistering outbound streams to API level 2

  
  def startThreads(self):
    """Starts thread required by the filter chain
    """
    self.avthread.startCall()


  def stopThreads(self):
    """Stops threads in the filter chain
    """
    self.avthread.stopCall()
    

  def decodingOff(self):
    self.avthread.decodingOffCall()


  def decodingOn(self):
    self.avthread.decodingOnCall()
      

