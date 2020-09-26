"""
test_studio_1.py : Test live streaming with Qt

Copyright 2017, 2018 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    test_studio_1.py
@author  Sampsa Riikonen
@date    2018
@version 1.0.0 
@brief   Test live streaming with Qt


In the main text field, write live video sources, one to each line, e.g.

::

    rtsp://admin:admin@192.168.1.10
    rtsp://admin:admin@192.168.1.12
    multicast.sdp
    multicast2.dfp

Reserve enough frames into the pre-reserved frame stack.  There are stacks for 720p, 1080p, etc.  The bigger the buffering time "msbuftime" (in milliseconds), the bigger stack you'll be needing.

When affinity is greater than -1, the processes are bound to a certain processor.  Setting "live affinity" to 0, will bind the Live555 thread to processor one.  Setting "dec affinity start" to 1 and "dec affinity start 3" will bind the decoding threads to processors 1-3.  (first decoder process to 1, second to 2, third to 3, fourth to 1 again, etc.)

If replicate is 10, then each video is replicated 10 times.  It is _not_ decoded 10 times, but just copied to 10 more x windoses.

It's very important to disable vertical sync in OpenGL rendering..!  Otherwise your *total* framerate is limited to 60 fps.  Disabling vsync can be done in mesa-based open source drives with:

export vblank_mode=0

and in nvidia proprietary drivers with

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
from valkka.api2 import BasicFilterchain
from valkka.api2.logging import *
from valkka.core import TimeCorrectionType_dummy, TimeCorrectionType_none, TimeCorrectionType_smart, setLogLevel_livelogger

# Local imports form this directory
from demo_base import ConfigDialog, TestWidget0, getForeignWidget, WidgetPair

pre="test_studio : " # aux string for debugging 


# valkka_xwin =True # use x windows create by Valkka and embed them into Qt
valkka_xwin =False # use Qt provided x windows

# setValkkaLogLevel(loglevel_silent) # set all loggers to silent
# setLogLevel_livelogger(loglevel_crazy) # set an individual loggers


class MyConfigDialog(ConfigDialog):
  
  def setConfigPars(self):
    self.tooltips={        # how about some tooltips?
      }
    self.pardic.update({
      "replicate"          : 1,
      "correct timestamp"  : 1,
      "socket size bytes"  : 0,
      "ordering time millisecs" : 0,
      "threads per decoder": 1
      })
    self.plis +=["replicate"]
    self.plis +=["correct timestamp"]
    self.plis +=["socket size bytes"]
    self.plis +=["ordering time millisecs"]
    self.plis +=["threads per decoder"]
    self.config_fname="test_studio_1.config" # define the config file name
 
 
class MyGui(QtWidgets.QMainWindow):

  debug=False
  # debug=True

  def __init__(self,pardic,parent=None):
    super(MyGui, self).__init__()
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
      # naudio  =self.pardic["naudio"], # obsolete
      # verbose =True,
      verbose =False,
      msbuftime=self.pardic["msbuftime"],
      affinity=self.pardic["gl affinity"]
      )

    
    if (self.openglthread.hadVsync()):
      w=QtWidgets.QMessageBox.warning(self,"VBLANK WARNING","Syncing to vertical refresh enabled\n THIS WILL DESTROY YOUR FRAMERATE\n Disable it with 'export vblank_mode=0' for nvidia proprietary drivers, use 'export __GL_SYNC_TO_VBLANK=0'")

    tokens     =[]
    self.chains=[]
    
    a =self.pardic["dec affinity start"]
    cw=0 # widget / window index
    cs=1 # slot / stream count
    
    for address in self.addresses:
      # now livethread and openglthread are running
      if (a>self.pardic["dec affinity stop"]): a=self.pardic["dec affinity start"]
      print(pre,"openValkka: setting decoder thread on processor",a)


      # Timestamp correction type: TimeCorrectionType_none, TimeCorrectionType_dummy, or TimeCorrectionType_smart (default)
      if self.pardic["correct timestamp"] == 1:
          time_correction = TimeCorrectionType_smart
      else:
          time_correction = TimeCorrectionType_dummy
          
      chain=BasicFilterchain(       # decoding and branching the stream happens here
        livethread  =self.livethread, 
        openglthread=self.openglthread,
        address     =address,
        slot        =cs,
        affinity    =a,
        # verbose    =True
        verbose     =False,
        msreconnect =10000,
        
        # flush_when_full =True
        flush_when_full =False,
        
        time_correction = time_correction,
        
        recv_buffer_size = self.pardic["socket size bytes"],                        # Operating system socket ringbuffer size in bytes # 0 means default
        # recv_buffer_size  =1024*800,   # 800 KB
        
        reordering_mstime = self.pardic["ordering time millisecs"],                   # Reordering buffer time for Live555 packets in MILLIseconds # 0 means default
        # reordering_mstime =300           
        n_threads = self.pardic["threads per decoder"]
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
            fr =TestWidget0(self.w)
            win_id =int(fr.winId()) 
          else:
            # """
            # (3) Again, let Valkka create the window, but put on top a translucent widget (that catches mouse gestures)
            win_id      =self.openglthread.createWindow(show=False)
            widget_pair =WidgetPair(self.w,win_id,TestWidget0)
            fr          =widget_pair.getWidget()
            self.widget_pairs.append(widget_pair)
            # """
            
          nrow=self.pardic["videos per row"]
          print(pre,"setupUi: layout index, address : ",cw//nrow,cw%nrow,address)
          self.lay.addWidget(fr,cw//nrow,cw%nrow)
          self.videoframes.append(fr)
          
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
    self.widget_pairs =[]
    self.videoframes  =[]
    self.openglthread.close()
    
    
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
 
 
