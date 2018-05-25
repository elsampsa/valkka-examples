"""
demo_base.py : Common classes, etc. for the qt streaming, shared-memory and opecv demos

Copyright 2017, 2018 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    demo_base.py
@author  Sampsa Riikonen
@date    2018
@version 0.4.5 
@brief   
"""

from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import json
import os

pre="demo_base : "


class TestWidget0(QtWidgets.QWidget):
  
  
  def mouseDoubleClickEvent(self,e):
        print("double click!")

  
def getForeignWidget(parent, win_id): 
    """Valkka creates a window.  The window is used to generate the widget.. however.. here we loose the interaction with the window .. clicks on it, etc. (were detached from the qt system)
    """
    # some interesting flags for the createWindowContainer method: QtCore.Qt.ForeignWindow QtCore.Qt.X11BypassWindowManagerHint
    # other things: QtGui.QSurface(QtGui.QSurface.OpenGLSurface), q_widget.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
    q_window =QtGui.QWindow.fromWinId(win_id)
    
    q_widget    =QtWidgets.QWidget.createWindowContainer(q_window,parent=parent)
    # q_widget.activateWindow()
    
    return q_widget
  
  
class WidgetPair:
  """Creates a "foreign" QWidget by using the X window id win_id.  Another "top" widget is placed on top of the foreign widget that catches the mouse gestures.  
  
  :param parent:       Parent (a QWidget) of the widget pair
  :param win_id:       An X-window id
  :param widget_class: Class for the top widget
  """
  
  def __init__(self,parent,win_id,widget_class):
    self.foreign_window =QtGui.QWindow.fromWinId(win_id)
    self.foreign_widget =QtWidgets.QWidget.createWindowContainer(self.foreign_window,parent=parent)
    
    self.widget =widget_class(self.foreign_widget)
    self.lay   =QtWidgets.QHBoxLayout(self.foreign_widget)
    self.lay.addWidget(self.widget)
    
    
  def getWidget(self):
    return self.foreign_widget




 
class ConfigDialog(QtWidgets.QDialog):
  """A configuration dialog for test/demo programs
  """
  
  def setConfigPars(self):
    """Re-define in the child class
    """
    self.tooltips={        # how about some tooltips?
      }
    self.pardic.update({}) # add more parameter key/value pairs
    self.plis +=[]         # list of parameter keys that are saved to config file
    self.config_fname="test_studio_1.config" # define config file
  
  
  def extra(self): # anything extra .. called in the end of __init__
    pass
  
  
  def __init__(self,parent=None):
    super().__init__(parent)
    
    self.pardic={
      "cams"    : [],
      "n_720p"   : 10,  # reserve stacks of YUV video frames for various resolutions
      "n_1080p"  : 10,
      "n_1440p"  : 10,
      "n_4K"     : 10,
      "naudio"  : 10,
      "verbose" : 0,
      "msbuftime" :100,
      "live affinity" : -1,
      "gl affinity"   : -1,
      "dec affinity start" : -1,
      "dec affinity stop"  : -1,
      "ok"                 : True
    }
    
    # ["n_720p", "n_1080p", "n_1440p", "n_4K", "naudio", "verbose", "live affinity", "gl affinity", "dec affinity start", "dec affinity stop"]
    self.plis=["n_720p", "n_1080p", "n_1440p", "n_4K", "naudio", "verbose", "msbuftime", "live affinity", "gl affinity", "dec affinity start", "dec affinity stop"]
    
    self.setConfigPars() # custom pars
    
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
      if (key in self.tooltips):
        t2.setToolTip(self.tooltips[key])
    
    self.save_button    =QtWidgets.QPushButton("SAVE",self.lower)
    self.run_button     =QtWidgets.QPushButton("RUN (QT)",self.lower)
    self.run2_button    =QtWidgets.QPushButton("RUN",self.lower)
    self.ffplay_button  =QtWidgets.QPushButton("FFPLAY",self.lower)
    self.vlc_button     =QtWidgets.QPushButton("VLC",self.lower)
    
    self.save_button.  clicked.connect(self.save_button_slot)
    self.run_button.   clicked.connect(self.run_button_slot)
    self.run2_button.  clicked.connect(self.run2_button_slot)
    self.ffplay_button.clicked.connect(self.ffplay_button_slot)
    self.vlc_button.   clicked.connect(self.vlc_button_slot)
    
    self.lay_lower.addWidget(self.save_button)
    self.lay_lower.addWidget(self.run_button)
    self.lay_lower.addWidget(self.run2_button)
    self.lay_lower.addWidget(self.ffplay_button)
    self.lay_lower.addWidget(self.vlc_button)
    
    self.readPars()
    # print(pre,self.pardic)
    self.putPars()
    
    self.extra()
    
    
  def exec_(self):
    super().exec_()
    return self.pardic
  
    
  def putPars(self):
    for i, key in enumerate(self.plis):
      if ((key not in self.partext) or (key not in self.pardic)):
        raise(AssertionError("Your config file "+self.config_fname+" is corrupt or out-of-date.  Remove it and try again"))
      t2 = self.partext[key]
      t2.setText(str(self.pardic[key]))
    st=""
    for cam in self.pardic["cams"]:
      st+=cam+"\n"
    self.cams.setText(st)
      
    
  def getPars(self):
    """
    print(pre,self.pardic)
    for key in self.pardic:
      print(pre,key,key.__class__)
    """
    for i, key in enumerate(self.plis):
      # print(pre,key,key.__class__)
      # print(pre,key,self.partext[key].text())
      self.pardic[key]=int(self.partext[key].text())
      
    self.pardic["cams"]=[]
    for cam in self.cams.toPlainText().split("\n"):
      address=cam.strip()
      if (len(address)>0 and (address.find("#")==-1)):
        self.pardic["cams"].append(address)
      
    
  def readPars(self):
    try:
      f=open(self.config_fname,"r")
    except:
      pass
    else:
      self.pardic=json.loads(f.read())
      self.pardic["ok"]=True
      print(pre,">",self.pardic)
      f.close()
    
    
  def savePars(self):
    f=open(self.config_fname,"w")
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
    
    
  def run2_button_slot(self):
    self.getPars()
    self.pardic["no_qt"]=True
    print(pre,"running with",self.pardic)
    self.done(0)
    
    
  def ffplay_button_slot(self):
    self.getPars()
    for cam in self.pardic["cams"]:
      os.system("ffplay "+cam+" &")
      
  
  def vlc_button_slot(self):
    self.getPars()
    for cam in self.pardic["cams"]:
      os.system("vlc "+cam+" &")
  
    
    
  # *** events ***
  
  def closeEvent(self,e):
    self.pardic["ok"]=False
    super().closeEvent(e)
    # e.accept()
    

 
 
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
    pass

  def setupUi(self):
    self.setGeometry(QtCore.QRect(100,100,500,500))
    
    self.w=QtWidgets.QWidget(self)
    self.setCentralWidget(self.w)
    
  
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
 
