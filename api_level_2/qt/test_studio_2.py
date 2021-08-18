"""
test_studio_2.py : Test live streaming with Qt with floating instead of grouped widgets

Copyright 2017-2021 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  
This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the MIT License for more details.

@file    test_studio_2.py
@author  Sampsa Riikonen
@date    2018
@version 1.2.1 
@brief   Test live streaming with Qt with floating instead of grouped widgets


In the main text field, write live video sources, one to each line, e.g.

::

    rtsp://admin:admin@192.168.1.10
    rtsp://admin:admin@192.168.1.12
    multicast.sdp
    multicast2.dfp

Reserve enough frames into the pre-reserved frame stack.  There are stacks for 720p, 1080p, etc.  The bigger the buffering time "msbuftime" (in milliseconds), the bigger stack you'll be needing.

When affinity is greater than -1, the processes are bound to a certain processor.  Setting "live affinity" to 0, will bind the Live555 thread to processor one.  
Setting "dec affinity start" to 1 and "dec affinity start 3" will bind the decoding threads to processors 1-3.  (first decoder process to 1, second to 2, third to 3, fourth to 1 again, etc.)

If replicate is 10, then each video is replicated 10 times.  It is _not_ decoded 10 times, but just copied to 10 more x windoses.

It's very important to disable vertical sync in OpenGL rendering..!  Otherwise your *total* framerate is limited to 60 fps.  Disabling vsync can be done in mesa-based open source drives with:

::

    export vblank_mode=0

and in nvidia proprietary drivers with

::

    export __GL_SYNC_TO_VBLANK=0

For benchmarking purposes, you can launch the video streams with:

  -PyQt created X windowses (this is the intended use case) : RUN(QT)
  -With X windowses created by valkka : RUN
  -With ffplay or vlc (if you have them installed)


This Qt test program produces a config file.  You might want to remove that config file after updating the program.
"""

# from PyQt5 import QtWidgets, QtCore, QtGui # If you use PyQt5, be aware of the licensing consequences
from PySide2 import QtWidgets, QtCore, QtGui
import sys
import json
import os
import time
from valkka.api2 import LiveThread, OpenGLThread
from valkka.api2.logging import setValkkaLogLevel, loglevel_silent, loglevel_crazy
from valkka.core import TimeCorrectionType_dummy, TimeCorrectionType_none, TimeCorrectionType_smart

# Local imports form this directory
from basic import BasicFilterchain # a file in this directory, implementing filterchains
from demo_base import ConfigDialog, TestWidget0, getForeignWidget, WidgetPair, DesktopHandler

pre="test_studio_2 : " # aux string for debugging 

# valkka_xwin =True # use x windows created by Valkka and embed them into Qt
valkka_xwin =False # use Qt provided x windows

# setValkkaLogLevel(loglevel_silent)
# setValkkaLogLevel(loglevel_crazy)

class MyConfigDialog(ConfigDialog):
  
  def setConfigPars(self):
    self.tooltips={        # how about some tooltips?
      }
    # define customizable parameters
    self.pardic.update({
      "replicate"          : 1
      })
    # self.plis defines parameters to be saved on the disk
    self.plis +=["replicate"]
    self.config_fname="test_studio_2.config" # define the config file name
  

  
class VideoContainer:
  """A widget container: a floating window containing a video widget
  
  :param parent:    Parent widget (if any)
  :param video:     The video widget (A subclassed QWidget)
  """
    
  def __init__(self,parent,video,n=0):
    self.n =n
    self.main_widget=QtWidgets.QWidget(parent)
    self.lay        =QtWidgets.QVBoxLayout(self.main_widget)
    self.video      =video; self.video.setParent(self.main_widget)
    self.lay.addWidget(self.video)    
    self.video.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        
    
  def mouseDoubleClickEvent(self,e):
    print("double click!")
        
  
  def getVideoWidget(self):
    return self.video

  
  def getWidget(self):
    return self.main_widget
  
    

