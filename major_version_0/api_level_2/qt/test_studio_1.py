"""
test_studio_1.py : test live streaming conveniently from Qt

Copyright 2017 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    test_studio_1.py
@author  Sampsa Riikonen
@date    2018
@version 0.1
@brief   test live streaming conveniently from Qt
"""

from PyQt5 import QtWidgets, QtCore, QtGui # Qt5
import sys
import json
from valkka.api2.threads import LiveThread, OpenGLThread
from valkka.api2.chains import BasicFilterchain

 
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
      "live affinity" : -1,
      "gl affinity"   : -1,
      "dec affinity start" : -1,
      "dec affinity stop"  : -1
    }
    
    # ["n720p", "n1080p", "n1440p", "n4K", "naudio", "verbose", "live affinity", "gl affinity", "dec affinity start", "dec affinity stop"]
    self.plis=["n720p", "n1080p", "n1440p", "n4K", "naudio", "verbose", "live affinity", "gl affinity", "dec affinity start", "dec affinity stop"]
    
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
    
    self.save_button =QtWidgets.QPushButton("SAVE",self.lower)
    self.run_button  =QtWidgets.QPushButton("RUN",self.lower)
    
    self.save_button.clicked.connect(self.save_button_slot)
    self.run_button.clicked.connect(self.run_button_slot)
    
    self.lay_lower.addWidget(self.save_button)
    self.lay_lower.addWidget(self.run_button)
    
    self.readPars()
    # print(self.pardic)
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
    print(">>",self.pardic)
    for key in self.pardic:
      print(">>>",key,key.__class__)
    """
    for i, key in enumerate(self.plis):
      # print(">>>>",key,key.__class__)
      # print(">>",key,self.partext[key].text())
      self.pardic[key]=int(self.partext[key].text())
      
    self.pardic["cams"]=[]
    for cam in self.cams.toPlainText().split("\n"):
      address=cam.strip()
      if (len(address)>0):
        self.pardic["cams"].append(address)
      
    
  def readPars(self):
    try:
      f=open("test_studio_1.config","r")
    except:
      pass
    else:
      self.pardic=json.loads(f.read())
      print(">",self.pardic)
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
    print("running with",self.pardic)
    self.done(0)
    
    
    
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
    self.start_streams()
    
    
  def initVars(self):
    pass


  def setupUi(self):
    self.setGeometry(QtCore.QRect(100,100,800,800))
    self.w=QtWidgets.QWidget(self)
    self.setCentralWidget(self.w)
    self.lay=QtWidgets.QGridLayout(self.w)
    
    self.videoframes=[]
    self.addresses=self.pardic["cams"]
    
    for i, address in enumerate(self.addresses):
      fr=QtWidgets.QFrame(self.w)
      print("setupUi: layout index, address : ",i//4,i%4,address)
      self.lay.addWidget(fr,i//4,i%4)
      self.videoframes.append((fr,address)) # list of (QFrame, address) pairs
    
    
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
      affinity=self.pardic["gl affinity"]
      )

    tokens     =[]
    self.chains=[]
    cc=1
    
    a=self.pardic["dec affinity start"]
    
    for qframe, address in self.videoframes:
      # now livethread and openglthread are running
      if (a>self.pardic["dec affinity stop"]): a=self.pardic["dec affinity start"]
      
      print("openValkka: setting decoder thread on processor",a)
      
      chain=BasicFilterchain(       # decoding and branching the stream happens here
        livethread  =self.livethread, 
        openglthread=self.openglthread,
        address     =address,
        slot        =cc,
        affinity    =a
        )
  
      self.chains.append(chain) # important .. otherwise chain will go out of context and get garbage collected ..

      win_id =int(qframe.winId())
      token  =self.openglthread.connect(slot=cc,window_id=win_id)
      tokens.append(token)
      
      chain.decodingOn() # tell the decoding thread to start its job
      cc+=1 # TODO: crash when repeating the same slot number ..?
      a +=1
      
  
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
  
  
  conf=ConfigDialog()
  pardic=conf.exec_()
  
  print("got",pardic)
  
  mg=MyGui(pardic)
  mg.show()
  app.exec_()


if (__name__=="__main__"):
  main()
 
 
