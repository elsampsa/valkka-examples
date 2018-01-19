"""
single_stream.py : A demo program: streaming from a single rtsp camera

Copyright 2017 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    single_stream.py
@author  Sampsa Riikonen
@date    2017
@version 0.1
@brief   A demo program: streaming from a single rtsp camera
"""

from PyQt5 import QtWidgets, QtCore, QtGui # Qt5
import sys
from valkka.valkka_core import *


class MyGui(QtWidgets.QMainWindow):
  """A simple Qt main window.  
  
  Creating the filterchain and starting valkka threads is done in method openValkka.  Stopping valkka threads done in closeValkka.
  """

  def __init__(self,parent=None,stream_address=None):
    super(MyGui, self).__init__()
    self.setupUi()
    if (stream_address==None):
      print("Stream not specified!")
      return
    else:
      self.stream_address=stream_address
    self.openValkka()
    self.start_streams()
    

  def setupUi(self):
    self.setGeometry(QtCore.QRect(100,100,500,500))
    
    # self.lay=QtWidgets.QHBoxLayout(self
    
    self.videoframe=QtWidgets.QFrame(self)
    self.setCentralWidget(self.videoframe)
    
    self.window_id=int(self.videoframe.winId())

    
  def openValkka(self):
    """Creates thread instances, creates filter chain, starts threads
    
    So, you've learned from
    
    https://elsampsa.github.io/valkka-core/html/process_chart.html
    
    that:
    
    * Concatenating FrameFilters, creates a simple callback cascade
    * Threads write to a FrameFilter
    * Threads read from a FrameFifo
    * FrameFifos have an internal stack of pre-reserved frames
    * Threads are not python threads, so there are no global intepreter lock (GIL) problems in this code
    
    The filtergraph (**) here looks like this:
    
    (LiveThread:livethread) --> {InfoFrameFilter:live_out_filter} --> {FifoFrameFilter:av_in_filter} --> [FrameFifo:av_fifo] -->> (AVThread:avthread) --> {FifoFrameFilter:gl_in_gilter} -->  
    --> [OpenGLFrameFifo:gl_fifo] -->> (OpenGLThread:glthread)
    """
    
    """
    Instantiate OpenGLThread.  This thread does all openGL calls.  It also times and presents all frames.  Memory is pre-reserved on the GPU, so we have to specify how many frames are reserved for every resolution.  You can use the following formula:
    
    Number of frames for resolution n = buffering time * (frames per second of one camera) * number of cameras for resolution n
    """
    self.glthread        =OpenGLThread ("glthread", # name
                                        10,         # n720p
                                        10,         # n1080p
                                        0,          # n1440p
                                        0,          # n4K
                                        10,         # naudio == number of audio frames
                                        100,        # buffering time in milliseconds
                                        -1          # thread affinity: -1 = no affinity, n = id of processor where the thread is bound
                                        )
    
    self.livethread      =LiveThread         ("livethread", # name
                                              0,            # size of input fifo
                                              -1            # thread affinity: -1 = no affinity, n = id of processor where the thread is bound
                                              )
    
    """
    Start constructing the filter chain.  Follow the filtergraph (**) from end to beginning.
    
    Some details:
    
    * OpenGLFrameFifo is a special FrameFifo - it must be requested from OpenGLThread.  This is because OpenGLThread handles all OpenGL calls, that are also needed to create the pre-reserved stack of frames, cached on the GPU (aka "pixel buffer objects")
    
    * Decoding thread AVThread reads from "av_fifo" and writes to "gl_in_filter"
    """
    self.gl_fifo         =self.glthread.getFifo()
    self.gl_in_filter    =FifoFrameFilter    ("gl_in_filter",   self.gl_fifo)
    
    self.av_fifo         =FrameFifo          ("av_fifo",10)        # FrameFifo is 10 frames long.  Payloads in the frames adapt automatically to the streamed data.
    
    # [av_fifo] -->> (avthread) --> {gl_in_filter}
    self.avthread        =AVThread           ("avthread",          # name    
                                              self.av_fifo,        # read from
                                              self.gl_in_filter,   # write to
                                              -1                   # thread affinity: -1 = no affinity, n = id of processor where the thread is bound
                                              ) 
    
    self.av_in_filter    =FifoFrameFilter    ("av_in_filter",   self.av_fifo)
    self.live_out_filter =InfoFrameFilter    ("live_out_filter",self.av_in_filter)
    
    # Start all threads
    self.glthread.  startCall()
    self.livethread.startCall()
    self.avthread  .startCall()
  
  
  def closeValkka(self):
    """Stop all valkka threads
    """
    self.avthread  .stopCall()
    self.livethread.stopCall()
    self.glthread.  stopCall()
  
  
  def start_streams(self):
    print("start decoding")
    self.avthread.decodingOnCall() # signal AVThread that it may start decoding

    # define stream source, how the stream is passed on, etc.
    self.ctx=LiveConnectionContext()
    self.ctx.slot=1                                  # slot number identifies the stream source
    self.ctx.connection_type=LiveConnectionType_rtsp # this is an rtsp connection
    self.ctx.address=self.stream_address             # stream address, i.e. "rtsp://.."
    self.ctx.framefilter=self.live_out_filter        # where the received frames are written to.  See filterchain (**)
        
    # send the information about the stream to LiveThread
    print("registering stream")
    self.livethread.registerStreamCall(self.ctx)
    
    # request frames from the stream
    print("playing stream !")
    self.livethread.playStreamCall(self.ctx)
    
    """
    "Render group" corresponds to an x-window (we can, in principle, render various bitmaps to the same x-window .. this will be implemented in the future (++))
    "Render context" is a mapping from a source (identified by slot number) to a "Render group" (x-window)
    """
    self.glthread.newRenderGroupCall(self.window_id);
    self.context_id=self.glthread.newRenderContextCall(1,               # slot number identifying the stream
                                                       self.window_id,  # where that stream is going to
                                                       0                # z index of the bitmap (not functional at the moment (++))
                                                        )
    
    # context_id identifies the Render context
    print("got render context id",self.context_id)
    
    
  def stop_streams(self):
    print("stopping streams")
    self.glthread.delRenderContextCall(self.context_id)
    ok=self.glthread.delRenderGroupCall(self.window_id)
    self.avthread.decodingOffCall()

    
  def closeEvent(self,e):
    print("closeEvent!")
    self.stop_streams()
    self.closeValkka()
    e.accept()


def main():
  if (len(sys.argv)<2):
    print("Give rtsp stream address, i.e. rtsp://passwd:user@ip")
    return
  app=QtWidgets.QApplication(["single_stream_test"])
  mg=MyGui(stream_address=sys.argv[1])
  mg.show()
  app.exec_()


if (__name__=="__main__"):
  main()

  