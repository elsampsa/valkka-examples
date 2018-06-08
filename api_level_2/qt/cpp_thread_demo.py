"""
cpp_thread_demo.py : Launch a cpp thread in python.  That thread uses a callback to send a signal to PyQt's signal/slot system

Copyright 2017 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    cpp_thread_demo.py
@author  Sampsa Riikonen
@date    2017
@version 0.4.7 
@brief   Launch a cpp thread in python.  That thread uses a callback to send a signal to PyQt's signal/slot system
"""

from PyQt5 import QtWidgets, QtCore, QtGui # Qt5
import sys
from valkka.valkka_core import TestThread



class MyGui(QtWidgets.QMainWindow):

  class Signals(QtCore.QObject):  
    counter =QtCore.pyqtSignal(object) # use always object


  def __init__(self,parent=None):
    super(MyGui, self).__init__()
    self.initVars()
    self.setupUi()
    self.startProcesses()
    

  def initVars(self):
    self.signals =self.Signals()
    self.t       =TestThread("thread1")
    
    # The cpp thread launches a callback.  Use any of these:
    #
    self.t.setCallback(self.signals.counter.emit)
    # self.t.setCallback(lambda x: self.signals.counter.emit(x))
    # self.t.setCallback(self.counter_slot_int) 
    
  
  def startProcesses(self):
    self.t.startCall()
    
    
  def stopProcesses(self):
    self.t.stopCall()


  def setupUi(self):
    self.setGeometry(QtCore.QRect(100,100,500,500))
    self.w=QtWidgets.QWidget(self)
    self.setCentralWidget(self.w)
    self.lay=QtWidgets.QVBoxLayout(self.w)
    
    self.message_text=QtWidgets.QTextEdit(self.w)
    self.lay.addWidget(self.message_text)
    
    self.button=QtWidgets.QPushButton("send signal",self.w)
    self.lay.addWidget(self.button)
    
    self.button.clicked. connect(self.t.addCall)
    self.signals.counter.connect(self.counter_slot_int)
    
    
  def counter_callback(self,i):
    print("counter_callback got",i)
    self.signals.counter.emit(i)
    
  
  def counter_slot_int(self,i):
    print("counter_slot got",i)
    self.message_text.insertPlainText(str(i)+" ")
  
  
  def button_slot(self):
    self.t.addCall()
    

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
 
