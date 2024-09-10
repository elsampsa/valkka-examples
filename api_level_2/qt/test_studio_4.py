"""
test_studio_4.py : Test live streaming with Qt.  Jump video from one x-screen (and gpu) to another

(c) Copyright 2017-2024 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    test_studio_2.py
@author  Sampsa Riikonen
@date    2018
@version 1.6.1 
@brief   Test live streaming with Qt


In the main text field, write live video sources, one to each line, e.g.

::

    rtsp://admin:admin@192.168.1.10
    rtsp://admin:admin@192.168.1.12
    multicast.sdp
    multicast2.dfp

Reserve enough frames into the pre-reserved frame stack.  There are stacks for 720p, 1080p, etc.  The bigger the buffering time "msbuftime" (in milliseconds), the bigger stack you'll be needing.

When affinity is greater than -1, the processes are bound to a certain processor.  Setting "live affinity" to 0, will bind the Live555 thread to processor one.  Setting "dec affinity start" to 1 and "dec affinity start 3" will bind the decoding threads to processors 1-3.  (first decoder process to 1, second to 2, third to 3, fourth to 1 again, etc.)

If replicate is 10, then each video is replicated 10 times.  It is _not_ decoded 10 times, but just copied to 10 more x windoses.

It's very important to disable vertical sync in OpenGL rendering..!  Otherwise your *total* framerate is limited to 60 fps.  Disabling vsync can be done in mesa-based open source drives with:

::

    export vblank_mode=0

and in nvidia proprietary drivers with

::

    export __GL_SYNC_TO_VBLANK=0

For benchmarking purposes, you can launch the video streams with:

  -PyQt created X windowses (this is the intended use case) : RUN(QT)
  -With X windowses created by valkka : RUN
  -With ffplay or vlc (if you have them installed)


This Qt test program produces a config file.  You might want to remove that config file after updating the program.
"""

# from PyQt5 import QtWidgets, QtCore, QtGui # If you use PyQt5, be aware of the licensing consequences
from PySide2 import QtWidgets, QtCore, QtGui
import sys
import json
import os
import time
from valkka.api2 import LiveThread, OpenGLThread
from valkka.api2.logging import setValkkaLogLevel, loglevel_silent, loglevel_crazy
from valkka.core import ValkkaXInitThreads

# Local imports form this directory
from manager import ManagedFilterchain
from port import ViewPort
from demo_base import ConfigDialog, TestWidget0, getForeignWidget, WidgetPair, DesktopHandler, QuickMenu, QuickMenuElement

pre="test_studio_4 : " # aux string for debugging

# setValkkaLogLevel(loglevel_debug)
# ValkkaXInitThreads()

class MyConfigDialog(ConfigDialog):
  
  def setConfigPars(self):
    self.tooltips={        # how about some tooltips?
      }
    # define customizable parameters
    self.pardic.update({
      "replicate"          : 1
      })
    # self.plis defines parameters to be saved on the disk
    self.plis +=["replicate"]
    self.config_fname="test_studio_4.config" # define the config file name
  
  
  
class GPUHandler:
  """Handles an OpenGLThread for each separate GPU
  """
  
  def __init__(self, pardic):
    self.pardic=pardic
    self.true_screens =[]
    self.openglthreads=[]
    self.findXScreens()
    
    # self.true_screens=[self.true_screens[0]]
    
    for n_gpu, screen in enumerate(self.true_screens):
    
      x_connection=":0."+str(n_gpu)
      # x_connection=":0.1"
      # x_connection=":1.0" # nopes
    
      print(pre,"GPUHandler: starting OpenGLThread with",x_connection)
    
      openglthread=OpenGLThread(     # starts frame presenting services
        name    ="gpu_"+str(n_gpu),
        n_720p   =self.pardic["n_720p"],   # reserve stacks of YUV video frames for various resolutions
        n_1080p  =self.pardic["n_1080p"],
        n_1440p  =self.pardic["n_1440p"],
        n_4K     =self.pardic["n_4K"],
        verbose =False,
        msbuftime=self.pardic["msbuftime"],
        affinity=self.pardic["gl affinity"],
        x_connection =x_connection
        )
      
      print(pre,"GPUHandler: OpenGLThread started")

      self.openglthreads.append(openglthread)
      
    if (self.openglthreads[0].hadVsync()):
      w=QtWidgets.QMessageBox.warning(None,"VBLANK WARNING","Syncing to vertical refresh enabled\n THIS WILL DESTROY YOUR FRAMERATE\n Disable it with 'export vblank_mode=0' for nvidia proprietary drivers, use 'export __GL_SYNC_TO_VBLANK=0'")
    
    
  def findXScreens(self):
    qapp    =QtCore.QCoreApplication.instance()
    screens =qapp.screens()
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
      
    # print("GPUHandler: findXScreens: virtual screens",virtual_screens)
    true_screens=list(set(screens)-virtual_screens)
    
    # sort'em
    for screen in true_screens:
      self.true_screens.insert(screens.index(screen),screen)
    
    print("GPUHandler: findXScreens: true screens:",self.true_screens)
    
    
  def close(self):
    for openglthread in self.openglthreads:
      openglthread.close()
    
    

