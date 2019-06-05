"""
multiprocessing_demo.py : Use Qt with python multiprocesses.  Couple to Qt signal/slot system

Copyright 2018 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    multiprocessing_demo.py
@author  Sampsa Riikonen
@date    2018
@version 0.12.0 
@brief   Use Qt with python multiprocesses.  Couple to Qt signal/slot system
"""

# from PyQt5 import QtWidgets, QtCore, QtGui # If you use PyQt5, be aware of the licensing consequences
from PySide2 import QtWidgets, QtCore, QtGui
import sys
import time
from valkka.api2 import ValkkaProcess, safe_select
from valkka.api2 import dictionaryCheck


class TestProcess(ValkkaProcess):
  """A multiprocess with Qt signals
  """
  
  incoming_signal_defs={ # each key corresponds to a backend method
    "test_"    : {"test_int": int, "test_str": str},
    "stop_"    : [],
    "ping_"    : {"message":str},
    "button_"  : []
    }
  
  outgoing_signal_defs={ # each key corresponds to a frontend method
    "pong_o"    : {"message":str},
    "counter"   : {"value":str}
    }
  
  # For each outgoing signal, create a Qt signal with the same name.  The frontend QThread will read processes communication pipe and emit the signals.
  class Signals(QtCore.QObject):  
    # PyQt5:
    """
    pong_o  =QtCore.pyqtSignal(object)
    counter =QtCore.pyqtSignal(str)
    """
    # PySide2:
    pong_o  =QtCore.Signal(object)
    counter =QtCore.Signal(str)
  
  
  def __init__(self,name):
    self.name=name
    super().__init__(self.name) # don't forget this!
    self.pre="QValkkaTestProcess: "+self.name
    self.signals =self.Signals() # instantiate a set of qt signals
    
    
  def preRun_(self):
    """ Run immediately after fork
    """
    super().preRun_()
    print(self.pre,"hello!")
    self.counter=0
  
  
  def postRun_(self):
    """ Run immediately after process exit
    """
    print(self.pre,"bye!")
    
    
  def cycle_(self):
    """ Process action is defined here
    """
    time.sleep(1)
    print(self.pre,"still alive, counter=",self.counter)
    self.sendSignal_(name="counter",value=str(self.counter)) # send signal to frontend
    self.counter+=1
    
  
  # *** backend methods corresponding to incoming signals ***
  def stop_(self):
    self.running=False # controls the execution of the main loop
  
  
  def test_(self,test_int=0,test_str="nada"):
    print(self.pre,"test_ signal received with",test_int,test_str)
    
  
  def ping_(self,message="nada"):
    print(self.pre,"At backend: ping_ received",message,"sending it back to front")
    self.sendSignal_(name="pong_o",message=message)
    
    
  def button_(self):
    print(self.pre,"Got button signal - will increase the counter by 100")
    self.counter+=100
  
  
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
  
  
  def button_slot(self):
    self.sendSignal(name="button_")
  
  
  # ** frontend methods handling outgoing signals ***
  def pong_o(self,message="nada"):
    print(self.pre,"At frontend: pong got message",message)
    ns=Namespace()
    ns.message=message
    self.signals.pong_o.emit(ns)


  def counter(self,value="0"):
    print(self.pre,"Emitting counter signal")
    self.signals.counter.emit(value+" ")
    


class QValkkaThread(QtCore.QThread):
  """A QThread that sits between multiprocesses message pipe and Qt's signal system
  
  After ValkkaProcess instances have been given to this thread, they are accessible with:
  .process_name
  [process_index]
      
  The processes have methods that launch ingoing signals (like ping(message="hello")) and Qt signals that can be connected to slots (e.g. process.signals.pong_o.connect(slot))
  """
  
  def __init__(self,timeout=1,processes=[]):
    super().__init__()
    self.pre=self.__class__.__name__+" : "
    self.timeout=timeout
    self.processes=processes
    self.process_by_pipe={}
    self.process_by_name={}
    for p in self.processes:
      self.process_by_pipe[p.getPipe()]=p
      self.process_by_name[p.name]     =p


  def preRun(self):
    pass
  
  
  def postRun(self):
    pass
    
    
  def run(self):
    self.preRun()
    self.loop=True
    
    rlis=[]; wlis=[]; elis=[]
    for key in self.process_by_pipe:
      rlis.append(key)
    
    while self.loop:
      tlis=safe_select(rlis,wlis,elis,timeout=self.timeout)
      for pipe in tlis[0]:
        p=self.process_by_pipe[pipe] # let's find the process that sent the message to the pipe
        # print("receiving from",p,"with pipe",pipe)
        st=pipe.recv() # get signal from the process
        # print("got from  from",p,"with pipe",pipe,":",st)
        p.handleSignal(st)
    
    self.postRun()
    print(self.pre,"bye!")
 
 
  def stop(self):
    self.loop=False
    self.wait()
 
 
  def __getattr__(self,attr):
    return self.process_by_name[attr]
  
  
  def __getitem__(self,i):
    return self.processes[i]



class MyGui(QtWidgets.QMainWindow):


  def __init__(self,parent=None):
    super(MyGui, self).__init__()
    self.initVars()
    self.setupUi()
    self.startProcesses()
    

  def initVars(self):
    self.p1       =TestProcess("process 1")
    self.p2       =TestProcess("process 2")
    self.qthread  =QValkkaThread(processes=[self.p1,self.p2])


  def startProcesses(self):
    self.p1.start()
    time.sleep(0.2)
    self.p2.start()
    self.qthread.start()
    
    
  def stopProcesses(self):
    self.p1.stop()
    self.p2.stop()
    self.qthread.stop()


  def setupUi(self):
    self.setGeometry(QtCore.QRect(100,100,500,500))
    self.w=QtWidgets.QWidget(self)
    self.setCentralWidget(self.w)
    self.lay=QtWidgets.QVBoxLayout(self.w)
    
    self.message_text=QtWidgets.QTextEdit(self.w)
    self.lay.addWidget(self.message_text)
    
    self.button=QtWidgets.QPushButton("send signal",self.w)
    self.lay.addWidget(self.button)
    
    self.button.clicked.connect(self.p1.button_slot)
    self.p1.signals.counter.connect(self.message_text.insertPlainText)
    
    
  
  def closeEvent(self,e):
    print("closeEvent!")
    e.accept()
    self.stopProcesses()


def main():
  app=QtWidgets.QApplication(["test_app"])
  mg=MyGui()
  mg.show()
  app.exec_()


if (__name__=="__main__"):
  main()
 
