"""
test_studio_shmem.py : Test live streaming with Qt.  Send a copies of the streams via shared memory to a python multiprocess

Copyright 2017, 2018 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    test_studio_shmem.py
@author  Sampsa Riikonen
@date    2018
@version 0.1
@brief   Test live streaming with Qt.  Send copies of the streams to OpenCV movement detector processes.


In the main text field, write live video sources, one to each line, e.g.

::

    rtsp://admin:admin@192.168.1.10
    rtsp://admin:admin@192.168.1.12
    multicast.sdp
    multicast2.dfp

Reserve enough frames into the pre-reserved frame stack.  There are stacks for 720p, 1080p, etc.  The bigger the buffering time "msbuftime" (in milliseconds), the bigger stack you'll be needing.

When affinity is greater than -1, the processes are bound to a certain processor.  Setting "live affinity" to 0, will bind the Live555 thread to processor one.  Setting "dec affinity start" to 1 and "dec affinity start 3" will bind the decoding threads to processors 1-3.  (first decoder process to 1, second to 2, third to 3, fourth to 1 again, etc.)

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

from PyQt5 import QtWidgets, QtCore, QtGui # Qt5
import cv2
import sys
import json
import os
from valkka.api2.threads import LiveThread, OpenGLThread, ValkkaProcess, ShmemClient
from valkka.api2.chains import ShmemFilterchain
from valkka.api2.tools import parameterInitCheck
from valkkathread import QValkkaThread, QValkkaOpenCVProcess
from analyzer import MovementDetector
from demo_base import ConfigDialog, TestWidget0, TestWidget, getForeignWidget, WidgetPair


pre="test_studio_shmem : "
 
   
class MyConfigDialog(ConfigDialog):
  
  
  def setConfigPars(self):
    self.tooltips={        # how about some tooltips?
      }
    self.pardic.update({}) # add more parameter key/value pairs
    self.plis +=[]         # list of parameter keys that are saved to config file
    self.config_fname="test_studio_shmem.config" # define the config file name


  def extra(self):
    self.run2_button.hide()    
    self.ffplay_button.hide() 
    self.vlc_button.hide() 
    

        
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
    self.startProcesses()
    
    
  def initVars(self):
    pass


  def setupUi(self):
    self.setGeometry(QtCore.QRect(100,100,800,800))
    self.w=QtWidgets.QWidget(self)
    self.setCentralWidget(self.w)
    self.lay=QtWidgets.QGridLayout(self.w)
    self.addresses  =self.pardic["cams"]
    
  
  def openValkka(self):
    self.livethread=LiveThread(         # starts live stream services (using live555)
      name   ="live_thread",
      verbose=False,
      affinity=self.pardic["live affinity"]
    )

    self.openglthread=OpenGLThread(     # starts frame presenting services
      name    ="mythread",
      n720p   =self.pardic["n720p"],   # reserve stacks of YUV video frames for various resolutions
      n1080p  =self.pardic["n1080p"],
      n1440p  =self.pardic["n1440p"],
      n4K     =self.pardic["n4K"],
      naudio  =self.pardic["naudio"],
      verbose =False,
      msbuftime=self.pardic["msbuftime"],
      affinity=self.pardic["gl affinity"]
      )

    if (self.openglthread.hadVsync()):
      w=QtWidgets.QMessageBox.warning(self,"VBLANK WARNING","Syncing to vertical refresh enabled\n THIS WILL DESTROY YOUR FRAMERATE\n Disable it with 'export vblank_mode=0' for nvidia proprietary drivers, use 'export __GL_SYNC_TO_VBLANK=0'")

    tokens           =[]
    self.chains      =[]
    self.processes   =[]
    self.widget_pairs=[]
    self.videoframes =[]
    cs=1
    cc=0
    a=self.pardic["dec affinity start"]
    
    for address in self.addresses:
      # now livethread and openglthread are running
      if (a>self.pardic["dec affinity stop"]): a=self.pardic["dec affinity start"]
      
      print(pre,"openValkka: setting decoder thread on processor",a)
      
      chain=ShmemFilterchain(       # decoding and branching the stream happens here
        livethread  =self.livethread, 
        openglthread=self.openglthread,
        address     =address,
        slot        =cs,
        affinity    =a,
        # this filterchain creates a shared memory server
        shmem_name             ="test_studio_"+str(cs),
        shmem_image_dimensions =(1920//4,1080//4),  # Images passed over shmem are quarter of the full-hd reso
        shmem_image_interval   =1000,               # YUV => RGB interpolation to the small size is done each 1000 milliseconds and passed on to the shmem ringbuffer
        shmem_ringbuffer_size  =10                  # Size of the shmem ringbuffer
        )
    
      shmem_name, n_buffer, n_bytes =chain.getShmemPars()
      # print(pre,"shmem_name, n_buffer, n_bytes",shmem_name,n_buffer,n_bytes)
      
      process=QValkkaOpenCVProcess("process_"+str(cs),shmem_name=shmem_name, n_buffer=n_buffer, n_bytes=n_bytes)
            
      self.chains.append(chain)
      self.processes.append(process)

      win_id      =self.openglthread.createWindow(show=False)
      widget_pair =WidgetPair(self.w,win_id,TestWidget0)
      fr          =widget_pair.getWidget()
      self.widget_pairs.append(widget_pair)
    
      print(pre,"setupUi: layout index, address : ",cc//4,cc%4,address)
      self.lay.addWidget(fr,cc//4,cc%4)
      self.videoframes.append(fr)
      
      token  =self.openglthread.connect(slot=cs,window_id=win_id)
      tokens.append(token)
      
      chain.decodingOn() # tell the decoding thread to start its job
      cs+=1 # TODO: crash when repeating the same slot number ..?
      a +=1
      cc+=1
      
    # finally, give the multiprocesses to a qthread that's reading their message pipe
    self.thread =QValkkaThread(processes=self.processes)
    
  
  def startProcesses(self):
    for p in self.processes:
      p.start()
      # p.startAsThread() # debugging
    self.thread.start()
  
  
  def stopProcesses(self):
    for p in self.processes:
      p.stop()
    print(pre,"stopping QThread")
    self.thread.stop()
    # self.thread.quit() # nopes ..
    print(pre,"QThread stopped")
    
    
  def closeEvent(self,e):
    print(pre,"closeEvent!")
    self.stopProcesses()
    self.chains=[]
    self.videoframes=[]
    self.widget_pairs=[]
    super().closeEvent(e)



def main():
  app=QtWidgets.QApplication(["test_app"])
  conf=MyConfigDialog()
  pardic=conf.exec_()
  # print(pre,"got",pardic)
  # return
  if (pardic["ok"]):
    mg=MyGui(pardic)
    mg.show()
    app.exec_()


if (__name__=="__main__"):
  main()
 
 
