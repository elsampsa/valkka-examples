"""
test_studio_file.py : An example GUI for reading matroska (mkv) files, playing and sending them to an analyzer

* Copyright: 2018-2021 Sampsa Riikonen
* Authors  : Sampsa Riikonen
* Date     : 2018
* Version  : 0.1

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    test_studio_file.py
@author  Sampsa Riikonen
@date    2018
@version 1.4.0 
@brief   An example GUI for reading matroska (mkv) files, playing and sending them to an analyzer
"""

# from PyQt5 import QtWidgets, QtCore, QtGui # If you use PyQt5, be aware of the licensing consequences
from PySide2 import QtWidgets, QtCore, QtGui
import cv2
import sys
import json
import time
import os
from valkka.api2 import LiveThread, FileThread, OpenGLThread
from valkka.api2 import parameterInitCheck

# Local imports from this directory
from basic1 import ShmemFilterchain1
from demo_base import ConfigDialog, TestWidget0, getForeignWidget, WidgetPair
from demo_rgb import RGB24Process
from demo_qthread import QHandlerThread
from demo_analyzer import MovementDetector
from demo_singleton import event_fd_group_1

pre = "test_studio_file : "

# valkka_xwin =True # use x windows create by Valkka and embed them into Qt
valkka_xwin = False  # use Qt provided x windows

class MovementDetectorProcess(RGB24Process):
    """To implement your own detector process, just override handleFrame__  :)
    """
    class Signals(QtCore.QObject):
        """These signals are instantiated into the member "signals"

        Typically emitted by a QThread that's listening to this processes self.front_pipe
        """
        # PyQt5
        #start_move = QtCore.pyqtSignal(object)
        #stop_move = QtCore.pyqtSignal(object)
        # PySide2
        start_move = QtCore.Signal(object)
        stop_move = QtCore.Signal(object)

    def __init__(self, mstimeout=1000):
        super().__init__(mstimeout=mstimeout)
        self.signals = self.Signals()

    def preRun__(self):
        """This takes place in the multiprocessing backend
        """
        super().preRun__()
        # analyzer class is instantiated in the backend:
        self.analyzer = MovementDetector(treshold=0.0001)

    def sendSignal__(self, name):
        self.send_out__({"signal": name})  # send a dict object to the frontend
        # this message is typically captured by a QThread running in the frontend
        # which then converts it into a Qt signal

    def handleFrame__(self, frame, meta):
        print("RGB24Process: handleFrame__ : rgb client got frame",
              frame.shape, "from slot", meta.slot)
        """metadata has the following members:
        size 
        width
        height
        slot
        mstimestamp
        """
        result = self.analyzer(frame)
        if (result == MovementDetector.state_same):
            pass
        elif (result == MovementDetector.state_start):
            self.sendSignal__(name="start_move")
        elif (result == MovementDetector.state_stop):
            self.sendSignal__(name="stop_move")