class VideoContainer:
  """
  
  - Create and manage a ViewPort instance (encapsulates x window id and x screen number)
  
  - A method that is given the stream parameters .. this would be used by the drag'n'drop in the future.  setStream(stream)
  - Change x screen method
  
  - setStream(pars)
    - pars: info about the stream, most importantly, the slot number
    - VideoContainer adds its own information and ..
    - .. calls ResourceManager(pars,view_port)
      => ResourceManager has the ManagedFilterchain instances .. chooses the correct one .. and calls addViewPort(view_port)


  ResourceManager (not using this..)
    -ManagedFilterChain(s) instances

  VideoContainer
    - ViewPort instance

  drag'n'drop => pars => VideoContainer => ViewPort
  => ResourceManager => ManagedFilterchain(s)

  References:
    VideoContainer -> ViewPort
    ManagedFilterchain -> ViewPort

  - GPUHandler finds X screens and instantiates OpenGLThreads
  - OpenGLThreads are passed to ManagedFilterchain(s) when they're instantiated
  - Create a minimalistic GUI:
    * Create a new window => Creates a new VideoContainer on x-screen 0
    * Exit => closeEvent => closes all VideoContainers
    
  - VideoContainer initialized with a list of QScreen instances
  - VideoContainer's switch x-screen button => call makeWidget(QScreen) .. updates self.win_id .. updates self.view_port.x_screen_num (call view_port.setXScreenNum())
    => calls ResourceManager(pars,view_port)
    
    
  - Take stuff from the gui tools module .. create a separate gui tools here
    
  """
  def __init__(self,gpu_handler,filterchains):
    self.pre="VideoContainer: "
    self.gpu_handler  =gpu_handler
    self.filterchains =filterchains
    self.closed       =False
    
    self.n            =0 # x-screen number
    self.openglthread =self.gpu_handler.openglthreads[self.n]
    self.index        =-1 # no video set

    qapp    =QtCore.QCoreApplication.instance()
    desktop =qapp.desktop()

    self.viewport =ViewPort(window_id=0, x_screen_num=self.n)

    self.makeWidget(self.gpu_handler.true_screens[self.n]) # create widget into a certain xscreen


  def setStream(self,pars):
    """
    :param pars:  Generic parameters. Used to identify the filterchain
    :return:      None
    """
    assert(pars.__class__==dict)
    assert("index" in pars)
    index=pars["index"]
    assert(index.__class__==int)

    try:
      fc=self.filterchains[index]
    except IndexError:
      print(self.pre,"setStream: no such filterchain",index)
      return

    assert(issubclass(fc.__class__,ManagedFilterchain))

    self.index =index
    self.viewport.setXScreenNum(self.n)
    self.viewport.setWindowId  (self.win_id)

    fc.addViewPort(self.viewport)


  def remStream(self):
    index=self.index
    print(self.pre,"remStream: index",index)
    if (index<0):
      return

    try:
      fc = self.filterchains[index]
    except IndexError:
      print(self.pre, "setStream: no such filterchain", index)
      return

    assert (issubclass(fc.__class__, ManagedFilterchain))

    fc.delViewPort(self.viewport)


  def makeWidget(self,qscreen):
    """ Widget needs to be re-created when jumping from one x-screen to another
    
    :param qscreen:   QScreen
    """
    
    class MyWidget(QtWidgets.QWidget):
      
      class MySignals(QtCore.QObject):
        close =QtCore.Signal(object)
        
        
      def __init__(self,parent=None):
        super().__init__(parent)
        self.signals =self.MySignals()
      
      
      def closeEvent(self, e):
        self.signals.close.emit(e)
        e.accept()
        
    
    self.main_widget=MyWidget()
    self.main_widget.signals.close.connect(self.close_slot)
    
    self.main_widget.show()
    
    self.main_widget.windowHandle().setScreen(qscreen)
    self.lay        =QtWidgets.QVBoxLayout(self.main_widget)

    self.video      =TestWidget0(self.main_widget)
    self.lay.addWidget(self.video)
    self.video.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    if (len(self.gpu_handler.true_screens)>1):
      self.button     =QtWidgets.QPushButton("Change Screen",self.main_widget)
      self.lay.addWidget(self.button)
      self.button.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
      self.button.clicked.connect(self.cycle_slot)

    self.win_id = int(self.video.winId())

    # create drop-down menu for all cameras?
    self.dropdown =QtWidgets.QComboBox(self.main_widget)
    self.dropdown.addItem("<Choose A Camera>", -1)
    for index, fc in enumerate(self.filterchains):
      assert(fc.__class__==ManagedFilterchain) # filterchains should have a copy of the parameter set (=rtsp address, date when added, etc.) that invoked them
      self.dropdown.addItem(fc.address,index) # QComboBox.addItem(str,qvariant) .. now qvariant is just a python object! :)

    self.lay.addWidget(self.dropdown)

    self.dropdown.currentIndexChanged.connect(self.dropdown_changed_slot)

    self.main_widget.show()

    # this will call dropdown_changed_slot and activate the video if needed
    # index = filterchain index
    # argument of self.dropdown.setCurrentIndex = index of the QComboBox dropdown item
    if self.index>=0:
      self.dropdown.setCurrentIndex(self.index+1) # TODO: here self.index maps from parameters => filterchain .. parameters => menu item index mapping required as well

    
  def cycle_slot(self):
    """Cycle from one X-Screen to another
    """
    # viewport has x screen number and x window id
    self.n +=1
    if (self.n>=len(self.gpu_handler.true_screens)):
      self.n=0
    print("cycle_slot: going to screen:",self.n)

    # """
    if (self.index>-1): # video has been chosen..
      fc = self.filterchains[self.index]
      fc.delViewPort(self.viewport)
    # """

    # WORKS WITH LATEST PYQT5 5.11.2
    self.makeWidget(self.gpu_handler.true_screens[self.n])

    # """
    if (self.index>-1):
      fc.addViewPort(self.viewport)
    # """


  def dropdown_changed_slot(self,i):
    print(self.pre,"dropdown_changed_slot: combobox selection now",i)
    index=self.dropdown.itemData(i)
    print(self.pre,"dropdown_changed_slot: index",index)
    if (index<0):
      self.remStream()
    else:
      self.setStream({"index":index})


  def close_slot(self):
    self.close()


  def mouseDoubleClickEvent(self,e):
    print("double click!")
        
  
  def getVideoWidget(self):
    return self.video

  
  def getWidget(self):
    return self.main_widget


  def close(self):
    if (self.closed):
      return
    self.remStream()
    self.openglthread =None
    self.gpu_handler  =None
    self.filterchains =[]
    self.main_widget.close()
    self.main_widget.deleteLater()
    self.closed=True


