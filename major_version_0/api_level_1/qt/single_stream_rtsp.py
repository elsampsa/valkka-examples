"""
single_stream.py : A demo program streaming from a single rtsp camera

Copyright 2017 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify
it under the terms of the MIT License
 
This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    single_stream.py
@author  Sampsa Riikonen
@date    2017
@version 0.1
@brief   A demo program streaming from a single rtsp camera
"""

from PyQt5 import QtWidgets, QtCore, QtGui # Qt5
import sys
from valkka.valkka_core import *


class MyGui(QtWidgets.QMainWindow):

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
    """
    filtergraph:
    (LiveThread:livethread) --> {InfoFrameFilter:live_out_filter} --> {FifoFrameFilter:av_in_filter} --> [FrameFifo:av_fifo] -->> (AVThread:avthread) --> {FifoFrameFilter:gl_in_gilter} --> 
    --> [OpenGLFrameFifo:gl_fifo] -->> (OpenGLThread:glthread)
    """
    self.glthread        =OpenGLThread ("glthread",
                                        10,     # n720p
                                        10,     # n1080p
                                        0,      # n1440p
                                        0,      # n4K
                                        10,     # naudio
                                        100,    # msbuftime
                                        -1      # thread affinity
                                        )
    
    self.gl_fifo         =self.glthread.getFifo() # get gl_fifo from glthread
    self.gl_in_filter    =FifoFrameFilter    ("gl_in_filter",   self.gl_fifo)
    
    self.av_fifo         =FrameFifo          ("av_fifo",10)                 
    self.avthread        =AVThread           ("avthread",       self.av_fifo, self.gl_in_filter) # [av_fifo] -->> (avthread) --> {gl_in_filter}
    
    self.av_in_filter    =FifoFrameFilter    ("av_in_filter",   self.av_fifo)
    self.live_out_filter =InfoFrameFilter    ("live_out_filter",self.av_in_filter)
    self.livethread      =LiveThread         ("livethread")
    
    self.glthread.  startCall()
    self.livethread.startCall()
    self.avthread  .startCall()
  
  
  def closeValkka(self):
    self.avthread  .stopCall()
    self.livethread.stopCall()
    self.glthread.  stopCall()
  
  
  def start_streams(self):
    print("start decoding")
    self.avthread.decodingOnCall()

    self.ctx=LiveConnectionContext()
    self.ctx.slot=1
    self.ctx.connection_type=LiveConnectionType_rtsp
    self.ctx.address=self.stream_address
    self.ctx.framefilter=self.live_out_filter
        
    print("registering stream")
    self.livethread.registerStreamCall(self.ctx)
    
    print("playing stream !")
    self.livethread.playStreamCall(self.ctx)
    
    self.glthread.newRenderGroupCall(self.window_id);
    self.context_id=self.glthread.newRenderContextCall(1, self.window_id, 0)
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

  