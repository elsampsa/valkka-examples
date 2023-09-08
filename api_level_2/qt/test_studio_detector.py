"""
test_studio_detector.py : Test live streaming with Qt.  Send copies of streams to OpenCV movement detector processes.  There is one OpenCV detector & multiprocess for each stream.

Copyright 2017 - 2021 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    test_studio_detector.py
@author  Sampsa Riikonen
@date    2018
@version 1.5.4 
@brief   Test live streaming with Qt.  Send copies of streams to OpenCV movement detector processes.  There is one OpenCV detector & multiprocess for each stream.

In the main text field, write live video sources, one to each line, e.g.

::

    rtsp://admin:admin@192.168.1.10
    rtsp://admin:admin@192.168.1.12
    multicast.sdp
    multicast2.dfp

Reserve enough frames into the pre-reserved frame stack.  There are stacks for 720p, 1080p, etc.  The bigger the buffering time "msbuftime" (in milliseconds), the bigger stack you'll be needing.

When affinity is greater than -1, the processes are bound to a certain processor.  Setting "live affinity" to 0, will bind the Live555 thread to processor one.  Setting "dec affinity start" to 1 and "dec affinity start 3" will bind the decoding threads to processors 1-3.  (first decoder process to 1, second to 2, third to 3, fourth to 1 again, etc.)

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

# from PyQt5 import QtWidgets, QtCore, QtGui # If you use PyQt5, be aware
# of the licensing consequences
from PySide2 import QtWidgets, QtCore, QtGui
import sys
import json
import os
from valkka.api2 import LiveThread, OpenGLThread
from valkka.api2 import parameterInitCheck
from valkka.core import TimeCorrectionType_dummy, TimeCorrectionType_none, TimeCorrectionType_smart, setLogLevel_livelogger

# Local imports from this directory:
from basic import ShmemFilterchain
from demo_base import ConfigDialog, TestWidget0, getForeignWidget, WidgetPair
from demo_rgb import RGB24Process
from demo_qthread import QHandlerThread
from demo_analyzer import MovementDetector
from demo_singleton import event_fd_group_1

pre = "test_studio_detector : "

# valkka_xwin =True # use x windows create by Valkka and embed them into Qt
valkka_xwin = False  # use Qt provided x windows

class MyConfigDialog(ConfigDialog):

    def setConfigPars(self):
        self.tooltips = {        # how about some tooltips?
        }
        self.pardic.update({})  # add more parameter key/value pairs
        self.plis += []         # list of parameter keys that are saved to config file
        self.config_fname = "test_studio_detector.config"  # define the config file name

    def extra(self):
        self.run2_button.hide()
        self.ffplay_button.hide()
        self.vlc_button.hide()


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


    def __init__(self, mstimeout = 1000):
        super().__init__(mstimeout = mstimeout)
        self.signals = self.Signals()

    def preRun__(self):
        """This takes place in the multiprocessing backend
        """
        super().preRun__()
        # analyzer class is instantiated in the backend:
        self.analyzer = MovementDetector(treshold=0.0001)

    def sendSignal__(self, name):
        self.send_out__({"signal": name}) # send a dict object to the frontend
        # this message is typically captured by a QThread running in the frontend
        # which then converts it into a Qt signal

    def handleFrame__(self, frame, meta):
        print("RGB24Process: handleFrame__ : rgb client got frame", frame.shape, "from slot", meta.slot)
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

    class Frame:
        """Create a frame with text (indicating movement) and a video frame.  The video frame is created from a "foreign" window (created by Valkka)
        """

        def __init__(self, parent, win_id):
            self.widget = QtWidgets.QWidget(parent)
            self.lay = QtWidgets.QVBoxLayout(self.widget)

            self.text = QtWidgets.QLabel("", self.widget)
            self.text_stylesheet = self.text.styleSheet()

            # create the foreign widget / normal widget pair
            # normal widget of class TestWidget0
            self.widget_pair = WidgetPair(self.widget, win_id, TestWidget0)
            self.video = self.widget_pair.getWidget()

            self.lay.addWidget(self.text)
            self.lay.addWidget(self.video)
            self.text.setSizePolicy(
                QtWidgets.QSizePolicy.Minimum,
                QtWidgets.QSizePolicy.Minimum)
            self.video.setSizePolicy(
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding)
            self.set_still()

        def setText(self, txt):
            self.text.setText(txt)

        def set_still(self):
            self.setText("still")
            self.widget.setStyleSheet(self.text_stylesheet)

        def set_moving(self):
            self.setText("MOVING")
            self.widget.setStyleSheet(
                "QLabel {border: 2px; border-style:solid; border-color: red; margin:0 px; padding:0 px; border-radius:8px;}")

    class NativeFrame:
        """Create a frame with text (indicating movement) and a video frame.  The video frame is created by Qt.
        """

        def __init__(self, parent):
            self.widget = QtWidgets.QWidget(parent)
            self.lay = QtWidgets.QVBoxLayout(self.widget)

            self.text = QtWidgets.QLabel("", self.widget)
            self.text_stylesheet = self.text.styleSheet()

            self.video = QtWidgets.QWidget(self.widget)

            self.lay.addWidget(self.text)
            self.lay.addWidget(self.video)
            self.text.setSizePolicy(
                QtWidgets.QSizePolicy.Minimum,
                QtWidgets.QSizePolicy.Minimum)
            self.video.setSizePolicy(
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding)
            self.set_still()

        def getWindowId(self):
            return int(self.video.winId())

        def setText(self, txt):
            self.text.setText(txt)

        def set_still(self):
            self.setText("still")
            self.widget.setStyleSheet(self.text_stylesheet)

        def set_moving(self):
            self.setText("MOVING")
            self.widget.setStyleSheet(
                "QLabel {border: 2px; border-style:solid; border-color: red; margin:0 px; padding:0 px; border-radius:8px;}")

    debug = False
    # debug=True

    def __init__(self, pardic, parent=None):
        super(MyGui, self).__init__()
        self.pardic = pardic
        self.initVars()
        self.setupUi()
        if (self.debug):
            return
        self.openValkka()

    def initVars(self):
        pass

    def setupUi(self):
        self.setGeometry(QtCore.QRect(100, 100, 800, 800))
        self.w = QtWidgets.QWidget(self)
        self.setCentralWidget(self.w)
        self.lay = QtWidgets.QGridLayout(self.w)
        self.frames = []  # frames with movement detector alert and video
        self.addresses = self.pardic["cams"]

    def openValkka(self):
        # some constant values
        # Images passed over shmem are quarter of the full-hd reso
        shmem_image_dimensions = (1920 // 4, 1080 // 4) # x, y
        # YUV => RGB interpolation to the small size is done each 1000
        # milliseconds and passed on to the shmem ringbuffer
        shmem_image_interval = 1000
        shmem_ringbuffer_size = 10

        # create & start multiprocesses before threads:
        # https://medium.com/@sampsa.riikonen/doing-python-multiprocessing-the-right-way-a54c1880e300
        cs = 1
        self.processes = []
        for address in self.addresses:
            shmem_name = "test_studio_" + str(cs)
            process = MovementDetectorProcess()
            process.start()
            self.processes.append(process)

        # ..so, forks have been done.  Now we can spawn all threads
        self.thread = QHandlerThread()
        self.thread.start()
        for process in self.processes:
            self.thread.addProcess(process)
        # ..now the QThread listens to all multiprocesses
        # and converts their outgoing messages into signals

        self.livethread = LiveThread(         # starts live stream services (using live555)
            name="live_thread",
            verbose=False,
            affinity=self.pardic["live affinity"]
        )

        self.openglthread = OpenGLThread(     # starts frame presenting services
            name="mythread",
            # reserve stacks of YUV video frames for various resolutions
            n_720p=self.pardic["n_720p"],
            n_1080p=self.pardic["n_1080p"],
            n_1440p=self.pardic["n_1440p"],
            n_4K=self.pardic["n_4K"],
            # naudio  =self.pardic["naudio"], # obsolete
            verbose=False,
            msbuftime=self.pardic["msbuftime"],
            affinity=self.pardic["gl affinity"]
        )

        if (self.openglthread.hadVsync()):
            w = QtWidgets.QMessageBox.warning(
                self,
                "VBLANK WARNING",
                "Syncing to vertical refresh enabled\n THIS WILL DESTROY YOUR FRAMERATE\n Disable it with 'export vblank_mode=0' for nvidia proprietary drivers, use 'export __GL_SYNC_TO_VBLANK=0'")

        tokens = []
        self.chains = []
        self.frames = []
        cs = 1
        cc = 0
        a = self.pardic["dec affinity start"]

        for address in self.addresses:
            # now livethread and openglthread are running
            if (a > self.pardic["dec affinity stop"]):
                a = self.pardic["dec affinity start"]
            print(pre, "openValkka: setting decoder thread on processor", a)

            # this filterchain creates a shared memory server
            # identifies shared memory buffer must be same as in the
            # multiprocess

            ipc_index, event_fd = event_fd_group_1.reserve()

            chain = ShmemFilterchain(       # decoding and branching the stream happens here
                livethread=self.livethread,
                openglthread=self.openglthread,
                address=address,
                slot=cs,
                affinity=a,
                shmem_name="test_studio_" + str(cs),
                shmem_image_dimensions=shmem_image_dimensions,
                shmem_image_interval=shmem_image_interval,
                shmem_ringbuffer_size=shmem_ringbuffer_size,
                msreconnect=10000,
                event_fd = event_fd # use event file descriptors
                # time_correction   =TimeCorrectionType_smart # this is the default, no need to specify
            )
            self.chains.append(chain)

            if (valkka_xwin):
                win_id = self.openglthread.createWindow(show=False)
                frame = self.Frame(self.w, win_id)
            else:
                frame = self.NativeFrame(self.w)
                win_id = frame.getWindowId()

            # print(pre,"setupUi: layout index, address : ",cc//4,cc%4,address)
            # self.lay.addWidget(frame.widget,cc//4,cc%4)

            nrow = self.pardic["videos per row"]
            print(
                pre,
                "setupUi: layout index, address : ",
                cc //
                nrow,
                cc %
                nrow,
                address)
            self.lay.addWidget(frame.widget, cc // nrow, cc % nrow)

            self.frames.append(frame)

            token = self.openglthread.connect(slot=cs, window_id=win_id)
            tokens.append(token)

            # take corresponding analyzer multiprocess
            process = self.processes[cc]

            # tell process to create the shmem client
            # it's important to do this _after_ the filterchain has been created, since
            # the filterchain creates the shmem server
            process.activateRGB24Client(
                name = "test_studio_" + str(cs), # must be exactly same as up there..
                n_ringbuffer = shmem_ringbuffer_size,
                width  = shmem_image_dimensions[0],
                height = shmem_image_dimensions[1],
                ipc_index = ipc_index
            )

            # connect signals to the nested widget
            process.signals.start_move.connect(frame.set_moving)
            process.signals.stop_move.connect(frame.set_still)

            chain.decodingOn()  # tell the decoding thread to start its job
            cs += 1  # TODO: crash when repeating the same slot number ..?
            a += 1
            cc += 1

    def stopProcesses(self):
        for p in self.processes:
            p.deactivateRGB24Client()
            p.stop()
        print(pre, "stopping QThread")
        self.thread.stop()
        print(pre, "QThread stopped")

    def closeValkka(self):
        self.livethread.close()

        for chain in self.chains:
            chain.close()

        self.chains = []
        self.openglthread.close()
        self.widget_pairs = []
        self.videoframes = []

    def closeEvent(self, e):
        print(pre, "closeEvent!")
        self.stopProcesses()
        self.closeValkka()
        # super().closeEvent(e)
        e.accept()


def main():
    app = QtWidgets.QApplication(["test_app"])
    conf = MyConfigDialog()
    pardic = conf.exec_()
    # print(pre,"got",pardic)
    # return
    if (pardic["ok"]):
        mg = MyGui(pardic)
        mg.show()
        app.exec_()


if (__name__ == "__main__"):
    main()