class MyGui(QtWidgets.QMainWindow):

  debug=False
  # debug=True

  def __init__(self,pardic,parent=None):
    super(MyGui, self).__init__()
    # print(pre,"Qapp=",QtCore.QCoreApplication.instance())
    self.pardic=pardic
    self.initVars()
    self.setupUi()
    if (self.debug): 
      return
    self.openValkka()
    self.start_streams()
    
    
  def initVars(self):
    pass


  def setupUi(self):
    self.desktop_handler =DesktopHandler()
    print(self.desktop_handler)
    
    self.setGeometry(QtCore.QRect(100,100,800,800))
    self.w=QtWidgets.QWidget(self)
    self.setCentralWidget(self.w)
    self.lay=QtWidgets.QGridLayout(self.w)
    
    self.videoframes =[]
    self.widget_pairs=[]
    self.addresses=self.pardic["cams"]
    
  
  def openValkka(self):
    self.livethread=LiveThread(         # starts live stream services (using live555)
      name   ="live_thread",
      # verbose=True,
      verbose=False,
      affinity=self.pardic["live affinity"]
    )

    self.openglthread=OpenGLThread(     # starts frame presenting services
      name    ="mythread",
      n_720p   =self.pardic["n_720p"],   # reserve stacks of YUV video frames for various resolutions
      n_1080p  =self.pardic["n_1080p"],
      n_1440p  =self.pardic["n_1440p"],
      n_4K     =self.pardic["n_4K"],
      # verbose =False,
      verbose = True,
      msbuftime=self.pardic["msbuftime"],
      affinity=self.pardic["gl affinity"]
      )

    if (self.openglthread.hadVsync()):
      w=QtWidgets.QMessageBox.warning(self,"VBLANK WARNING","Syncing to vertical refresh enabled\n\
      THIS WILL DESTROY YOUR FRAMERATE\n Disable it with 'export vblank_mode=0' for nvidia proprietary drivers, use 'export __GL_SYNC_TO_VBLANK=0'")

    tokens     =[] # list of tokens representing slot number => X window-id mappings
    self.chains=[] # list of BasicFilterChain instances
    
    a =self.pardic["dec affinity start"]
    cw=0 # widget / window index
    cs=1 # slot / stream count
    
    ntotal=len(self.addresses)*self.pardic["replicate"]
    nrow  =self.pardic["videos per row"]
    ncol  =max( (ntotal//self.pardic["videos per row"])+1, 2)
    
    for address in self.addresses:
      # now livethread and openglthread are running
      if (a>self.pardic["dec affinity stop"]): a=self.pardic["dec affinity start"]
      print(pre,"openValkka: setting decoder thread on processor",a)

      chain=BasicFilterchain(       # decoding and branching the stream happens here
        livethread  =self.livethread, 
        openglthread=self.openglthread,
        address     =address,
        slot        =cs,
        affinity    =a,
        # verbose     =True,
        verbose     =False,
        msreconnect =10000,
        
        # flush_when_full =True
        flush_when_full =False,
        
        # time_correction   =TimeCorrectionType_dummy,  # Timestamp correction type: TimeCorrectionType_none, TimeCorrectionType_dummy, or TimeCorrectionType_smart (default)
        time_correction   =TimeCorrectionType_smart,
        
        recv_buffer_size  =0,                        # Operating system socket ringbuffer size in bytes # 0 means default
        # recv_buffer_size  =1024*800,   # 800 KB
        
        reordering_mstime =0                           # Reordering buffer time for Live555 packets in MILLIseconds # 0 means default
        # reordering_mstime =300                         
        )
  
      self.chains.append(chain) # important .. otherwise chain will go out of context and get garbage collected ..
      
      for cc in range(0,self.pardic["replicate"]):
        if ("no_qt" in self.pardic):
          # create our own x-windowses
          win_id=self.openglthread.createWindow(show=True)
        else:
          
          # *** Choose one of the following sections ***
          
          # (1) Let Valkka create the windows/widget # use this: we get a window with correct parametrization
          # win_id =self.openglthread.createWindow(show=False)
          # fr     =getForeignWidget(self.w, win_id)
          
          if (valkka_xwin==False):
            # (2) Let Qt create the widget
            fr =TestWidget0(None); win_id =int(fr.winId()) 
          else:
            # """
            # (3) Again, let Valkka create the window, but put on top a translucent widget (that catches mouse gestures)
            win_id      =self.openglthread.createWindow(show=False)
            widget_pair =WidgetPair(None,win_id,TestWidget0)
            fr          =widget_pair.getWidget()
            self.widget_pairs.append(widget_pair)
            # """
            
          print(pre,"setupUi: layout index, address : ",cw//nrow,cw%nrow,address)
          # self.lay.addWidget(fr,cw//nrow,cw%nrow) # floating windows instead
          
          container =VideoContainer(None,fr,n=0)
          container.getWidget().setGeometry(self.desktop_handler.getGeometry(nrow,ncol,cw%nrow,cw//nrow))
          container.getWidget().show()
          
          self.videoframes.append(container)
          
        token  =self.openglthread.connect(slot=cs,window_id=win_id) # present frames with slot number cs at window win_id
        tokens.append(token)
        cw+=1
      
      cs+=1 # TODO: crash when repeating the same slot number ..?
        
      chain.decodingOn() # tell the decoding thread to start its job
      a+=1
      
  
  def closeValkka(self):
    self.livethread.close()
    for chain in self.chains:
      chain.close()
    self.chains       =[]
    print(pre, "closeValkka: closing openglthread")
    self.openglthread.close()
    print(pre, "closeValkka: openglthread closed")
    # of couse, do _not_ "annihilate" the floating Qt windows while openglthread is still trying to write into them
    # after openglthread has been closed:
    self.widget_pairs =[]
    self.videoframes  =[]

    
  def start_streams(self):
    pass
    
    
  def stop_streams(self):
    pass
    
  def closeEvent(self,e):
    print(pre,"closeEvent!")
    self.stop_streams()
    self.closeValkka()
    e.accept()


def main():
  app=QtWidgets.QApplication(["test_app"])
  conf=MyConfigDialog()
  pardic=conf.exec_()
  if (pardic["ok"]):
    mg=MyGui(pardic)
    mg.show()
    app.exec_()


if (__name__=="__main__"):
  main()
 
 