class MyGui(QtWidgets.QMainWindow):

  debug=False
  # debug=True

  def __init__(self,pardic,parent=None):
    super(MyGui, self).__init__()
    # print(pre,"Qapp=",QtCore.QCoreApplication.instance())
    self.pardic=pardic
    self.initVars()
    self.setupUi()
    if (self.debug): 
      return
    self.openValkka()
    self.start_streams()
    
    
  def initVars(self):
    self.videocontainers = []
    self.chains = []


  def makeMenus(self):

    class FileMenu(QuickMenu):
      title="File"
      elements=[
        QuickMenuElement(title="Add New View"),
        QuickMenuElement(title="Exit")
        ]

    self.filemenu=FileMenu(self)

    self.filemenu.add_new_view.triggered.connect(self.add_new_view_slot)
    self.filemenu.exit.triggered.connect(self.exit_slot)


  def add_new_view_slot(self):
    print("add new view")
    self.videocontainers.append(VideoContainer(self.gpu_handler,self.chains))


  def exit_slot(self):
    self.close()


  def setupUi(self):
    self.desktop_handler =DesktopHandler()
    print(self.desktop_handler)
    
    self.setGeometry(QtCore.QRect(100,100,800,800))
    self.w=QtWidgets.QWidget(self)
    self.setCentralWidget(self.w)
    self.lay=QtWidgets.QGridLayout(self.w)

    self.makeMenus()
    self.addresses=self.pardic["cams"]
    
  
  def openValkka(self):
    self.livethread=LiveThread(         # starts live stream services (using live555)
      name   ="live_thread",
      # verbose=True,
      verbose=False,
      affinity=self.pardic["live affinity"]
    )

    self.gpu_handler=GPUHandler(self.pardic)

    a =self.pardic["dec affinity start"]
    cs=1 # slot / stream count

    for address in self.addresses:
      # now livethread and openglthread are running
      if (a>self.pardic["dec affinity stop"]): a=self.pardic["dec affinity start"]
      print(pre,"openValkka: setting decoder thread on processor",a)

      chain=ManagedFilterchain(       # decoding and branching the stream happens here
        livethread  =self.livethread,
        openglthreads
                    =self.gpu_handler.openglthreads,
        address     =address,
        slot        =cs,
        affinity    =a,
        msreconnect =10000,
        
        verbose=True
        )

      self.chains.append(chain) # important .. otherwise chain will go out of context and get garbage collected ..

      cs+=1
      a+=1
      
  
  def closeValkka(self):
    self.livethread.close()
    
    for chain in self.chains:
      chain.close()
    
    self.chains       =[]
    self.gpu_handler.close()
    # of couse, do _not_ "annihilate" the floating Qt windows while openglthread is still trying to write into them
    # after openglthread has been closed:
    self.widget_pairs =[]
    self.videoframes  =[]


    
  def start_streams(self):
    pass
    
    
  def stop_streams(self):
    pass
    
  def closeEvent(self,e):
    print(pre,"closeEvent!")
    for vc in self.videocontainers:
      vc.close()
    self.stop_streams()
    self.closeValkka()
    e.accept()


def main():
  app=QtWidgets.QApplication(["test_app"])
  conf=MyConfigDialog()
  pardic=conf.exec_()
  if (pardic["ok"]):
    mg=MyGui(pardic)
    mg.show()
    app.exec_()


if (__name__=="__main__"):
  main()
 
 
