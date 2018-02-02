"""
test_studio_detector.py : Test live streaming with Qt.  Send a copies of the streams to OpenCV movement detector processes.

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
from valkka.valkka_core import XInitThreads
from valkka.api2.threads import LiveThread, OpenGLThread, ValkkaProcess, ShmemClient
from valkka.api2.chains import ShmemFilterchain
from valkka.api2.tools import parameterInitCheck
from valkkathread import QValkkaThread
from analyzer import MovementDetector

pre="test_studio_detector : "
 
class ValkkaOpenCVProcess(ValkkaProcess):
  
  
  incoming_signal_defs={ # each key corresponds to a front- and backend methods
    "test_"    : {"test_int": int, "test_str": str},
    "stop_"    : [],
    "ping_"    : {"message":str}
    }
  
  outgoing_signal_defs={
    "pong_o"    : {"message":str}
    }
  
  # For each outgoing signal, create a Qt signal with the same name.  The frontend Qt thread will read processes communication pipe and emit these signals.
  class Signals(QtCore.QObject):  
    pong_o  =QtCore.pyqtSignal(object)
  
  
  parameter_defs={
    "n_buffer"   : (int,10),
    "n_bytes"    : int,
    "shmem_name" : str
    }
  
  
  def __init__(self,name,**kwargs):
    super().__init__(name,**kwargs)
    self.signals =self.Signals()
    parameterInitCheck(ValkkaOpenCVProcess.parameter_defs, kwargs, self)
    
    
  def preRun_(self):
    """Create the shared memory client after fork
    """
    # XInitThreads() # doesn't help
    self.client=ShmemClient(
      name          =self.shmem_name, 
      n_ringbuffer  =self.n_buffer,   # size of ring buffer
      n_bytes       =self.n_bytes,    # size of the RGB image
      mstimeout     =1000,            # client timeouts if nothing has been received in 1000 milliseconds
      verbose       =False
    )
    
    
  def cycle_(self):
    index, isize = self.client.pull()
    if (index==None):
      print(self.pre,"Client timed out..")
    else:
      print(self.pre,"Client index, size =",index, isize)
      data=self.client.shmem_list[index]
      img=data.reshape((1080//4,1920//4,3))
      """ # WARNING: the x-server doesn't like this, i.e., we're creating a window from a separate python multiprocess, so the program will crash
      print(self.pre,"Visualizing with OpenCV")
      cv2.imshow("openCV_window",img)
      cv2.waitKey(1)
      """
      print(self.pre,">>>",data[0:10])
      
      # res=self.analyzer(img) # does something .. returns something ..
      
  
  # *** backend methods corresponding to incoming signals ***
  def stop_(self):
    self.running=False
  
  
  def test_(self,test_int=0,test_str="nada"):
    print(self.pre,"test_ signal received with",test_int,test_str)
    
  
  def ping_(self,message="nada"):
    print(self.pre,"At backend: ping_ received",message,"sending it back to front")
    self.sendSignal_(name="pong_o",message=message)
  
  
  # ** frontend methods launching incoming signals
  def stop(self):
    self.sendSignal(name="stop_")
  
  
  def test(self,**kwargs):
    dictionaryCheck(self.incoming_signal_defs["test_"],kwargs)
    kwargs["name"]="test_"
    self.sendSignal(**kwargs)
    
    
  def ping(self,**kwargs):
    dictionaryCheck(self.incoming_signal_defs["ping_"],kwargs)
    kwargs["name"]="ping_"
    self.sendSignal(**kwargs)
  
  
  # ** frontend methods handling received outgoing signals ***
  def pong_o(self,message="nada"):
    print(self.pre,"At frontend: pong got message",message)
    ns=Namespace()
    ns.message=message
    self.signals.pong_o.emit(ns)
  
  
  
class ValkkaMovementDetectorProcess(ValkkaOpenCVProcess):
  
  
  incoming_signal_defs={ # each key corresponds to a front- and backend methods
    "test_"    : {"test_int": int, "test_str": str},
    "stop_"    : [],
    "ping_"    : {"message":str}
    }
  
  outgoing_signal_defs={
    "pong_o"    : {"message":str},
    "start_move": {},
    "stop_move" : {}
    }
  
  # For each outgoing signal, create a Qt signal with the same name.  The frontend Qt thread will read processes communication pipe and emit these signals.
  class Signals(QtCore.QObject):  
    pong_o     =QtCore.pyqtSignal(object)
    start_move =QtCore.pyqtSignal()
    stop_move  =QtCore.pyqtSignal()
  
  
  parameter_defs={
    "n_buffer"   : (int,10),
    "n_bytes"    : int,
    "shmem_name" : str
    }
  
  
  def __init__(self,name,**kwargs):
    super().__init__(name,**kwargs)
    self.signals =self.Signals()
    parameterInitCheck(ValkkaMovementDetectorProcess.parameter_defs, kwargs, self)
    # self.analyzer=MovementDetector(verbose=True)
    self.analyzer=MovementDetector(treshold=0.0001)
  
  
  def cycle_(self):
    index, isize = self.client.pull()
    if (index==None):
      # print(self.pre,"Client timed out..")
      pass
    else:
      # print(self.pre,"Client index, size =",index, isize)
      data=self.client.shmem_list[index]
      img=data.reshape((1080//4,1920//4,3))
      result =self.analyzer(img)
      # print(self.pre,">>>",data[0:10])
      
      if   (result==MovementDetector.state_same):
        pass
      elif (result==MovementDetector.state_start):
        self.sendSignal_(name="start_move")
      elif (result==MovementDetector.state_stop):
        self.sendSignal_(name="stop_move")
      
      
  # ** frontend methods handling received outgoing signals ***
  def start_move(self):
    print(self.pre,"At frontend: got movement")
    self.signals.start_move.emit()
  
  
  def stop_move(self):
    print(self.pre,"At frontend: movement stopped")
    self.signals.stop_move.emit()
  
  
  
class ConfigDialog(QtWidgets.QDialog):
  
  def __init__(self,parent=None):
    super().__init__(parent)
    
    self.pardic={
      "cams"    : [],
      "n720p"   : 10,  # reserve stacks of YUV video frames for various resolutions
      "n1080p"  : 10,
      "n1440p"  : 10,
      "n4K"     : 10,
      "naudio"  : 10,
      "verbose" : 0,
      "msbuftime" :100,
      "live affinity" : -1,
      "gl affinity"   : -1,
      "dec affinity start" : -1,
      "dec affinity stop"  : -1,
      "ok"                 : True
    }
    
    # ["n720p", "n1080p", "n1440p", "n4K", "naudio", "verbose", "live affinity", "gl affinity", "dec affinity start", "dec affinity stop"]
    self.plis=["n720p", "n1080p", "n1440p", "n4K", "naudio", "verbose", "msbuftime", "live affinity", "gl affinity", "dec affinity start", "dec affinity stop"]
    
    self.partag ={}
    self.partext={}
    
    self.lay=QtWidgets.QVBoxLayout(self)
    
    self.upper =QtWidgets.QWidget(self)
    self.lower =QtWidgets.QWidget(self)
    self.lay.addWidget(self.upper)
    self.lay.addWidget(self.lower)
    
    self.lay_upper =QtWidgets.QHBoxLayout(self.upper)
    self.lay_lower =QtWidgets.QHBoxLayout(self.lower)
    
    self.cams  =QtWidgets.QTextEdit(self.upper)
    self.lay_upper.addWidget(self.cams)
    self.pars  =QtWidgets.QWidget(self.upper)
    self.lay_upper.addWidget(self.pars)
    
    self.lay_pars =QtWidgets.QGridLayout(self.pars)
    
    for i, key in enumerate(self.plis):
      t1 = self.partag [key] =QtWidgets.QLabel(key,self.pars)
      t2 = self.partext[key] =QtWidgets.QLineEdit(self.pars)
      self.lay_pars.addWidget(t1,i,0)
      self.lay_pars.addWidget(t2,i,1)
    
    self.save_button    =QtWidgets.QPushButton("SAVE",self.lower)
    self.run_button     =QtWidgets.QPushButton("RUN",self.lower)
    
    self.save_button.  clicked.connect(self.save_button_slot)
    self.run_button.   clicked.connect(self.run_button_slot)
    
    self.lay_lower.addWidget(self.save_button)
    self.lay_lower.addWidget(self.run_button)
    
    self.readPars()
    # print(pre,self.pardic)
    self.putPars()
    
    
  def exec_(self):
    super().exec_()
    return self.pardic
  
    
  def putPars(self):
    for i, key in enumerate(self.plis):
      t2 = self.partext[key]
      t2.setText(str(self.pardic[key]))
    st=""
    for cam in self.pardic["cams"]:
      st+=cam+"\n"
    self.cams.setText(st)
      
    
  def getPars(self):
    """
    print(pre,">>",self.pardic)
    for key in self.pardic:
      print(pre,">>>",key,key.__class__)
    """
    for i, key in enumerate(self.plis):
      # print(pre,">>>>",key,key.__class__)
      # print(pre,">>",key,self.partext[key].text())
      self.pardic[key]=int(self.partext[key].text())
      
    self.pardic["cams"]=[]
    for cam in self.cams.toPlainText().split("\n"):
      address=cam.strip()
      if (len(address)>0 and (address.find("#")==-1)):
        self.pardic["cams"].append(address)
      
    
  def readPars(self):
    try:
      f=open("test_studio_1.config","r")
    except:
      pass
    else:
      self.pardic=json.loads(f.read())
      self.pardic["ok"]=True
      print(pre,">",self.pardic)
      f.close()
    
    
  def savePars(self):
    f=open("test_studio_1.config","w")
    f.write(json.dumps(self.pardic))
    f.close()
    
    
  # *** slots ***
  
  def save_button_slot(self):
    self.getPars()
    self.savePars()
    
    
  def run_button_slot(self):
    self.getPars()
    print(pre,"running with",self.pardic)
    self.done(0)
    
  
  # *** events ***
  
  def closeEvent(self,e):
    self.pardic["ok"]=False
    super(e)
    
    
    
    
class MyGui(QtWidgets.QMainWindow):


  class Frame:
    
    def __init__(self,parent):
      self.widget=QtWidgets.QWidget(parent)
      self.lay  =QtWidgets.QVBoxLayout(self.widget)
      
      self.text =QtWidgets.QLabel("",self.widget)
      self.text_stylesheet=self.text.styleSheet()
      
      self.video=QtWidgets.QFrame(self.widget)
      self.lay.addWidget(self.text)
      self.lay.addWidget(self.video)
      self.text.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)
      self.video.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
      self.set_still()
      
    def setText(self,txt):
      self.text.setText(txt)
      
      
    def getVideoFrameId(self):
      return int(self.video.winId())
      

    def set_still(self):
      self.setText("still")
      self.widget.setStyleSheet(self.text_stylesheet)
      
      
    def set_moving(self):
      self.setText("MOVING")
      self.widget.setStyleSheet("QLabel {border: 2px; border-style:solid; border-color: red; margin:0 px; padding:0 px; border-radius:8px;}")
      


  debug=False
  # debug=True

  def __init__(self,pardic,parent=None):
    super(MyGui, self).__init__()
    # XInitThreads()
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
    
    self.frames     =[] # frames with movement detector alert and video
    self.addresses  =self.pardic["cams"]
    
    for i, address in enumerate(self.addresses):
      fr =self.Frame(self.w)
      print(pre,"setupUi: layout index, address : ",i//4,i%4,address)
      self.lay.addWidget(fr.widget,i//4,i%4)
      self.frames.append((fr,address)) # list of (QFrame, address) pairs

    
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

    tokens        =[]
    self.chains   =[]
    self.processes=[]
    cc=1
    
    a=self.pardic["dec affinity start"]
    
    for frame, address in self.frames:
      # now livethread and openglthread are running
      if (a>self.pardic["dec affinity stop"]): a=self.pardic["dec affinity start"]
      
      print(pre,"openValkka: setting decoder thread on processor",a)
      
      chain=ShmemFilterchain(       # decoding and branching the stream happens here
        livethread  =self.livethread, 
        openglthread=self.openglthread,
        address     =address,
        slot        =cc,
        affinity    =a,
        # this filterchain creates a shared memory server
        shmem_name             ="test_studio_"+str(cc),
        shmem_image_dimensions =(1920//4,1080//4),  # Images passed over shmem are quarter of the full-hd reso
        shmem_image_interval   =1000,               # YUV => RGB interpolation to the small size is done each 1000 milliseconds and passed on to the shmem ringbuffer
        shmem_ringbuffer_size  =10                  # Size of the shmem ringbuffer
        )
    
      shmem_name, n_buffer, n_bytes =chain.getShmemPars()
      # print(pre,"shmem_name, n_buffer, n_bytes",shmem_name,n_buffer,n_bytes)
      
      # process=ValkkaOpenCVProcess("process_"+str(cc),shmem_name=shmem_name, n_buffer=n_buffer, n_bytes=n_bytes)
      process=ValkkaMovementDetectorProcess("process_"+str(cc),shmem_name=shmem_name, n_buffer=n_buffer, n_bytes=n_bytes)
      
      process.signals.start_move.connect(frame.set_moving)
      process.signals.stop_move.connect(frame.set_still)
      
      self.chains.append(chain)
      self.processes.append(process)

      win_id =frame.getVideoFrameId()
      
      token  =self.openglthread.connect(slot=cc,window_id=win_id)
      tokens.append(token)
      
      chain.decodingOn() # tell the decoding thread to start its job
      cc+=1 # TODO: crash when repeating the same slot number ..?
      a +=1
      
      
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
    super().closeEvent(e)


def main():
  app=QtWidgets.QApplication(["test_app"])
  
  
  conf=ConfigDialog()
  pardic=conf.exec_()
  
  print(pre,"got",pardic)

  # return
  
  if (pardic["ok"]):
    mg=MyGui(pardic)
    mg.show()
    app.exec_()


if (__name__=="__main__"):
  main()
 
 
