"""
xscreen_test.py : Test sending a Qt Widget to another xscreen

Copyright 2018 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    NAME.py
@author  Sampsa Riikonen
@date    2017
@version 0.5.0 
@brief   
"""

from PyQt5 import QtWidgets, QtCore, QtGui # Qt5
import sys

 
class MyGui(QtWidgets.QMainWindow):

  debug=False
  # debug=True

  def __init__(self,parent=None):
    super(MyGui, self).__init__()
    self.initVars()
    self.setupUi()
    if (self.debug): 
      return
    self.openValkka()
    self.start_streams()
    
    
  def initVars(self):
    self.n=0


  def setupUi(self):
    self.setGeometry(QtCore.QRect(100,100,500,500))
    
    self.w=QtWidgets.QWidget(self)
    self.setCentralWidget(self.w)
    
    self.button=QtWidgets.QPushButton("Jump",self.w)
    self.button.clicked.connect(self.jump_slot)
    
    
  def jump_slot(self):
    print("jump_slot:")
    qapp    =QtCore.QCoreApplication.instance()
    desktop =qapp.desktop()
    n_max   =desktop.screenCount()
    print("jump_slot: number of desktops:",n_max)
    self.n +=1
    if (self.n>=n_max):
      self.n=0
    print("jump_slot: going to desktop:",self.n)
    
    geom    =desktop.screenGeometry(self.n)    
    self.move(QtCore.QPoint(geom.x(), geom.y()));
    # self.main_widget.resize(geom.width(), geom.height());
    # self.main_widget.showFullScreen();
    
    
    
  
  def openValkka(self):
    pass
    
  
  def closeValkka(self):
    pass
  
  
  def start_streams(self):
    pass
    
    
  def stop_streams(self):
    pass
    
  def closeEvent(self,e):
    print("closeEvent!")
    self.stop_streams()
    self.closeValkka()
    e.accept()


def main():
  app=QtWidgets.QApplication(["test_app"])
  mg=MyGui()
  mg.show()
  app.exec_()


if (__name__=="__main__"):
  main()
 
