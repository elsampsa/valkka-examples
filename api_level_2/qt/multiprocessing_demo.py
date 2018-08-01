"""
multiprocessing_demo.py : Use Qt with python multiprocesses

Copyright 2018 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    multiprocessing_demo.py
@author  Sampsa Riikonen
@date    2018
@version 0.5.2 
@brief   Use Qt with python multiprocesses
"""

# from PyQt5 import QtWidgets, QtCore, QtGui # If you use PyQt5, be aware of the licensing consequences
from PySide2 import QtWidgets, QtCore, QtGui
import sys
import time
from valkka.api2 import ValkkaProcess
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
    "pong_o"    : {"message":str}
    }
  
  
  def __init__(self):
    super().__init__("TestProcess") # don't forget this!
    self.pre="QValkkaTestProcess: "
    
  def preRun_(self):
    """ Run immediately after fork
    """
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
    

class MyGui(QtWidgets.QMainWindow):


  def __init__(self,parent=None):
    super(MyGui, self).__init__()
    self.initVars()
    self.setupUi()
    self.startProcesses()
    

  def initVars(self):
    self.p =TestProcess()


  def startProcesses(self):
    self.p.start()
    
    
  def stopProcesses(self):
    self.p.stop()


  def setupUi(self):
    self.setGeometry(QtCore.QRect(100,100,500,500))
    self.w=QtWidgets.QWidget(self)
    self.setCentralWidget(self.w)
    
    self.lay=QtWidgets.QVBoxLayout(self.w)
    self.button=QtWidgets.QPushButton("send signal",self.w)
    self.lay.addWidget(self.button)
    
    self.button.clicked.connect(self.p.button_slot)
    
  
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
 
