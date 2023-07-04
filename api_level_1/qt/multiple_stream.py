"""
multiple_stream.py : A demo program streaming from various rtsp cameras and other sources (defined per .sdp files)

Copyright 2017, 2018 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    multiple_stream.py
@author  Sampsa Riikonen
@date    2017
@version 1.4.0 
@brief   A demo program streaming from various rtsp cameras and other sources (defined per .sdp files)
"""

# from PyQt5 import QtWidgets, QtCore, QtGui # If you use PyQt5, be aware of the licensing consequences
from PySide2 import QtWidgets, QtCore, QtGui
import sys
from valkka.core import *


class FilterChain:
    """
    So, you've learned from

    https://elsampsa.github.io/valkka-core/html/process_chart.html

    that:

    * Concatenating FrameFilters, creates a simple callback cascade
    * Threads write to a FrameFilter
    * Threads read from a FrameFifo
    * FrameFifos have an internal stack of pre-reserved frames

    In this class, we implement a part of the filterchain - so that we don't have to write it explicitly for each camera.

    The filtergraph (**) here looks like this:

    --> {FifoFrameFilter:av_in_filter} --> [FrameFifo:av_fifo] -->> (AVThread:avthread) --> {FifoFrameFilter:gl_in_gilter} -->

    Parameters:

    :param gl_in_filter:  Bitmap (decoded) frames are written here
    :param window_id:     Video is dumped into this x-window
    :address:             Stream source: either filename (supposedly an sdp file) or "rtsp://.." rtsp address
    :slot:                Slot number identifying this stream

    Some rarameters accessed through a get method

    :param getConnectionCtx: Returns the connection context that can be passed to LiveThread.

    """

    def __init__(self, gl_in_filter, window_id, address, slot):
        self.gl_in_filter = gl_in_filter
        self.window_id = window_id
        self.address = address
        self.slot = slot
        self.render_ctx = None

        self.avthread = AVThread("avthread", self.gl_in_filter)
        self.av_in_filter = self.avthread.getFrameFilter()

        self.ctx = LiveConnectionContext()
        self.ctx.slot = slot
        if (self.address.find("rtsp://") > -1):
            self.ctx.connection_type = LiveConnectionType_rtsp
        else:
            self.ctx.connection_type = LiveConnectionType_sdp
        self.ctx.address = self.address
        self.ctx.framefilter = self.av_in_filter
        self.ctx.msreconnect = 0  # do reconnection if the stream dies out

        self.avthread.startCall()
        self.avthread.decodingOnCall()

    def getSlot(self):
        return self.slot

    def getConnectionCtx(self):
        return self.ctx

    def getWindowId(self):
        return self.window_id

    def decodingOn(self):
        self.avthread.decodingOnCall()

    def decodingOff(self):
        self.avthread.decodingOffCall()

    # These two setters and getters are used simply to save the render context id
    def setRenderCtx(self, n):
        self.render_ctx = n

    def getRenderCtx(self):
        return self.render_ctx

    def stop(self):
        self.avthread.stopCall()

    def __del__(self):  # call at garbage collection
        self.stop()


class MyGui(QtWidgets.QMainWindow):

    def __init__(self, parent=None, addresses=[]):
        super(MyGui, self).__init__()
        self.debug = False
        # self.debug=True
        if (len(addresses) < 1):
            print("No streams!")
            return
        self.addresses = addresses
        self.n_streams = len(self.addresses)
        self.initVars()
        self.setupUi()
        if (self.debug):
            return
        self.openValkka()
        self.makeFilterChains()
        self.start_streams()

    def initVars(self):
        self.filterchains = []
        self.videoframes = []

    def setupUi(self):
        self.setGeometry(QtCore.QRect(100, 100, 500, 500))

        self.w = QtWidgets.QWidget(self)
        self.setCentralWidget(self.w)

        self.lay = QtWidgets.QGridLayout(self.w)

        for i, address in enumerate(self.addresses):
            fr = QtWidgets.QFrame(self.w)
            print("setupUi: layout index, address : ", i//4, i % 4, address)
            self.lay.addWidget(fr, i//4, i % 4)
            # list of (QFrame, address) pairs
            self.videoframes.append((fr, address))

    def openValkka(self):
        """
        Filtergraph:
        (LiveThread:livethread) --> FilterChain --> {FifoFrameFilter:gl_in_gilter} --> [OpenGLFrameFifo:gl_fifo] -->> (OpenGLThread:glthread)

        See "single_stream_rtsp.py" for more details !
        """
        self.gl_ctx = OpenGLFrameFifoContext()
        self.gl_ctx.n_720p = 20
        self.gl_ctx.n_1080p = 20
        self.gl_ctx.n_1440p = 20
        self.gl_ctx.n_4K = 20
        self.gl_ctx.n_setup = 20
        self.gl_ctx.n_signal = 20
        self.gl_ctx.flush_when_full = False

        self.glthread = OpenGLThread("glthread", self.gl_ctx)
        self.gl_in_filter = self.glthread.getFrameFilter()
        self.livethread = LiveThread("livethread")

        # Start threads
        self.glthread.  startCall()
        self.livethread.startCall()

    def closeValkka(self):
        self.livethread.stopCall()
        self.glthread.  stopCall()

    def makeFilterChains(self):
        # videoframe == (QFrame, address) pairs
        for i, videoframe in enumerate(self.videoframes):
            # QFrame.windId() returns x-window id
            window_id = int(videoframe[0].winId())
            address = videoframe[1]
            self.filterchains.append(FilterChain(
                self.gl_in_filter, window_id, address, i+1))

    def start_streams(self):
        print("starting streams")
        for filterchain in self.filterchains:
            ctx = filterchain.getConnectionCtx()
            self.livethread.registerStreamCall(ctx)
            self.livethread.playStreamCall(ctx)
            filterchain.decodingOn()

            window_id = filterchain.getWindowId()
            self.glthread.newRenderGroupCall(window_id)
            context_id = self.glthread.newRenderContextCall(
                filterchain.getSlot(), window_id, 0)
            # save context id to filterchain
            filterchain.setRenderCtx(context_id)

    def stop_streams(self):
        print("stopping streams")
        for filterchain in self.filterchains:
            filterchain.stop()
            ctx = filterchain.getConnectionCtx()
            self.livethread.stopStreamCall(ctx)
            self.livethread.deregisterStreamCall(ctx)
            self.glthread.delRenderContextCall(filterchain.getRenderCtx())
            self.glthread.delRenderGroupCall(filterchain.getWindowId())

    def closeEvent(self, e):
        print("closeEvent!")
        self.stop_streams()
        self.closeValkka()
        e.accept()


def main():
    if (len(sys.argv) < 2):
        print("Give multiple rtsp and sdp stream addresses, i.e. rtsp://passwd1:user1@ip1 sdp_filename1 sdp_filename2 rtsp://passwd2:user2@i2")
        return
    app = QtWidgets.QApplication(["multiple_stream_test"])
    mg = MyGui(addresses=sys.argv[1:])
    mg.show()
    app.exec_()


if (__name__ == "__main__"):
    main()
