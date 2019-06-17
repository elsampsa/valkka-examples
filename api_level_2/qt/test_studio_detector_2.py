"""
test_studio_detector_2.py : Test live streaming with Qt.  Send copies of the streams to machine vision process.  There is a single machine vision process for all streams.

Copyright 2017 - 2019 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    test_studio_detector_2.py
@author  Sampsa Riikonen
@date    2018
@version 0.12.0 
@brief   Test live streaming with Qt.  Send copies of the streams to OpenCV movement detector processes.


In the main text field, write live video sources, one to each line, e.g.

::

    rtsp://admin:admin@192.168.1.10
    rtsp://admin:admin@192.168.1.12
    multicast.sdp
    multicast2.dfp

Reserve enough frames into the pre-reserved frame stack.  There are stacks for 720p, 1080p, etc.  The bigger the buffering time "msbuftime" (in milliseconds), the bigger stack you'll be needing.

When affinity is greater than -1, the processes are bound to a certain processor.  Setting "live affinity" to 0, will bind the Live555 thread to processor one.  Setting "dec affinity start" to 1 and "dec affinity start 3" will bind the decoding threads to processors 1-3.  (first decoder process to 1, second to 2, third to 3, fourth to 1 again, etc.)

It's very important to disable vertical sync in OpenGL rendering..!  Otherwise your *total* framerate is limited to 60 fps.  Disabling vsync can be done in mesa-based open source drives with:

export vblank_mode=0

and in nvidia proprietary drivers with

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
import cv2
import sys
import json
import os
import time
from valkka.api2 import LiveThread, OpenGLThread, ValkkaProcess, ShmemClient
from valkka.api2 import ShmemFilterchain
from valkka.api2 import parameterInitCheck
from valkka.core import TimeCorrectionType_dummy, TimeCorrectionType_none, TimeCorrectionType_smart, setLogLevel_livelogger, RGBShmemFrameFilter, ThreadSafeFrameFilter

# Local imports from this directory
from demo_multiprocess import QValkkaThread
from demo_analyzer_process import QValkkaGlobalDetectorProcess
from demo_base import ConfigDialog, TestWidget0, getForeignWidget, WidgetPair
from chains import MovementFilterchain

pre = "test_studio_detector_2 :"

shmem_image_dimensions  = (1920 // 4, 1080 // 4) # max image dimensions that the shmem can handle
shmem_name = "valkka_multi_detector"
shmem_ringbuffer_size = 10

image_dimensions = shmem_image_dimensions # actual image dimensions for the RGB bitmaps



class MyConfigDialog(ConfigDialog):

    def setConfigPars(self):
        self.tooltips = {        # how about some tooltips?
        }
        self.pardic.update({})  # add more parameter key/value pairs
        self.plis += []         # list of parameter keys that are saved to config file
        self.config_fname = "test_studio_detector_2.config"  # define the config file name

    def extra(self):
        self.run2_button.hide()
        self.ffplay_button.hide()
        self.vlc_button.hide()



class MyGui(QtWidgets.QMainWindow):


    class OverlayWidget(QtWidgets.QWidget):
        
        class Signals(QtCore.QObject):
            current_rectangle = QtCore.Signal(object) # informs controller about the newly created rectangle
            draw_rectangles   = QtCore.Signal(object) # carries of list of all rectangles to be drawn
        
        def __init__(self, parent):
            super().__init__(parent)
            self.signals = self.Signals()
            self.reset()
            self.token = None
            
        def setToken(self, token):
            self.token = token
            
        def reset(self):
            self.fac = 1
            self.old_t = 0
            self.frame_list = []
            self.resetRect()

        def resetRect(self):
            self.rect = None
            self.x0 = None
            self.x1 = None
            self.y0 = None
            self.y1 = None
            
        def mousePressEvent(self, e):
            print("mousepressevent :", e)
            self.x0 = e.x()
            self.y0 = e.y()
            e.accept()
        
        def mouseReleaseEvent(self, e):
            # print("mousereleaseevent :", e)
            self.t = time.time()
            dt = (self.t - self.old_t)
            self.old_t = self.t
            
            if (dt < 0.5):
                print("double click")
                self.resetRect()
                
            e.accept()
            # self.signals.current_rectangle.emit(self.getDrawRect())
            self.signals.draw_rectangles.emit(
                (self.token, [self.getDrawRect()] + self.frame_list)
                )
            
        def set_frames_slot(self, frame_list):
            # print("OverlayWidget: set_frames_slot: frame_list=", frame_list)
            self.frame_list = frame_list
            self.signals.draw_rectangles.emit(
                (self.token, [self.getDrawRect()] + self.frame_list)
                )
            
        def mouseMoveEvent(self, e):
            if self.x0 is not None:
                self.x1 = e.x()
                self.y1 = e.y()
                # print("mousemoveevent : (%i, %i) -> (%i, %i)" % (self.x0, self.y0, self.x1, self.y1))
                self.repaint()
                e.accept()
                
        def getDrawRect(self):
            # Return rectangle that can be draw directly with OpenGLThread
            # return left, right, top, bottom
            if (self.x1 != None):
                w = self.width()
                h = self.height()
                left    = min(self.x0, self.x1)
                right   = max(self.x0, self.x1)
                top     = max(h-self.y0, h-self.y1) # from Qt coordinates (origo: top left) to normal coordinates (origo: bottom left)
                bottom  = min(h-self.y0, h-self.y1)
                # print("getDrawRect: l, r, t, b", left, right, top, bottom)
                return left/w, right/w, top/h, bottom/h
            else:
                return 0., 1., 1., 0. # by default, whole image
        
        def paintEvent(self, e):
            # print("paintevent")
            qp = QtGui.QPainter()
            qp.begin(self)
            self.drawWidget(qp)
            qp.end()
                
        """# nopes
        def resizeEvent(self, e):
            self.resetRect()
            super().resizeEvent(e)
        """
           
            
        """
        def sizeHint(self):
            print("default sizeHint: ", super(TagWidget, self).sizeHint())
            if (self.pixmap):
                return self.pixmap.size()
            else:
                return QtCore.QSize(300,300)
        """
        
        
        def drawWidget(self, qp):
            if self.x1 != None: # there is a rectangle
                pen = QtGui.QPen(QtGui.QColor(20, 255, 20), 6, QtCore.Qt.SolidLine)
                qp.setPen(pen)
                qp.setBrush(QtCore.Qt.NoBrush)
                rect = QtCore.QRect( # QRect starts from top-left
                    self.x0,
                    self.y0,
                    self.x1-self.x0,
                    self.y1-self.y0
                )             
                qp.drawRect(rect)
                
        


    class NativeFrame:
        """Create a frame with text (indicating movement) and a video frame.  The video frame is created by Qt.
        """

        class Signals(QtCore.QObject):
            movement = QtCore.Signal()
            still = QtCore.Signal()
            current_frames = QtCore.Signal(object)
            

        def __init__(self, parent):
            self.signals = self.Signals()
            
            self.objects = [] # list of recently detected objects
            self.counter = 0
            
            self.widget = QtWidgets.QWidget(parent)
            self.lay = QtWidgets.QVBoxLayout(self.widget)

            self.text = QtWidgets.QLabel("", self.widget)
            self.text_stylesheet = self.text.styleSheet()

            self.video = QtWidgets.QWidget(self.widget)

            self.object_list = QtWidgets.QTextEdit(self.widget)
            self.object_list.setReadOnly(True)

            self.lay.addWidget(self.text)
            self.lay.addWidget(self.video)
            
            # ad an invisible widget on top of the video
            self.video_lay = QtWidgets.QHBoxLayout(self.video)
            self.overlay_widget = MyGui.OverlayWidget(self.video)
            # overlay_widget.signals.current_rectangle
            self.video_lay.addWidget(self.overlay_widget)
            
            self.text.setSizePolicy(
                QtWidgets.QSizePolicy.Minimum,
                QtWidgets.QSizePolicy.Minimum)
            self.video.setSizePolicy(
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding)
            
            self.lay.addWidget(self.object_list)
            
            self.signals.movement.connect(self.set_moving)
            self.signals.still.connect(self.set_still)
            self.signals.current_frames.connect(self.overlay_widget.set_frames_slot)
            
            self.set_still()
            
            self.mstimestampsave = 0
            self.mstimetolerance = 2000 # this far away in time are accepted
            self.mscleartime = 2000 # detection rectangles are cleared
            self.frame_list = []
            
            
        def getWindowId(self):
            return int(self.video.winId())

        def setText(self, txt):
            self.text.setText(txt)

        def set_still(self):
            self.setText("still")
            self.widget.setStyleSheet(self.text_stylesheet)
            self.frame_list = [] # reset detection frames when image is still
            self.signals.current_frames.emit(self.frame_list) 

        def set_moving(self):
            self.setText("MOVING")
            self.widget.setStyleSheet(
                "QLabel {border: 2px; border-style:solid; border-color: red; margin:0 px; padding:0 px; border-radius:8px;}")

        def add_object(self, tup):
            # [('sofa', 61, 236, 474, 108, 232, 1, 1560108601550), ('chair', 52, 123, 199, 96, 250, 1, 1560108601550)] # object, prob, left, right, top, bottom, slot, mstimestamp
            name = tup[0]
            mstimestamp = tup[7]
            # print("add_object:", tup)
            
            
            # - accept only detection events that are enough separated in time
            # - if enought time has passed, clear the detection rectangles first
            # - accept only detection events from the rectangle
            if (mstimestamp - self.mstimestampsave) >= self.mscleartime:
                self.frame_list = []
            
            if (mstimestamp - self.mstimestampsave) > self.mstimetolerance: # accept a new event
                #print("add_object: object accepted by time", tup)
                left, right, top, bottom = self.overlay_widget.getDrawRect()
                if (tup[2] >= left and tup[3] <= right and tup[4] <= top and tup[5] >= bottom):
                    #print("add_object: object accepted by geom", tup)
                    self.objects.append(name)
                    # NOTICE: so, this event would go to your database
                    if len(self.objects) > 5:
                        self.objects.pop(0)
                    txt = ""
                    for obj in self.objects:
                        txt += str(self.counter) +": "+ obj +"\n"
                        self.counter += 1
                    self.object_list.setText(txt)
                    self.frame_list.append(
                        (tup[2], tup[3], tup[4], tup[5]) # left, right, top, bottom
                        )
                    self.signals.current_frames.emit(self.frame_list)
                    
            self.mstimestampsave = mstimestamp
                    
    debug = False
    # debug=True


    class Signals(QtCore.QObject):
        movement = QtCore.Signal(object)

    def __init__(self, pardic, parent=None):
        super(MyGui, self).__init__()
        self.signals = self.Signals()
        self.pardic = pardic
        self.initVars()
        self.setupUi()
        if (self.debug):
            return
        self.openValkka()

    def initVars(self):
        pass

    def setupUi(self):
        self.signals.movement.connect(self.movement_slot)
        self.setGeometry(QtCore.QRect(100, 100, 800, 800))
        self.w = QtWidgets.QWidget(self)
        self.setCentralWidget(self.w)
        self.lay = QtWidgets.QGridLayout(self.w)
        self.frames = []  # frames with movement detector alert and video
        self.addresses = self.pardic["cams"]

    def openValkka(self):
        # the very first thing: create & start the multiprocess
        process = QValkkaGlobalDetectorProcess( # TODO
            "valkka_process",
            shmem_name       = shmem_name,
            n_buffer         = shmem_ringbuffer_size,
            image_dimensions = shmem_image_dimensions)

        self.processes = [process]

        # Give the multiprocesses to a qthread that's reading their message
        # pipe
        self.thread = QValkkaThread(processes = self.processes)

        # starts the multiprocesses
        self.startProcesses()
        # ..so, forks have been done.  Now we can spawn threads
        
        self.shmem_framefilter = RGBShmemFrameFilter( # creates the shmem server-side
            shmem_name,
            shmem_ringbuffer_size,
            shmem_image_dimensions[0], # max image dimensions that the shmem can handle
            shmem_image_dimensions[1]
        )
        
        self.threadsafe_filter = ThreadSafeFrameFilter("thread_safe", self.shmem_framefilter)
        
        self.livethread = LiveThread(         # starts live stream services (using live555)
            name="live_thread",
            verbose=False,
            affinity=self.pardic["live affinity"]
        )

        self.openglthread = OpenGLThread(     # starts frame presenting services
            name="mythread",
            # reserve stacks of YUV video frames for various resolutions
            n_720p  =self.pardic["n_720p"],
            n_1080p =self.pardic["n_1080p"],
            n_1440p =self.pardic["n_1440p"],
            n_4K    =self.pardic["n_4K"],
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
            chain = MovementFilterchain(       # decoding and branching the stream happens here
                livethread      = self.livethread,
                openglthread    = self.openglthread,
                address         = address,
                slot            = cs,
                affinity        = a,
                msreconnect     = 10000,
                
                movement_interval = 1000,
                movement_treshold = 0.01,
                movement_duration = 5000,
                image_dimensions  = image_dimensions,
                
                threadsafe_filter = self.threadsafe_filter,
                movement_callback  = self.movement_callback
                
                # time_correction   =TimeCorrectionType_smart # this is the default, no need to specify
            )
            self.chains.append(chain)

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
            print("setupUi: token=", token)
            # connect signal from current frame to self.selection_slot
            # frame.overlay_widget.signals.current_rectangle.connect(lambda x: self.selection_slot(cs, token, x))
            # frame.overlay_widget.signals.draw_rectangles.connect(lambda bbox_list: self.draw_rectangles_slot(token, bbox_list))
            frame.overlay_widget.setToken(token)
            frame.overlay_widget.signals.draw_rectangles.connect(self.draw_rectangles_slot)
    
            chain.decodingOn()  # tell the decoding thread to start its job
            cs += 1
            a += 1
            cc += 1

        process = self.processes[0]
        process.createClient()  # creates the shared memory client at the multiprocess
        # connect signals to the nested widget
        process.signals.detected_objects.connect(self.detected_objects_slot)
        # process.signals.stop_move. connect(frame.set_still)


    def movement_callback(self, tup):
        try:
            # print("test_callback:", tup) # (False, 1, 1560108596547)
            
            """
            status = tup[0]
            slot = tup[1]
            index = slot - 1
            """
            
            """# segfault follows:
            if status == True:
                self.frames[index].set_moving()
            else:
                self.frames[index].set_still()
            # messing with the widgets should be done via the signal / slot system
            """
            
            """# this is ok
            if status == True:
                self.frames[index].signals.movement.emit()
            else:
                self.frames[index].signals.still.emit()
            """
            # let's try this:
            self.signals.movement.emit(tup) # this is connected to movement_slot
            # so .. in python callbacks emitted from valkka, just call qt's signal/slot system & exit immediately
               
        except Exception as e:
            print("movement_callback failed with", str(e))
            
        
    def movement_slot(self, tup):
        # print("movement_slot:", tup)
        status = tup[0]
        slot = tup[1]
        index = slot - 1
        if status == True:
            self.frames[index].set_moving()
        else:
            self.frames[index].set_still()
        
        
    def detected_objects_slot(self, lis):
        # print("detected_objects_slot: got:", lis)
        # return
        # e.g.:
        # [('sofa', 61, 236, 474, 108, 232, 1, 1560108601550), ('chair', 52, 123, 199, 96, 250, 1, 1560108601550)] # object, prob, left, right, top, bottom, slot, mstimestamp
        # object, coords, slot, mstimestamp
        for tup in lis:
            index = tup[6] - 1 # index = slot - 1
            # self.frames[index].add_object(tup[0])
            self.frames[index].add_object(tup)
        
    """
    def selection_slot(self, slot, context_id, bbox):
        print("selection_slot: for slot number", slot)
        self.openglthread.core.addRectangleCall(context_id, bbox[0], bbox[1], bbox[2], bbox[3])
    """
       
        
    def draw_rectangles_slot(self, tup):
        context_id = tup[0]
        bbox_list = tup[1]
        # print("draw_rectangles_slot: context_id=", context_id)
        self.openglthread.core.clearObjectsCall(context_id)
        for bbox in bbox_list:
            # print("draw_rectangles_slot:", bbox) # (381, 463, 35, 256)
            self.openglthread.core.addRectangleCall(context_id, bbox[0], bbox[1], bbox[2], bbox[3])
        
        
    def startProcesses(self):
        self.thread.start()
        for p in self.processes:
            p.start()

    def stopProcesses(self):
        for p in self.processes:
            p.stop()
        print(pre, "stopping QThread")
        self.thread.stop()
        print(pre, "QThread stopped")

    def closeValkka(self):
        self.livethread.close()

        for chain in self.chains:
            chain.close()

        self.chains = []
        self.widget_pairs = []
        self.videoframes = []
        self.openglthread.close()

    def closeEvent(self, e):
        print(pre, "closeEvent!")
        self.stopProcesses()
        self.closeValkka()
        super().closeEvent(e)


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
