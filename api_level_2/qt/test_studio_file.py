"""
test_studio_file.py : An example GUI for reading matroska (mkv) files, playing and sending them to an analyzer

* Copyright: 2018 Sampsa Riikonen
* Authors  : Sampsa Riikonen
* Date     : 2018
* Version  : 0.1

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    test_studio_file.py
@author  Sampsa Riikonen
@date    2018
@version 0.5.1 
@brief   An example GUI for reading matroska (mkv) files, playing and sending them to an analyzer
"""

# from PyQt5 import QtWidgets, QtCore, QtGui # If you use PyQt5, be aware of the licensing consequences
from PySide2 import QtWidgets, QtCore, QtGui
import cv2
import sys
import json
import time
import os
from valkka.api2 import LiveThread, FileThread, OpenGLThread, ValkkaProcess, ShmemClient
from valkka.api2 import ShmemFilterchain1
from valkka.api2 import parameterInitCheck

# Local imports from this directory
from demo_multiprocess import QValkkaThread
from demo_analyzer_process import QValkkaMovementDetectorProcess
from analyzer import MovementDetector
from demo_base import ConfigDialog, TestWidget0, getForeignWidget, WidgetPair
pre="test_studio_file : "
 
valkka_xwin =True # use x windows create by Valkka and embed them into Qt
# valkka_xwin =False # use Qt provided x windows

