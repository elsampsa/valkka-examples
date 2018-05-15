"""
demo_analyzer_process.py : Use analyzers from the local file "analyzer.py" in a QValkkaOpenCVProcess multiprocess

Copyright 2017, 2018 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    demo_analyzer_process.py
@author  Sampsa Riikonen
@date    2017
@version 0.4.0 
@brief   Use analyzers from the local file "analyzer.py" in a QValkkaOpenCVProcess multiprocess


When using python multiprocesses with Qt, we need a frontend thread that reads the process communication pipes and turns the messages sent by the process into Qt signals.
"""


from PyQt5 import QtWidgets, QtCore, QtGui # Qt5

# Local imports from this directory
from demo_multiprocess import QValkkaOpenCVProcess
from analyzer import MovementDetector



class QValkkaMovementDetectorProcess(QValkkaOpenCVProcess):
  
  
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
  
  
  def __init__(self,name,**kwargs):
    super().__init__(name,**kwargs) # does parameterInitCheck
    self.signals =self.Signals()
    # # parameterInitCheck(QValkkaMovementDetectorProcess.parameter_defs, kwargs, self)
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
      try:
        img=data.reshape((self.image_dimensions[1],self.image_dimensions[0],3))
      except:
        print("QValkkaMovementDetectorProcess: WARNING: could not reshape image")
        pass
      else:
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
  
  
 
def test1():
  pass
  

def main():
  pre="main :"
  print(pre,"main: arguments: ",sys.argv)
  if (len(sys.argv)<2):
    print(pre,"main: needs test number")
  else:
    st="test"+str(sys.argv[1])+"()"
    exec(st)
  
  
if (__name__=="__main__"):
  main()
