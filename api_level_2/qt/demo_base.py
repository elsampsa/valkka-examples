"""
demo_base.py : Common classes, etc. for the qt streaming, shared-memory and opecv demos

Copyright 2017, 2018 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    demo_base.py
@author  Sampsa Riikonen
@date    2018
@version 0.13.0 
@brief   
"""

# from PyQt5 import QtWidgets, QtCore, QtGui
from PySide2 import QtWidgets, QtCore, QtGui
import sys
import json
import os

pre="demo_base : "


class DesktopHandler:
  """Handle XScreens and screen dimensions
  """
  
  def __init__(self):
    self.desktop =QtWidgets.QDesktopWidget()
    self.i       =self.desktop.primaryScreen()
    self.rect    =self.desktop.availableGeometry(self.i)
    self.n       =self.desktop.screenCount()
    
    # primary screen parameters
    self.x       =self.rect.x()
    self.y       =self.rect.y()
    self.w       =self.rect.width()
    self.h       =self.rect.height()
    
    
  def getGeometry(self,i_dim,j_dim,i,j):
    dx =self.w/i_dim
    dy =self.h/j_dim
    print(pre,"DesktopHandler: setGeometry:",i*dx,j*dy,dx,dy)
    return QtCore.QRect(i*dx,j*dy,dx,dy)
    
    
  def __str__(self):
    st = "DesktopHandler: x=%i, y=%i, w=%i, h=%i, N=%i" % (self.x, self.y, self.w, self.h, self.n)
    return st
    


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
      "videos per row"     : 4,
      "ok"                 : True
    }
    
    # ["n_720p", "n_1080p", "n_1440p", "n_4K", "naudio", "verbose", "live affinity", "gl affinity", "dec affinity start", "dec affinity stop"]
    self.plis=["n_720p", "n_1080p", "n_1440p", "n_4K", "naudio", "verbose", "msbuftime", "live affinity", "gl affinity", "dec affinity start", "dec affinity stop","videos per row"]
    
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
    os.system("killall ffplay vlc")
    super().closeEvent(e)
    # e.accept()
    

"""Some tools for making GUI menus

class FileMenu(QuickMenu):
  name="File"
  tooltip="The File Menu"
  
  elements=[
    QuickMenuElement(name="Open File",tooltip="Open New File")
    QuickMenuElement(name="Exit",tooltip="Exit the Program")
    FileSubMenu # (subclass of QuickMenu as well => this is a submenu)
  ]

At instantiation, the class creates a member self.menu (QMenu) 

Instantiation also auto-creates callback methods, i.e.:

filemenu =FileMenu(parent=mainwindow)
filemenu.open_file.triggered.connect(callback)
filemenu.exit.triggered.connect(callback)


"""



class QuickMenuElement(object):
  """Generic menu element object.  Can add lots of things here, say, tooltips, translations, etc.
  """


  def __init__(self,title="none"):
    self.title=title


  def getTitle(self):
    return self.title



class QuickMenu(object):
  title ="none"

  elements = [] # a list of QuickMenuElement(s)

  def __init__(self, parent):
    """
    :param parent:  Where this menu will be placed
    """
    if (isinstance(parent, QtWidgets.QMainWindow)): # i.e. the current menu will be placed in the main menu bar
      self.menu = parent.menuBar().addMenu(self.title)
    elif (parent == None):  # this is a popup menu
      self.menu = QtWidgets.QMenu()
    else: # a submenu
      print("submenu!")
      assert(issubclass(parent.__class__,QtWidgets.QMenu))
      self.menu = parent.addMenu(self.title)

    for element in self.elements:
      print(element)
      if (isinstance(element,QuickMenuElement)):
        # create menu entry / action, and find the callback / slot if defined
        # If name in EasyMenuElement was "Open File", create a method_name that is "open_file"
        method_name = element.getTitle().lower().replace(" ", "_").strip()
        # self.open_file =QMenu.addAction("Open File")
        setattr(self, method_name, self.menu.addAction(element.getTitle()))
        # now we have "self.method_name" .. lets refer to it as "method"
        method = getattr(self, method_name)
        """ # connect automatically to instances methods .. not really useful
        # callback functions name: self.open_file_called
        cbname = method_name + "_called"
        if (hasattr(self, cbname)):
          # if self.open_file_called exists, make connection: self.open_file.triggered.connect(self.open_file_called)
          method.triggered.connect(getattr(self, cbname))
        """
      elif (issubclass(element,QuickMenu)): # recursion: this is a subclass of MyMenu.  We instantiate it here
        submenu = element(parent=self.menu) # this constructor called for another subclass of QuickMenu
        submenu_title = element.title.lower()
        setattr(self, submenu_title, submenu) # now we can access menus hierarchically: menu.submenu.subsubmenu.etc
      else: # must be an EasyMenuElement instance
        raise(AssertionError("Use QuickMenu subclasses or QuickMenuElement instances"))


  def connect(self, name, cb):
    method = getattr(self, name)
    method.triggered.connect(cb)


  def popup(self, qp):
    self.menu.popup(qp)


 
 
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

    class FileSubMenu(QuickMenu):
      title="Submenu"
      elements=[
        QuickMenuElement(title="Submenu1"),
        QuickMenuElement(title="Submenu2")
      ]

    class FileMenu(QuickMenu):
      title="File"
      elements=[
        QuickMenuElement(title="New"),
        FileSubMenu,
        QuickMenuElement(title="Save as"),
        QuickMenuElement(title="Exit")
      ]

    self.filemenu=FileMenu(parent=self)

    self.filemenu.new.triggered.connect(self.new_slot)
    self.filemenu.submenu.submenu1.triggered.connect(self.submenu1_slot)

  def new_slot(self):
    print("New")

  def submenu1_slot(self):
    print("submenu1")

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
 
