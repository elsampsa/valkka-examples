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
@version 0.10.0 
@brief   
"""

# from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

import sys
# from valkka.core import *
from valkka.api2.valkkafs import findBlockDevices, ValkkaFS



class ValkkaFSConfig:
    """Widgets (and their controller) for setting ValkkaFS parameters 
    
    
    
    
    - Needs api2 ValkkaFS instance as an input parameter
    - ValkkaFS instance also refers to a directory with the following files:
    
    ::
    
        blockfile  
        dumpfile  
        valkkafs.json
    
    - ValkkaFS instance is a "singleton" .. it originates from here and is passed to all other instances using it
    
    ::
    
        ValkkaFS.newFromDirectory(dirname=None, blocksize=None, n_blocks=None, device_size=None, partition_uuid=None, verbose=False)
    
    """
    
    
    def __init__(self, dirname, parent = None, blocksize_limits = (1, 1024*100), n_blocks_limits = (4, 1024)): # 1 MB -> 100 GB, -> 100 TB
        self.dirname = dirname
        self.fs = ValkkaFS.loadFromDirectory(dirname = self.dirname)
        
        self.blocksize_limits = blocksize_limits
        self.n_blocks_limits = n_blocks_limits
        
        self.main_widget = QWidget(parent)
        self.main_lay = QGridLayout(self.main_widget)
                
        # self.record_checkbox = QCheckBox("Enable Recording", self.main_widget) # not in this widget
        
        self.label1 = QLabel("Filesystem Specs", self.main_widget)
        self.blocksize_label = QLabel("Blocksize (MB)", self.main_widget)
        self.blocksize_value = QLineEdit(self.main_widget)
        self.n_blocks_label = QLabel("Number of blocks", self.main_widget)
        self.n_blocks_value = QLineEdit(self.main_widget)
        self.totalsize_label = QLabel("Total size (MB)", self.main_widget)
        self.totalsize_value = QLineEdit(self.main_widget)
        
        self.totalsize_value.setReadOnly(True)

        self.blocksize_value.setValidator(QIntValidator(blocksize_limits[0], blocksize_limits[1]))
        self.n_blocks_value.setValidator(QIntValidator(n_blocks_limits[0], n_blocks_limits[1]))
        
        self.label2 = QLabel("Record Type", self.main_widget)
        self.regular_file_rb = QRadioButton("Regular File")
        self.block_fs_rb = QRadioButton("Dedicated block device")
        
        # self.regular_file_button = QPushButton("Choose File") # this is automagic
        self.block_fs_combo = QComboBox(self.main_widget)
        
        self.label3 = QLabel("Actions", self.main_widget)
        
        self.format_button = QPushButton("FORMAT", self.main_widget)
        self.format_label = QLabel("Applies filesystem changes (clears ValkkaFS)")
        
        self.save_button = QPushButton("SAVE", self.main_widget)
        self.save_label = QLabel("Applies other changes")
        
        self.cancel_button = QPushButton("CANCEL", self.main_widget)
        self.cancel_label = QLabel("Exits without applying any changes")
        
        # self.main_lay.addWidget(self.record_checkbox, 0, 0)
        
        self.main_lay.addWidget(self.label1, 1, 0)
        self.main_lay.addWidget(self.blocksize_label, 2, 0)
        self.main_lay.addWidget(self.blocksize_value, 2, 1)
        self.main_lay.addWidget(self.n_blocks_label, 3, 0)
        self.main_lay.addWidget(self.n_blocks_value, 3, 1)
        self.main_lay.addWidget(self.totalsize_label, 4, 0)
        self.main_lay.addWidget(self.totalsize_value, 4, 1)
        
        self.main_lay.addWidget(self.label2, 5, 0)
        self.main_lay.addWidget(self.regular_file_rb, 6, 0)
        # self.main_lay.addWidget(self.regular_file_button, 6, 1)
        self.main_lay.addWidget(self.block_fs_rb, 7, 0)
        self.main_lay.addWidget(self.block_fs_combo, 7, 1)
        
        self.main_lay.addWidget(self.label3, 8, 0)
        
        self.main_lay.addWidget(self.format_button, 9, 0)
        self.main_lay.addWidget(self.format_label, 9, 1)
        
        self.main_lay.addWidget(self.save_button, 10, 0)
        self.main_lay.addWidget(self.save_label, 10, 1)
        
        self.main_lay.addWidget(self.cancel_button, 11, 0)
        self.main_lay.addWidget(self.cancel_label, 11, 1)
        
        self.blocksize_value.textChanged.connect(self.blocksize_slot)
        self.n_blocks_value.textChanged.connect(self.n_blocks_slot)
        # self.regular_file_button.clicked.connect(self.regular_file_slot)
        self.block_fs_combo.currentIndexChanged.connect(self.block_device_slot)
        
        self.format_button.clicked.connect(self.format_slot)
        
        """
        self.save_button.clicked.connect(self.save_slot)
        self.cancel_button.clicked.connect(self.cancel_slot)
        """
        
        """TODO
        
        - Numerical values limit to blocksize and number of blocks
        - Total size can't be modified by the user
        - Default values for both
        
        - Default filesystem type = regular file
        - scan block devices => construct combobox
        - choose file : launch file selection dialog
        """
        
        self.initValues()
        
        
    def initValues(self):
        # self.n_blocks = self.n_blocks_limits[0]
        # self.blocksize = self.blocksize_limits[0]
        
        # get initial values from the ValkkaFS
        self.blocksize = round(self.fs.blocksize / 1024 / 1024) # bytes to megabytes
        self.n_blocks = self.fs.n_blocks
        
        self.n_blocks_value.setText(str(self.n_blocks))
        self.blocksize_value.setText(str(self.blocksize))
        
        self.regular_file_rb.setChecked(True)
    
        # self.regular_file = "recording.vfs"
        self.block_devices = findBlockDevices()
        
        # self.block_devices = {"xxx-xxx-xxx" : {}, "yyy-yyy-yyy" : {}}

        self.block_devices_list = []        
        for key, value in self.block_devices.items():
            self.block_fs_combo.addItem(key)
            self.block_devices_list.append(value)
        
        if len(self.block_devices_list) < 1:
            self.block_fs_rb.setEnabled(False)
        
        self.partition_uuid = None
        if self.fs.partition_uuid is not None and self.fs.partition_uuid in self.block_devices:
            self.block_fs_rb.setChecked(True)
            self.block_fs_combo.setCurrentText(self.fs.partition_uuid)
            
    
    def recalcSize(self):
        self.device_size = self.blocksize * self.n_blocks
        self.totalsize_value.setText(str(self.device_size))
    
    
    # *** slots ***
    
    def blocksize_slot(self, t):
        self.blocksize = int(t)
        self.recalcSize()
        
    def n_blocks_slot(self, t):
        self.n_blocks = int(t)
        self.recalcSize()
    
    def regular_file_slot(self):
        self.regular_file = QFileDialog.getOpenFileName(self.main_widget, self.regular_file, filter="*.vfs")[0]
    
    def block_device_slot(self, t):
        self.partition_uuid = t
        print("block_device_slot", self.partition_uuid)
        
        
    def format_slot(self):
        """Gather info and format ValkkaFS
        """
        partition_uuid = None
        if self.block_fs_rb.isChecked():
            self.partition_uuid = self.block_fs_combo.currentText()
            print("format_slot: block fs checked", self.partition_uuid)
            partition_uuid = self.partition_uuid
        
        print("formatting valkkafs")
        print("partition", partition_uuid)
        # return
        
        self.fs = ValkkaFS.newFromDirectory(
            dirname         = self.dirname, 
            blocksize       = self.blocksize * 1024 * 1024, # back to bytes
            n_blocks        = self.n_blocks, 
            device_size     = None, # calculate from blocksize and n_blocks
            partition_uuid  = partition_uuid,
            verbose         = False)
        
    # *** getters ***
    
    def getValkkaFSInstance(self):
        return self.fs
        
    
        
    
 
class MyGui(QMainWindow):


  def __init__(self,parent=None):
    super(MyGui, self).__init__()
    self.setupUi()
    

  def setupUi(self):
    self.setGeometry(QRect(100,100,500,500))
    
    self.w=QWidget(self)
    self.setCentralWidget(self.w)
    
    self.fspars = ValkkaFSConfig("/home/sampsa/tmp/testvalkkafs", parent = self.w)
    
  
def main():
  app=QApplication(["test_app"])
  mg=MyGui()
  mg.show()
  app.exec_()


if (__name__=="__main__"):
  main()
 
