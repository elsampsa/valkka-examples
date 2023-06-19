"""
test_studio_5.py : Test live streaming, recording and playback in Qt

Copyright 2017-2021 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    test_studio_5.py
@author  Sampsa Riikonen
@date    2019
@version 1.3.6 
@brief   Test live streaming, recording and playback in Qt


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

# from PyQt5 import QtWidgets, QtCore, QtGui # If you use PyQt5, be aware
# of the licensing consequences

# Qt
from PySide2 import QtWidgets, QtCore, QtGui

# stdlib
import sys
import json
import os
import time
import datetime
import logging

# https://stackoverflow.com/questions/47167251/pygilstate-ensure-causing-deadlock
# https://stackoverflow.com/questions/37513957/does-python-gil-need-to-be-taken-care-when-work-with-multi-thread-c-extension
""" # well, it was not this
import threading
t = threading.Thread(target=lambda: None, daemon=True)
t.run()
del t
"""

# valkka
from valkka.api2 import LiveThread, OpenGLThread # , ValkkaFS, ValkkaFSManager
from valkka.fs import ValkkaFSManager, ValkkaMultiFS, ValkkaSingleFS
from valkka.api2.logging import setValkkaLogLevel, loglevel_silent, loglevel_crazy
from valkka import core # for logging

# Local imports form this directory
from valkkafs import ValkkaFSLiveFilterchain, ValkkaFSFileFilterchain
# from valkkafs2 import ValkkaFSConfig
from valkkafs3 import ValkkaFSConfigMany
from demo_base import ConfigDialog, TestWidget0, getForeignWidget, WidgetPair
from playback import PlaybackController
from playwidget import TimeLineWidget, CalendarWidget
from playback import WidgetSet as PlayBackWidgetSet

# # this is now controlled with the "no_rec" command line argument
use_live = True
# use_live = False

pre = __name__  # aux string for debugging

# valkka_xwin =True # use x windows create by Valkka and embed them into Qt
valkka_xwin = False  # use Qt provided x windows

# setValkkaLogLevel(loglevel_silent) # set all loggers to silent
# setValkkaLogLevel(loglevel_crazy)
# core.setLogLevel_livelogger(loglevel_crazy) # set an individual loggers

""" # a nice debugging set:
core.setLogLevel_threadlogger(loglevel_crazy)
core.setLogLevel_valkkafslogger(loglevel_debug)
core.setLogLevel_avthreadlogger(loglevel_debug)
core.setLogLevel_valkkafslogger(loglevel_debug)
"""

valkka_fs_dirname = "fs_directory"
blocksize_default = 25*1024*1024 # blocksize in B # one block per two seconds, assuming 25 fps, 2Mbits/sec, 2 cameras, key frame each second for both
n_blocks_default = 100 # 2.5 GB in total

class MyConfigDialog(ConfigDialog):
    
    def __init__(self, parent = None):
        super().__init__(parent)
        if os.path.exists("test_studio_6_fs.config"):
            with open("test_studio_6_fs.config","r") as f:
                pars=json.loads(f.read())
        else:
            pars={
                "blocksize" :1,
                "n_blocks" :100,
            }
        pars["parent"] = self
        self.fs_config = ValkkaFSConfigMany(**pars)
        self.lay.addWidget(self.fs_config.main_widget)


    def setConfigPars(self):
        self.tooltips = {        # how about some tooltips?
        }
        self.config_fname = "test_studio_6.config"  # define the config file name

    
    def saveValkkaFSPars(self):
        if os.path.exists("test_studio_6_fs.config"):
            with open("test_studio_6_fs.config","w") as f:
                f.write(json.dumps(self.fs_config.getParDic()))


    def getValkkaFSPars(self):
        # blocksize, n_blocks,format = self.fs_config.getValkkaFSPars()
        return self.fs_config.getValkkaFSPars()


class MyTabWidget(QtWidgets.QTabWidget):
    
    
    def __init__(self, parent):
        super().__init__(parent)
        self.accept_close = False
        
        
    def forceClose(self):
        self.accept_close = True
        self.close()
    
    def closeEvent(self, e):
        if self.accept_close:
            e.accept()
        else:
            e.ignore()
        

class MyGui(QtWidgets.QMainWindow):

    debug = False
    # debug=True

    def __init__(self, pardic=None, blocksize=None, n_blocks=None, format=None, parent=None):
        super(MyGui, self).__init__()
        self.pardic = pardic
        self.blocksize = blocksize
        self.n_blocks = n_blocks
        self.format = format
        self.initVars()
        self.setupUi()
        if (self.debug):
            return
        self.openValkka()
        self.start_streams()

    def initVars(self):
        pass

    def setupUi(self):
        self.setGeometry(QtCore.QRect(100, 100, 800, 800))
        self.w = QtWidgets.QWidget(self)
        self.setCentralWidget(self.w)
        self.lay = QtWidgets.QGridLayout(self.w)

        self.videoframes = []
        self.widget_pairs = []
        self.addresses = self.pardic["cams"]

        # self.rec_window = QtWidgets.QMainWindow(self)
        # self.rec_window = QtWidgets.QTabWidget(None)
        self.rec_window = MyTabWidget(None)
        self.rec_window.setGeometry(QtCore.QRect(50, 50, 800, 800))
        self.rec_window.show()
        
        self.rec_video_tab = QtWidgets.QWidget(None)
        self.rec_video_lay = QtWidgets.QVBoxLayout(self.rec_video_tab)
        
        self.rec_calendar_tab = QtWidgets.QWidget(None)
        self.rec_calendar_lay = QtWidgets.QVBoxLayout(self.rec_calendar_tab)
        
        self.rec_window.addTab(self.rec_video_tab, "Video")
        self.rec_window.addTab(self.rec_calendar_tab, "Calendar")
        
        self.rec_video_area = QtWidgets.QWidget(self.rec_video_tab)
        self.rec_video_area.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)

        self.rec_video_area_lay = QtWidgets.QGridLayout(self.rec_video_area)
        self.rec_video_lay.addWidget(self.rec_video_area)
        
        # timeline
        self.timelinewidget = TimeLineWidget(datetime.date.today(), parent = self.rec_video_area)
        # self.timelinewidget.setLogLevel(logging.DEBUG)
        self.rec_video_lay.addWidget(self.timelinewidget)
        
        # buttons
        self.buttons = QtWidgets.QWidget(self.rec_video_area)
        self.buttons_lay = QtWidgets.QHBoxLayout(self.buttons)
        self.play_button = QtWidgets.QPushButton("play", self.buttons)
        self.stop_button = QtWidgets.QPushButton("stop", self.buttons)
        self.zoom_to_fs_button = QtWidgets.QPushButton("limits", self.buttons)
        self.buttons_lay.addWidget(self.play_button)
        self.buttons_lay.addWidget(self.stop_button)
        self.buttons_lay.addWidget(self.zoom_to_fs_button)
        self.rec_video_lay.addWidget(self.buttons)
        
        # calendar
        self.calendarwidget = CalendarWidget(datetime.date.today(), parent = self.rec_calendar_tab)
        self.rec_calendar_lay.addWidget(self.calendarwidget)
        
        
    def openValkka(self):
        # create some valkkafs'
        valkkafslist = []
        valkkafs_per_address = {}
        for i, address in enumerate(self.addresses):
            dirname="fs_directory_%i" % (i)
            print("checking directory", dirname)
            if self.format:
                print("(re)creating valkkafs for stream", address)
                fs = ValkkaSingleFS.newFromDirectory(
                    dirname         = dirname,
                    blocksize       = self.blocksize * 1024 * 1024, # back to bytes
                    n_blocks        = self.n_blocks, 
                    device_size     = None, # calculate from blocksize and n_blocks
                    partition_uuid  = None,
                    # verbose         = True
                    verbose         = False
                )
            else:
                try: 
                    ValkkaSingleFS.checkDirectory(dirname)
                except AssertionError as e:
                    print("can't read ValkkaFS directory:", e, "consider removing", dirname)
                    sys.exit(2)
                fs = ValkkaSingleFS.loadFromDirectory(dirname)
            valkkafs_per_address[address] = fs
            valkkafslist.append(fs)

        self.valkkafsmanager = ValkkaFSManager(
            valkkafslist
        )

        self.playback_controller = PlaybackController(
            valkkafs_manager    = self.valkkafsmanager,
            )

        self.widget_set = PlayBackWidgetSet(
            timeline_widget     = self.timelinewidget,
            play_button         = self.play_button,
            stop_button         = self.stop_button,
            calendar_widget     = self.calendarwidget,
            zoom_to_fs_button   = self.zoom_to_fs_button
        )

        self.playback_controller.register(self.widget_set)
    
        self.livethread = LiveThread(         # starts live stream services (using live555)
            name="live_thread",
            # verbose=True,
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
            # verbose =True,
            verbose=False,
            msbuftime=self.pardic["msbuftime"],
            affinity=self.pardic["gl affinity"]
        )

        # start writer, reader & cacher threads
        self.valkkafsmanager.start()

        if (self.openglthread.hadVsync()):
            w = QtWidgets.QMessageBox.warning(
                self,
                "VBLANK WARNING",
                "Syncing to vertical refresh enabled\n THIS WILL DESTROY YOUR FRAMERATE\n Disable it with 'export vblank_mode=0' for nvidia proprietary drivers, use 'export __GL_SYNC_TO_VBLANK=0'")

        tokens = []
        self.chains = []

        a = self.pardic["dec affinity start"]
        cw = 0  # widget / window index
        cs = 1  # slot / stream count

        for address in self.addresses:
            # now livethread and openglthread are running
            if (a > self.pardic["dec affinity stop"]):
                a = self.pardic["dec affinity start"]
            print(pre, "openValkka: setting decoder thread on processor", a)

            valkkafs = valkkafs_per_address[address]

            if use_live:
                # live filterchain needs a terminal
                # to dump the frames: rec_framefilter
                chain_live = ValkkaFSLiveFilterchain(       # decoding and branching the stream happens here
                    rec_framefilter = self.valkkafsmanager.getInputFilter(
                        valkkafs = valkkafs
                    ),
                    livethread = self.livethread,
                    address = address,
                    slot = cs,
                    affinity = a,
                    # verbose     =True
                    verbose = False,
                    msreconnect = 10000,
                    # Reordering buffer time for Live555 packets in MILLIseconds # 0 means default
                    reordering_mstime=0
                    # reordering_mstime =300
                )
                
            rec_slot = cs + 100 # live and rec slot numbers must be kept separated ..

            chain_rec = ValkkaFSFileFilterchain(       # decoding and branching the stream happens here
                slot = rec_slot,
                affinity = a,
                # verbose     =True
                verbose = False
            )
            # fs filterchain needs input/source
            # where the frames are coming:
            self.valkkafsmanager.map_(
                valkkafs = valkkafs,
                # recorded stream playback output:
                framefilter = chain_rec.getInputFilter(),
                write_slot = cs,
                read_slot = rec_slot,
                _id = cs
            )

            """
            # for case when recording yes, but don't want playback
            self.valkkafsmanager.map_(
                valkkafs = valkkafs,
                # recorded stream playback output:
                framefilter = None,
                write_slot = cs,
                read_slot = None,
                _id = cs
            )
            """
            
            # send yuv to OpenGLThread
            if use_live: chain_live.connect_to_yuv("yuv_to_opengl_"+str(cs), self.openglthread.getInput())
            chain_rec.connect_to_yuv("yuv_to_opengl_"+str(cs), self.openglthread.getInput())

            # important .. otherwise chain will go out of context and get
            # garbage collected ..
            if use_live: self.chains.append(chain_live)
            self.chains.append(chain_rec)

            if ("no_qt" in self.pardic):
                # create our own x-windowses
                win_id     = self.openglthread.createWindow(show=True)
                win_id_rec = self.openglthread.createWindow(show=True)
                
            else:
                # *** Choose one of the following sections ***

                # (1) Let Valkka create the windows/widget # use this: we get a window with correct parametrization
                # win_id =self.openglthread.createWindow(show=False)
                # fr     =getForeignWidget(self.w, win_id)

                if (valkka_xwin == False):
                    # (2) Let Qt create the widget
                    fr = TestWidget0(self.w)
                    win_id = int(fr.winId())
                    
                    fr_rec = TestWidget0(self.rec_video_area)
                    win_id_rec = int(fr_rec.winId())
                    
                else:
                    # """
                    # (3) Again, let Valkka create the window, but put on top a translucent widget (that catches mouse gestures)
                    win_id = self.openglthread.createWindow(show=False)
                    widget_pair = WidgetPair(self.w, win_id, TestWidget0)
                    fr = widget_pair.getWidget()
                    self.widget_pairs.append(widget_pair)
                    
                    win_id_rec = self.openglthread.createWindow(show=False)
                    widget_pair = WidgetPair(self.rec_video_area, win_id_rec, TestWidget0)
                    fr_rec = widget_pair.getWidget()
                    self.widget_pairs.append(widget_pair)
                    # """

                nrow = self.pardic["videos per row"]
                print(pre, "setupUi: layout index, address : ",
                    cw // nrow,
                    cw % nrow,
                    address)
                
                self.lay.addWidget(fr, cw // nrow, cw % nrow)
                self.rec_video_area_lay.addWidget(fr_rec, cw // nrow, cw % nrow)
                
                self.videoframes.append(fr)
                self.videoframes.append(fr_rec)
                

            # present frames with slot number cs at window win_id
            
            # rec_slot = cs # debug
            
            print(pre, "setupUi: live:", cs, win_id)
            print(pre, "setupUi: rec :", rec_slot, win_id_rec)
            
            token = self.openglthread.connect(slot = cs, window_id = win_id)
            tokens.append(token)
            token = self.openglthread.connect(slot = rec_slot, window_id = win_id_rec)
            tokens.append(token)
            
            cw += 1
            cs += 1

            if use_live: chain_live.decodingOn()  
            # ..tell the decoding thread to start its job
            chain_rec .decodingOn()

            a += 1


    def closeValkka(self):
        self.livethread.close()
        self.valkkafsmanager.close()
        for chain in self.chains:
            chain.close()
        self.chains = []
        self.widget_pairs = []
        self.videoframes = []
        self.openglthread.close()
        
        # time.sleep(5)
        

    def start_streams(self):
        pass

    def stop_streams(self):
        pass

    def closeEvent(self, e):
        print("\n", pre, "closeEvent!\n")
        self.stop_streams()
        self.closeValkka()
        self.rec_window.forceClose()
        # self.rec_window.close()
        e.accept()


def main():
    global use_live
    
    if len(sys.argv) > 1:
        print(sys.argv)
        if sys.argv[1] == "no_rec":
            print("\nWARNING: starting in playback-only mode")
            use_live = False
    
    app = QtWidgets.QApplication(["test_app"])
    conf = MyConfigDialog()
    pardic = conf.exec_()
    if (pardic["ok"]):
        blocksize, n_blocks, format = conf.getValkkaFSPars()
        conf.saveValkkaFSPars()
        mg = MyGui(
                pardic = pardic,
                blocksize = blocksize,
                n_blocks = n_blocks,
                format = format
            )
        mg.show()
        app.exec_()


if (__name__ == "__main__"):
    main()
