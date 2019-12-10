"""
test_studio_3.py : Test live streaming with Qt.  Jump video from one x-screen (and gpu) to another

Copyright 2017, 2018 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    test_studio_2.py
@author  Sampsa Riikonen
@date    2018
@version 0.15.0 
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
from valkka.api2.chains import OpenFilterchain
from valkka.api2.logging import *
from valkka.core import TimeCorrectionType_dummy, TimeCorrectionType_none, TimeCorrectionType_smart, ForkFrameFilterN, ValkkaXInitThreads

# Local imports form this directory
from demo_base import ConfigDialog, TestWidget0, getForeignWidget, WidgetPair, DesktopHandler

pre="test_studio_3 : " # aux string for debugging 

# setValkkaLogLevel(loglevel_debug)
# ValkkaXInitThreads()

class MyConfigDialog(ConfigDialog):
  
  def setConfigPars(self):
    self.tooltips={        # how about some tooltips?
      }
    self.pardic.update({
      "replicate"          : 1
      })
    self.plis +=["replicate"]
    self.config_fname="test_studio_3.config" # define the config file name
  

class GPUHandler:
  """Handles an OpenGLThread for each separate GPU
  """
  
  def __init__(self, pardic):
    self.pardic=pardic
    self.true_screens =[]
    self.openglthreads=[]
    self.findXScreens()
    
    # self.true_screens=[self.true_screens[0]]
    
    for n_gpu, screen in enumerate(self.true_screens):
    
      x_connection=":0."+str(n_gpu)
      # x_connection=":0.1"
      # x_connection=":1.0" # nopes
    
      print(pre,"GPUHandler: starting OpenGLThread with",x_connection)
    
      openglthread=OpenGLThread(     # starts frame presenting services
        name    ="gpu_"+str(n_gpu),
        n_720p   =self.pardic["n_720p"],   # reserve stacks of YUV video frames for various resolutions
        n_1080p  =self.pardic["n_1080p"],
        n_1440p  =self.pardic["n_1440p"],
        n_4K     =self.pardic["n_4K"],
        verbose =False,
        msbuftime=self.pardic["msbuftime"],
        affinity=self.pardic["gl affinity"],
        x_connection =x_connection
        )
      
      print(pre,"GPUHandler: OpenGLThread started")

      self.openglthreads.append(openglthread)
      
    if (self.openglthreads[0].hadVsync()):
      w=QtWidgets.QMessageBox.warning(None,"VBLANK WARNING","Syncing to vertical refresh enabled\n THIS WILL DESTROY YOUR FRAMERATE\n Disable it with 'export vblank_mode=0' for nvidia proprietary drivers, use 'export __GL_SYNC_TO_VBLANK=0'")

    
  def findXScreens(self):
    qapp    =QtCore.QCoreApplication.instance()
    screens =qapp.screens()
    """
    let's find out which screens are virtual
    
    screen, siblings:
      
    One big virtual desktop:
      
    A [A, B, C]
    B [A, B, C]
    C [A, B, C]
    
    A & B in one xscreen, C in another:
    
    A [A, B]
    B [A, B]
    C [C]
    
    """
    virtual_screens=set()
    for screen in screens:
      if (screen not in virtual_screens): # if screen has been deemed as "virtual", don't check its siblings
        siblings=screen.virtualSiblings()
        # remove the current screen under scrutiny from the siblings list
        virtual_screens.update(set(siblings).difference(set([screen])))
        # .. the ones left over are virtual
      
    # print("GPUHandler: findXScreens: virtual screens",virtual_screens)
    true_screens=list(set(screens)-virtual_screens)
    
    # sort'em
    for screen in true_screens:
      self.true_screens.insert(screens.index(screen),screen)
    
    print("GPUHandler: findXScreens: true screens:",self.true_screens)
    
    
  def close(self):
    for openglthread in self.openglthreads:
      openglthread.close()
    
    

class VideoContainer:
  """A widget container: video window and a button that sends it to another X-Screen
  
  :param slot:        The slot number identifying the video source
  :param gpu_handler: Instance of GPUHandler (i.e., the GPU & OpenGLThread handler)
  """
    
    
  """
  What we need here ..
                                                                            +------------->> (OpenGLThread:glthread1)
                                                                            |
  (LiveThread:livethread) -->> (AVThread:avthread) ----> {ForkFrameFilterN} +------------->> (OpenGLThread:glthread2)
                                                                            |
                                                                            +------------->> (OpenGLThread:glthread3)
                                >>  encapsulated into a class             <<
                                                                     
                                                                     
  - Btw .. when a video is not required on the monitor, it should not be sent to OpenGLThread at all..!
  - At the moment, just send all videos to all OpenGLThreads
  - When jump occurs, just reconnect the token                                                                     
  """
    
    
  def __init__(self,slot,gpu_handler):
    self.gpu_handler=gpu_handler
    
    self.n            =0
    self.openglthread =self.gpu_handler.openglthreads[self.n]
    
    qapp    =QtCore.QCoreApplication.instance()
    desktop =qapp.desktop()
    
    self.makeWidget(self.gpu_handler.true_screens[self.n]) # create widget into a certain xscreen
    self.win_id       =int(self.video.winId())
    print("VideoContainer: win_id=",self.win_id)
    
    self.slot    =slot
    self.token  =self.openglthread.connect(slot=self.slot,window_id=self.win_id) # present frames with slot number cs at window win_id
    
    
    
  def makeWidget(self,qscreen):
    """ Widget needs to be re-created when jumping from one x-screen to another
    
    :param qscreen:   QScreen
    """
    self.main_widget=QtWidgets.QWidget()
    self.main_widget.show()
    
    self.main_widget.windowHandle().setScreen(qscreen)
    self.lay        =QtWidgets.QVBoxLayout(self.main_widget)
    self.video      =TestWidget0(self.main_widget)
    self.button     =QtWidgets.QPushButton("Change Screen",self.main_widget)
    self.lay.addWidget(self.video)
    self.lay.addWidget(self.button)
    
    self.button.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)
    self.video.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
    
    self.button.clicked.connect(self.cycle_slot)
    self.main_widget.show()
    
    
  def cycle_slot(self):
    """Cycle from one X-Screen to another
    """
    self.openglthread.disconnect(self.token)
    
    self.n +=1
    if (self.n>=len(self.gpu_handler.true_screens)):
      self.n=0
    print("cycle_slot: going to screen:",self.n)
    
    self.openglthread =self.gpu_handler.openglthreads[self.n] # switch to OpenGLThread running on the other GPU
    
    print("cycle_slot: using OpenGLThread",self.openglthread.name)
    
    # WORKS WITH LATEST PYQT5 5.11.2
    self.makeWidget(self.gpu_handler.true_screens[self.n])
    
    self.win_id =int(self.video.winId()) # find the x-window id again
    print("VideoContainer: cycle_slot: win_id=",self.win_id)
    
    self.token =self.openglthread.connect(slot=self.slot,window_id=self.win_id) # present frames with slot number cs at window win_id
    
    
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

    self.gpu_handler=GPUHandler(self.pardic)

    self.chains=[]
    
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

      chain=OpenFilterchain(       # decoding and branching the stream happens here
        livethread  =self.livethread, 
        address     =address,
        slot        =cs,
        affinity    =a,
        # verbose     =True
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
  
      # send stream from all OpenFilterchain to all GPUs
      for glthread in self.gpu_handler.openglthreads:
        chain.connect(glthread.name,glthread.getInput()) # OpenGLThread.getInput() returns the input FrameFilter
        
      self.chains.append(chain) # important .. otherwise chain will go out of context and get garbage collected ..
      
      for cc in range(0,self.pardic["replicate"]):
        print(pre,"setupUi: layout index, address : ",cw//nrow,cw%nrow,address)
        # self.lay.addWidget(fr,cw//nrow,cw%nrow) # floating windows instead
        
        container =VideoContainer(cs,self.gpu_handler)
        container.getWidget().setGeometry(self.desktop_handler.getGeometry(nrow,ncol,cw%nrow,cw//nrow))
        container.getWidget().show()
        
        self.videoframes.append(container)
        
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
    self.gpu_handler.close()
    
    
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
 
 