class MyGui(QtWidgets.QMainWindow):

    debug = False
    # debug=True

    def __init__(self):
        super(MyGui, self).__init__()
        # self.pardic=pardic
        self.initVars()
        self.setupUi()
        if (self.debug):
            return
        self.openValkka()

    def initVars(self):
        self.messages = []
        self.mode = "file"
        self.slot_reserved = False

    def setupUi(self):
        self.setGeometry(QtCore.QRect(100, 100, 800, 800))
        self.w = QtWidgets.QWidget(self)
        self.setCentralWidget(self.w)
        self.lay = QtWidgets.QVBoxLayout(self.w)

        # divide window into three parts
        self.upper = QtWidgets.QWidget(self.w)
        self.lower = QtWidgets.QWidget(self.w)
        self.lowest = QtWidgets.QWidget(self.w)
        self.lay.addWidget(self.upper)
        self.lay.addWidget(self.lower)
        self.lay.addWidget(self.lowest)

        # upper part: license plate list and the video
        self.upperlay = QtWidgets.QHBoxLayout(self.upper)
        self.msg_list = QtWidgets.QTextEdit(self.upper)

        self.video_area = QtWidgets.QWidget(self.upper)
        self.video_lay = QtWidgets.QGridLayout(self.video_area)

        self.upperlay.addWidget(self.msg_list)
        self.upperlay.addWidget(self.video_area)
        self.msg_list.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum,  QtWidgets.QSizePolicy.Minimum)
        self.video_area.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # lower part: [Open File] [Close Live] [Play] [Stop] [Rewind]
        self.lowerlay = QtWidgets.QHBoxLayout(self.lower)
        self.open_file_button = QtWidgets.QPushButton("Open File", self.lower)
        self.close_file_button = QtWidgets.QPushButton(
            "Close File", self.lower)
        self.play_button = QtWidgets.QPushButton("Play", self.lower)
        self.stop_button = QtWidgets.QPushButton("Stop", self.lower)
        self.rewind_button = QtWidgets.QPushButton("<<",  self.lower)

        self.lowerlay.addWidget(self.open_file_button)
        self.lowerlay.addWidget(self.close_file_button)
        self.lowerlay.addWidget(self.play_button)
        self.lowerlay.addWidget(self.stop_button)
        self.lowerlay.addWidget(self.rewind_button)

        self.open_file_button.clicked. connect(self.open_file_button_slot)
        self.close_file_button.clicked.connect(self.close_file_button_slot)
        self.play_button.clicked.      connect(self.play_button_slot)
        self.stop_button.clicked.      connect(self.stop_button_slot)
        self.rewind_button.clicked.    connect(self.rewind_button_slot)

        # lowest part: some text
        self.lowestlay = QtWidgets.QVBoxLayout(self.lowest)
        self.infotext = QtWidgets.QLabel("info text", self.lowest)
        self.lowestlay.addWidget(self.infotext)

    def openValkka(self):
        # some constant values
        # Images passed over shmem are quarter of the full-hd reso
        shmem_image_dimensions = (1920 // 4, 1080 // 4)  # x, y
        # YUV => RGB interpolation to the small size is done each 1000
        # milliseconds and passed on to the shmem ringbuffer
        shmem_image_interval = 1000
        shmem_ringbuffer_size = 10

        # create & start multiprocesses before threads:
        # https://medium.com/@sampsa.riikonen/doing-python-multiprocessing-the-right-way-a54c1880e300
        self.process = MovementDetectorProcess()
        self.process.start()

        # multiprocess(es) have been started, now can spawn threads
        self.thread = QHandlerThread()
        self.thread.start()
        self.thread.addProcess(self.process) # self.thread now listens to self.process & translates its messages into Qt signals

        self.livethread = LiveThread(         # starts live stream services (using live555)
            name="live_thread",
            verbose=False
        )

        self.filethread = FileThread(
            name="file_thread",
            verbose=False
        )

        self.openglthread = OpenGLThread(     # starts frame presenting services
            name="mythread",
            n_720p=10,
            n_1080p=10,
            n_1440p=10,
            n_4K=10,
            verbose=False,
            msbuftime=100,
            affinity=-1
        )

        if (self.openglthread.hadVsync()):
            w = QtWidgets.QMessageBox.warning(
                self, "VBLANK WARNING", "Syncing to vertical refresh enabled\n THIS WILL DESTROY YOUR FRAMERATE\n Disable it with 'export vblank_mode=0' for nvidia proprietary drivers, use 'export __GL_SYNC_TO_VBLANK=0'")

        cc=1
        ipc_index, event_fd = event_fd_group_1.reserve()
        self.chain = ShmemFilterchain1(       # decoding and branching the stream happens here
            openglthread=self.openglthread,
            slot=cc,
            # this filterchain creates a shared memory server
            shmem_name="test_studio_file_"+str(cc),
            # Images passed over shmem are quarter of the full-hd reso
            shmem_image_dimensions=shmem_image_dimensions,
            # YUV => RGB interpolation to the small size is done each 1000 milliseconds and passed on to the shmem ringbuffer
            shmem_image_interval=shmem_image_interval,
            shmem_ringbuffer_size=shmem_ringbuffer_size,   # Size of the shmem ringbuffer
            event_fd = event_fd # use event file descriptor
        )

        shmem_name, n_buffer, shmem_image_dimensions_ = self.chain.getShmemPars()
        # print(pre,"shmem_name, n_buffer, n_bytes",shmem_name,n_buffer,n_bytes)

        self.process.activateRGB24Client(
            name = shmem_name, # must be exactly same as up there..
            n_ringbuffer = n_buffer,
            width  = shmem_image_dimensions_[0],
            height = shmem_image_dimensions_[1],
            ipc_index = ipc_index
        )

        self.process.signals.start_move.connect(self.set_moving_slot)
        self.process.signals.stop_move. connect(self.set_still_slot)

        if (valkka_xwin):
            # (1) Let OpenGLThread create the window
            self.win_id = self.openglthread.createWindow(show=False)
            self.widget_pair = WidgetPair(
                self.video_area, self.win_id, TestWidget0)
            self.video = self.widget_pair.getWidget()
        else:
            # (2) Let Qt create the window
            self.video = QtWidgets.QWidget(self.video_area)
            self.win_id = int(self.video.winId())

        self.video_lay.addWidget(self.video, 0, 0)
        self.token = self.openglthread.connect(slot=cc, window_id=self.win_id)

        self.chain.decodingOn()  # tell the decoding thread to start its job

    
    def stopProcesses(self):
        print(pre, "stopProcesses :", self.process)
        self.process.stop()
        self.thread.stop()
        print(pre, "QThread stopped")

    def closeValkka(self):
        self.livethread.close()
        self.chain.close()
        self.chain = None
        self.openglthread.close()

    def closeEvent(self, e):
        print(pre, "closeEvent!")
        self.stopProcesses()
        self.closeValkka()
        e.accept()

    # *** slots ****

    def open_file_button_slot(self):
        if (self.slot_reserved):
            self.infotext.setText("Close the current file first")
            return
        fname = QtWidgets.QFileDialog.getOpenFileName(filter="*.mkv")[0]
        if (len(fname) > 0):
            print(pre, "open_file_button_slot: got filename", fname)
            self.chain.setFileContext(fname)
            self.filethread.openStream(self.chain.file_ctx)
            self.slot_reserved = True
            if (self.chain.fileStatusOk()):
                self.infotext.setText("Opened file "+fname)
            else:
                self.infotext.setText("Can't play file "+fname)
        else:
            self.infotext.setText("No file opened")

    def close_file_button_slot(self):
        if (not self.slot_reserved):
            self.infotext.setText("Open a file first")
            return
        self.filethread.closeStream(self.chain.file_ctx)
        self.slot_reserved = False
        self.infotext.setText("Closed file")

    def open_live_button_slot(self):
        pass

    def play_button_slot(self):
        if (self.mode == "file"):
            if (not self.slot_reserved):
                self.infotext.setText("Open a file first")
                return
            self.filethread.playStream(self.chain.file_ctx)
        else:
            pass

    def rewind_button_slot(self):
        if (self.mode == "file"):
            if (not self.slot_reserved):
                self.infotext.setText("Open a file first")
                return
            self.chain.file_ctx.seektime_ = 0
            self.filethread.seekStream(self.chain.file_ctx)
        else:
            pass

    def stop_button_slot(self):
        if (self.mode == "file"):
            if (not self.slot_reserved):
                self.infotext.setText("Open a file first")
                return
            self.filethread.stopStream(self.chain.file_ctx)
        else:
            pass

    def set_still_slot(self):
        self.infotext.setText("still")
        self.messages.append("Movement stopped")
        if (len(self.messages) > 10):
            self.messages.pop(0)
        st = ""
        for message in self.messages:
            st += message+"\n"
        self.msg_list.setText(st)

    def set_moving_slot(self):
        self.infotext.setText("MOVING")
        self.messages.append("Movement started")
        if (len(self.messages) > 10):
            self.messages.pop(0)
        st = ""
        for message in self.messages:
            st += message+"\n"
        self.msg_list.setText(st)


def main():
    app = QtWidgets.QApplication(["test_app"])
    mg = MyGui()
    mg.show()
    app.exec_()


if (__name__ == "__main__"):
    main()
