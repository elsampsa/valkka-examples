"""
xscreen_test.py : Test sending a Qt Widget to another xscreen

Copyright 2018 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    NAME.py
@author  Sampsa Riikonen
@date    2017
@version 0.11.0 
@brief   
"""


# Objective: either move a window to another xscreen or create it there
#
# None of these works:
#
# https://stackoverflow.com/questions/3203095/display-window-full-screen-on-secondary-monitor-using-qt
# http://blog.qt.io/blog/2016/09/19/qt-graphics-with-multiple-displays-on-embedded-linux/
# https://stackoverflow.com/questions/30113311/in-qt-5-whats-the-right-way-to-show-multi-monitor-full-screen-qwidget-windows

# from PyQt5 import QtWidgets, QtCore, QtGui, QtX11Extras # If you use PyQt5, be aware of the licensing consequences
from PySide2 import QtWidgets, QtCore, QtGui, QtX11Extras

import sys
import os

 
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
    self.subwidgets=[]
    self.true_screens=[]


  def dumpScreenInfo(self):
    info=QtX11Extras.QX11Info
    print("info.appScreen",info.appScreen())
    print("info.appScreen",info.appScreen())
    qapp    =QtCore.QCoreApplication.instance()
    screens =qapp.screens()
    print("qapp.screens:",screens,"\n")
    for screen in screens:
      print("\n",screen)
      print(screen.name())
      print(screen.availableSize())
      print(screen.availableVirtualSize())
      # Bingo!  Using the "siblings" screen structure, we can differentiate between separate x-screens vs. virtual screens
      # A parent is included in its own siblings
      print("siblings:")
      for sibling in screen.virtualSiblings():
        print("         ",sibling)
    
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
      
    print("virtual screens",virtual_screens)
    true_screens=list(set(screens)-virtual_screens)
    
    # sort'em
    for screen in true_screens:
      self.true_screens.insert(screens.index(screen),screen)
    
    print("true screens:",self.true_screens)
    
    
  def setupUi(self):
    self.setGeometry(QtCore.QRect(100,100,500,500))
    
    self.w=QtWidgets.QWidget(self)
    self.setCentralWidget(self.w)
    
    self.button=QtWidgets.QPushButton("Jump",self.w)
    self.button.clicked.connect(self.jump_slot)
    
    # self.button2=QtWidgets.QPushButton("Create",self.w)
    # self.button2.clicked.connect(self.create_slot)
    
    # self.button2=QtWidgets.QPushButton("Create",self.w)
    # self.button2.clicked.connect(self.create_slot2)
    
    self.dumpScreenInfo()
    
    
    
  def jump_slot(self):
    print("jump_slot:")
    qapp    =QtCore.QCoreApplication.instance()
    print("jump_slot: qapp.screens:",qapp.screens())
    desktop =qapp.desktop()
    # n_max   =desktop.screenCount()
    n_max   =len(qapp.screens())
    print("jump_slot: number qapp.screens:",n_max)
    self.n +=1
    if (self.n>=n_max):
      self.n=0
    
    # self.n=0
    
    print("jump_slot: going to screen:",self.n)
    
    self.windowHandle().setScreen(qapp.screens()[self.n])
    # self.showFullScreen()
    self.show() # WORKS WITH LATEST PYQT5 5.11.2
    # self.setGeometry(100,100,100,100)
    
    # geom    =desktop.screenGeometry(self.n)    
    # self.move(QtCore.QPoint(geom.x(), geom.y()));
    
    #print("back to 0")
    #self.windowHandle().setScreen(qapp.screens()[0])
    #self.show()
    
    #self.resize(100,100)
    # self.main_widget.showFullScreen();
    
  
  def create_slot(self):
    print("create_slot:")
    qapp    =QtCore.QCoreApplication.instance()
    print("create_slot: qapp.screens:",qapp.screens())
    desktop =qapp.desktop()
    
    print("create_slot: avail geom 0:",desktop.screenGeometry(0))
    print("create_slot: avail geom 1:",desktop.screenGeometry(1))
    
    n_max   =desktop.screenCount()
    print("jump_slot: number of desktops:",n_max)
    
    if (n_max>1):
        print("jump_slot: creating window on second xscreen")
        # w=QtWidgets.QWidget(qapp.screens()[1]) # could we create the window directly on another x screen?
        w=QtWidgets.QWidget()
        w.show()
        w.windowHandle().setScreen(qapp.screens()[1])
        w.showFullScreen()
        w.setGeometry(100,100,100,100)
        self.subwidgets.append(w)
        
    # geom    =desktop.screenGeometry(self.n)    
    # self.move(QtCore.QPoint(geom.x(), geom.y()));
    
    #print("back to 0")
    #self.windowHandle().setScreen(qapp.screens()[0])
    #self.show()
    
    #self.resize(100,100)
    # self.main_widget.showFullScreen();
  
  
  def create_slot2(self):
    print("create_slot:")
    qapp    =QtCore.QCoreApplication.instance()
    print("create_slot: qapp.screens:",qapp.screens())
    desktop =qapp.desktop()
    
    print("create_slot: avail geom 0:",desktop.screenGeometry(0))
    print("create_slot: avail geom 1:",desktop.screenGeometry(1))
    
    n_max   =desktop.screenCount()
    print("jump_slot: number of desktops:",n_max)
    
    if (n_max>1):
        print("jump_slot: creating window on second xscreen")
        os.environ["DISPLAY"]=":0.1" # nopes .. does not work
        w=QtWidgets.QWidget()
        w.show()
        # w.windowHandle().setScreen(qapp.screens()[1])
        #w.showFullScreen()
        w.setGeometry(100,100,100,100)
        self.subwidgets.append(w)
        
    # geom    =desktop.screenGeometry(self.n)    
    # self.move(QtCore.QPoint(geom.x(), geom.y()));
    
    #print("back to 0")
    #self.windowHandle().setScreen(qapp.screens()[0])
    #self.show()
    
    #self.resize(100,100)
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
    for w in self.subwidgets:
        w.close()
    e.accept()


def main():
  app=QtWidgets.QApplication(["test_app"])
  mg=MyGui()
  mg.show()
  app.exec_()


if (__name__=="__main__"):
  main()
 