class MyGui(QtWidgets.QMainWindow):

  debug=False
  # debug=True

  def __init__(self):
    super(MyGui, self).__init__()
    # self.pardic=pardic
    self.initVars()
    self.setupUi()
    if (self.debug): 
      return
    self.openValkka()
    self.startProcesses()
    
    
  def initVars(self):
    self.messages=[]
    self.mode="file"
    self.slot_reserved=False


  def setupUi(self):
    self.setGeometry(QtCore.QRect(100,100,800,800))
    self.w=QtWidgets.QWidget(self)
    self.setCentralWidget(self.w)
    self.lay=QtWidgets.QVBoxLayout(self.w)
    
    # divide window into three parts
    self.upper  =QtWidgets.QWidget(self.w)
    self.lower  =QtWidgets.QWidget(self.w)
    self.lowest =QtWidgets.QWidget(self.w)
    self.lay.addWidget(self.upper)
    self.lay.addWidget(self.lower)
    self.lay.addWidget(self.lowest)
    
    # upper part: license plate list and the video
    self.upperlay   =QtWidgets.QHBoxLayout(self.upper)
    self.msg_list  =QtWidgets.QTextEdit(self.upper)
    
    self.video_area =QtWidgets.QWidget(self.upper)
    self.video_lay  =QtWidgets.QGridLayout(self.video_area)
    
    self.upperlay.addWidget(self.msg_list)
    self.upperlay.addWidget(self.video_area)
    self.msg_list.setSizePolicy(QtWidgets.QSizePolicy.Minimum,  QtWidgets.QSizePolicy.Minimum)
    self.video_area.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
    
    # lower part: [Open File] [Close Live] [Play] [Stop] [Rewind]
    self.lowerlay  =QtWidgets.QHBoxLayout(self.lower)
    self.open_file_button =QtWidgets.QPushButton("Open File", self.lower)
    self.close_file_button=QtWidgets.QPushButton("Close File",self.lower)
    self.play_button      =QtWidgets.QPushButton("Play",self.lower)
    self.stop_button      =QtWidgets.QPushButton("Stop",self.lower)
    self.rewind_button    =QtWidgets.QPushButton("<<",  self.lower)
    
    self.lowerlay.addWidget(self.open_file_button)
    self.lowerlay.addWidget(self.close_file_button)
    self.lowerlay.addWidget(self.play_button)
    self.lowerlay.addWidget(self.stop_button)
    self.lowerlay.addWidget(self.rewind_button)
    
    self.open_file_button.clicked. connect(self.open_file_button_slot)
    self.close_file_button.clicked.connect(self.close_file_button_slot)
    self.play_button.clicked.      connect(self.play_button_slot)
    self.stop_button.clicked.      connect(self.stop_button_slot)
    self.rewind_button.clicked.    connect(self.rewind_button_slot)
    
    # lowest part: some text
    self.lowestlay=QtWidgets.QVBoxLayout(self.lowest)
    self.infotext =QtWidgets.QLabel("info text",self.lowest)
    self.lowestlay.addWidget(self.infotext)
    
    
  def openValkka(self):
    self.livethread=LiveThread(         # starts live stream services (using live555)
      name   ="live_thread",
      verbose=False
    )

    self.filethread=FileThread(
      name  ="file_thread",
      verbose=False
    )

    self.openglthread=OpenGLThread(     # starts frame presenting services
      name    ="mythread",
      n_720p   =10,
      n_1080p  =10,
      n_1440p  =10,
      n_4K     =10,
      verbose =False,
      msbuftime=100,
      affinity=-1
      )
    
    if (self.openglthread.hadVsync()):
      w=QtWidgets.QMessageBox.warning(self,"VBLANK WARNING","Syncing to vertical refresh enabled\n THIS WILL DESTROY YOUR FRAMERATE\n Disable it with 'export vblank_mode=0' for nvidia proprietary drivers, use 'export __GL_SYNC_TO_VBLANK=0'")
    
    cc=1
    
    self.chain=ShmemFilterchain1(       # decoding and branching the stream happens here
      openglthread=self.openglthread,
      slot        =cc,
      # this filterchain creates a shared memory server
      shmem_name             ="test_studio_file_"+str(cc),
      shmem_image_dimensions =(1920//4,1080//4),  # Images passed over shmem are quarter of the full-hd reso
      shmem_image_interval   =1000,               # YUV => RGB interpolation to the small size is done each 1000 milliseconds and passed on to the shmem ringbuffer
      shmem_ringbuffer_size  =10                  # Size of the shmem ringbuffer
      )
    
    shmem_name, n_buffer, shmem_image_dimensions =self.chain.getShmemPars()    
    # print(pre,"shmem_name, n_buffer, n_bytes",shmem_name,n_buffer,n_bytes)
    
    self.process=QValkkaMovementDetectorProcess("process_"+str(cc),shmem_name=shmem_name, n_buffer=n_buffer, image_dimensions=shmem_image_dimensions)
    
    self.process.signals.start_move.connect(self.set_moving_slot)
    self.process.signals.stop_move. connect(self.set_still_slot)
    
    if (valkka_xwin):
      # (1) Let OpenGLThread create the window
      self.win_id      =self.openglthread.createWindow(show=False)
      self.widget_pair =WidgetPair(self.video_area,self.win_id,TestWidget0)
      self.video       =self.widget_pair.getWidget()
    else:
      # (2) Let Qt create the window
      self.video     =QtWidgets.QWidget(self.video_area)
      self.win_id    =int(self.video.winId())
    
    self.video_lay.addWidget(self.video,0,0)
    self.token =self.openglthread.connect(slot=cc,window_id=self.win_id)
    
    self.chain.decodingOn() # tell the decoding thread to start its job
    
    # finally, give the multiprocesses to a qthread that's reading their message pipe
    self.thread =QValkkaThread(processes=[self.process])
    
  
  def startProcesses(self):
    self.process.start()
    self.thread.start()
  
  
  def stopProcesses(self):
    self.process.stop()
    self.thread.stop()
    print(pre,"QThread stopped")
    
    
  def closeValkka(self):
    self.livethread.close()
    self.chain.close()
    self.chain =None
    self.openglthread.close()
    
    
  def closeEvent(self,e):
    print(pre,"closeEvent!")
    self.stopProcesses()
    self.closeValkka()
    super().closeEvent(e)
    
    
  # *** slot ****
  def open_file_button_slot(self):
    if (self.slot_reserved):
      self.infotext.setText("Close the current file first")
      return
    fname=QtWidgets.QFileDialog.getOpenFileName(filter="*.mkv")[0]
    if (len(fname)>0):
      print(pre,"open_file_button_slot: got filename",fname)
      self.chain.setFileContext(fname)
      self.filethread.openStream(self.chain.file_ctx)
      self.slot_reserved=True
      if (self.chain.fileStatusOk()):
        self.infotext.setText("Opened file "+fname)
      else:
        self.infotext.setText("Can't play file "+fname)
    else:
      self.infotext.setText("No file opened")
    
  
  def close_file_button_slot(self):
    if (not self.slot_reserved):
      self.infotext.setText("Open a file first")
      return
    self.filethread.closeStream(self.chain.file_ctx)
    self.slot_reserved=False
    self.infotext.setText("Closed file")
  
  
  def open_live_button_slot(self):
    pass
  
  
  def play_button_slot(self):
    if (self.mode=="file"):
      if (not self.slot_reserved):
        self.infotext.setText("Open a file first")
        return
      self.filethread.playStream(self.chain.file_ctx)
    else:
      pass
    
    
  def rewind_button_slot(self):
    if (self.mode=="file"):
      if (not self.slot_reserved):
        self.infotext.setText("Open a file first")
        return
      self.chain.file_ctx.seektime_=0;
      self.filethread.seekStream(self.chain.file_ctx)
    else:
      pass
    
    
  def stop_button_slot(self):
    if (self.mode=="file"):
      if (not self.slot_reserved):
        self.infotext.setText("Open a file first")
        return
      self.filethread.stopStream(self.chain.file_ctx)
    else:
      pass
    
  
  def set_still_slot(self):
    self.infotext.setText("still")
    self.messages.append("Movement stopped at ")
    if (len(self.messages)>10): self.messages.pop(0)
    st=""
    for message in self.messages:
      st+=message+"\n"
    self.msg_list.setText(st)
    
      
  def set_moving_slot(self):
    self.infotext.setText("MOVING")
    self.messages.append("Movement started at ")
    if (len(self.messages)>10): self.messages.pop(0)
    st=""
    for message in self.messages:
      st+=message+"\n"
    self.msg_list.setText(st)
    
    
def main():
  app=QtWidgets.QApplication(["test_app"])
  mg=MyGui()
  mg.show()
  app.exec_()


if (__name__=="__main__"):
  main()

 
