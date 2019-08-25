"""
demo_widget.py : Widgets (and widget groups) for the demo programs

Copyright 2019 Sampsa Riikonen

Authors: Petri Eränkö, Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    NAME.py
@author  Sampsa Riikonen
@author  Petri Eränkö
@date    2019
@version 0.13.3 
@brief   
"""

from PySide2 import QtWidgets, QtCore, QtGui
#from PySide2.QtWidgets import *
#from PySide2.QtCore import *
#from PySide2.QtGui import *

import sys
from valkka.core import *



class ValkkaFSParameters:
    """Widgets (and their controller) for setting ValkkaFS parameters 
    """
    
    
    def __init__(self, parent, blocksize_limits = (1, 1024), numblocks_limits = (4, 1000)):
        
        self.numblocks = numblocks_limits[0]
        self.blocksize = blocksize_limits[0]
        
        self.main_widget = QtWidgets.QWidget(parent)
        self.main_lay = QtWidgets.QGridLayout(self.main_widget)
                
        self.record_checkbox = QtWidgets.QCheckBox("Enable Recording", self.main_widget)
        
        self.label1 = QtWidgets.QLabel("Filesystem Specs", self.main_widget)
        self.blocksize_label = QtWidgets.QLabel("Blocksize (MB)", self.main_widget)
        self.blocksize_value = QtWidgets.QLineEdit(self.main_widget)
        self.numblocks_label = QtWidgets.QLabel("Number of blocks", self.main_widget)
        self.numblocks_value = QtWidgets.QLineEdit(self.main_widget)
        self.totalsize_label = QtWidgets.QLabel("Total size (MB)", self.main_widget)
        self.totalsize_value = QtWidgets.QLineEdit(self.main_widget)
        
        self.totalsize_value.setReadOnly(True)

        #self.blocksize_value.setValidator(QIntValidator(blocksize_limits[0], blocksize_limits[1]))
        #self.numblocks_value.setValidator(QIntValidator(numblocks_limits[0], numblocks_limits[1]))
        
        self.label2 = QtWidgets.QLabel("Record Type", self.main_widget)
        self.regular_file_rb = QtWidgets.QRadioButton("Regular File")
        self.block_fs_rb = QtWidgets.QRadioButton("Dedicated block device")
        
        self.regular_file_button = QtWidgets.QPushButton("Choose File")
        self.block_fs_combo = QtWidgets.QComboBox(self.main_widget)
        
        self.label3 = QtWidgets.QLabel("Actions", self.main_widget)
        self.save_button = QtWidgets.QPushButton("SAVE", self.main_widget)
        self.save_label = QtWidgets.QLabel("Clears earlier recordings")
        self.cancel_button = QtWidgets.QPushButton("CANCEL", self.main_widget)
        self.cancel_label = QtWidgets.QLabel("Exits without applying changes")
        
        self.main_lay.addWidget(self.record_checkbox, 0, 0)
        
        self.main_lay.addWidget(self.label1, 1, 0)
        self.main_lay.addWidget(self.blocksize_label, 2, 0)
        self.main_lay.addWidget(self.blocksize_value, 2, 1)
        self.main_lay.addWidget(self.numblocks_label, 3, 0)
        self.main_lay.addWidget(self.numblocks_value, 3, 1)
        self.main_lay.addWidget(self.totalsize_label, 4, 0)
        self.main_lay.addWidget(self.totalsize_value, 4, 1)
        
        self.main_lay.addWidget(self.label2, 5, 0)
        self.main_lay.addWidget(self.regular_file_rb, 6, 0)
        self.main_lay.addWidget(self.regular_file_button, 6, 1)
        self.main_lay.addWidget(self.block_fs_rb, 7, 0)
        self.main_lay.addWidget(self.block_fs_combo, 7, 1)
        
        self.main_lay.addWidget(self.label3, 8, 0)
        self.main_lay.addWidget(self.save_button, 9, 0)
        self.main_lay.addWidget(self.save_label, 9, 1)
        self.main_lay.addWidget(self.cancel_button, 10, 0)
        self.main_lay.addWidget(self.cancel_label, 10, 1)
        
        
        # self.blocksize_value.editingFinished.connect(self.paska_slot)
        self.blocksize_value.textChanged.connect(self.blocksize_slot)
        self.numblocks_value.textChanged.connect(self.numblocks_slot)
        #self.numblocks_value.editingFinished.connect(self.numblocks_slot)
        
        
        # self.save_button.clicked.connect(self.paska_slot)
        self.save_button.clicked.connect(self.paska_slot)
        
        
        
        """TODO
        
        - Numerical values limit to blocksize and number of blocks
        - Total size can't be modified by the user
        - Default values for both
        
        - Default filesystem type = regular file
        - scan block devices => construct combobox
        - choose file : launch file selection dialog
        """
        
        
        
    def blocksize_slot(self, t):
        self.blocksize = int(t)
        self.recalcSize()
        
    def numblocks_slot(self, t):
        self.numblocks = int(t)
        self.recalcSize()
    
    def recalcSize(self):
        self.size = self.blocksize * self.numblocks
        self.totalsize_value.setText(str(self.size))
    
    
    
 
class MyGui(QtWidgets.QMainWindow):


  def __init__(self,parent=None):
    super(MyGui, self).__init__()
    self.setupUi()
    

  def setupUi(self):
    self.setGeometry(QtCore.QRect(100,100,500,500))
    
    self.w=QtWidgets.QWidget(self)
    self.setCentralWidget(self.w)
    
    self.fspars = ValkkaFSParameters(self.w)
    
  
def main():
  app=QtWidgets.QApplication(["test_app"])
  mg=MyGui()
  mg.show()
  app.exec_()


if (__name__=="__main__"):
  main()
 
