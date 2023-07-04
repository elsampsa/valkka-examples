"""
multiprocessing_demo.py : Use Qt with python multiprocesses

Copyright 2018 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    multiprocessing_demo.py
@author  Sampsa Riikonen
@date    2018
@version 1.4.0 
@brief   Use Qt with python multiprocesses
"""

# from PyQt5 import QtWidgets, QtCore, QtGui # If you use PyQt5, be aware of the licensing consequences
from PySide2 import QtWidgets, QtCore, QtGui
import sys
import time
from setproctitle import setproctitle
from valkka.api2 import dictionaryCheck
from valkka.multiprocess import MessageProcess, MessageObject, safe_select
# import from the local directory
from demo_qthread import QHandlerThread

class TestProcess(MessageProcess):
    """This class implements the frontend/backend model of multiprocessing:

    ::

        Backend methods (designated with __ or with c__) <=PIPE=> Frontend methods
          Backend reads the pipe and multiplexes                    You just call these
          also any other communication channels                     from your python main process


    Backend is _the_ multiprocess running in its own virtual memory space, isolated from the rest of the processes.

    Intercommunication is handled under-the-hood, making life easier for the API programmer that just calls Frontend methods.
    """
    class Signals(QtCore.QObject):
        """These signals are instantiated into the member "signals"

        Typically emitted by a QThread that's listening to this processes self.front_pipe
        """
        # PyQt5
        #pong = QtCore.pyqtSignal(object)
        # PySide2
        pong = QtCore.Signal(object)

    def __init__(self, mstimeout=1000):
        super().__init__()
        self.mstimeout = mstimeout
        self.signals = self.Signals()

    """PROCESS BACKEND methods
    """
    def preRun__(self):
        """This should be subclassed for your multiprocess class.  It is executed just after the fork (i.e. in the backend)

        Use this to do variable initialization etc. before the async execution starts and for naming your multiprocess
        """
        print("preRun__")
        # name your multiprocess: now you can easily find it with linux process and memory
        # monitoring tools
        # I recommend using smem and/or htop
        setproctitle("Valkka-example-Process")

    def postRun__(self):
        """Last thing executed before multiprocess exits
        """
        print("postRun__")

    def readPipes__(self, timeout):
        """Multiplex all intercom pipes / events

        This is used by your multiprocesses run() method
        (which you don't need to touch)

        Multiplexing file-descriptor is actually more neat in asyncio: 
        see the fragmp4 process

        For a tutorial for multiplexing communication pipes and sockets
        in normal (not asyncio) python, see: https://docs.python.org/3/howto/sockets.html
        """
        rlis = [self.back_pipe]
        rs, ws, es = safe_select(rlis, [], [], timeout=timeout)
        for fd in rs:
            # 1. handle the main intercom pipe
            if fd is self.back_pipe:
                self.handleBackPipe__(self.back_pipe)

    def sendSignal__(self, name):
        self.send_out__({"signal": name}) # send a dict object to the frontend
        # this message is typically captured by a QThread running in the frontend
        # which then converts it into a Qt signal

    # commands that come from the main python process (aka frontend)
    def c__ping(self, parameter=1):
        """The backend part of some custom call
        """
        print("multiprocess got PING - sending back a PONG")
        self.sendSignal__("pong")


    """PROCESS FRONTEND
    
    These methods are called by your main python process
    """

    def ping(self, parameter=1):
        # your demo custom call :)
        self.sendMessageToBack(MessageObject(
            "ping",
            parameter=parameter
        ))
        # that intercommunicates with backend and looks
        # for method "c__ping" therein


class MyGui(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(MyGui, self).__init__()
        self.initVars()
        self.setupUi()
        self.startProcesses()

    def initVars(self):
        self.p = TestProcess()
        self.t = QHandlerThread()
        
    def startProcesses(self):
        # start first multiprocess, then thread
        self.p.start()
        self.t.start()
        self.t.addProcess(self.p)
        # ..now QHanderThread listens to the multiprocess
        # and translates its messages into qt signals

    def stopProcesses(self):
        self.p.stop()
        self.t.stop()

    def setupUi(self):
        self.setGeometry(QtCore.QRect(100, 100, 500, 500))
        self.w = QtWidgets.QWidget(self)
        self.setCentralWidget(self.w)

        self.lay = QtWidgets.QVBoxLayout(self.w)
        self.button = QtWidgets.QPushButton("send signal", self.w)
        self.field = QtWidgets.QLineEdit("", self.w)
        self.lay.addWidget(self.button)
        self.lay.addWidget(self.field)
        
        self.button.clicked.connect(self.button_slot)
        self.p.signals.pong.connect(self.pong_slot)


    def button_slot(self):
        """From the main GUI to the multiprocess
        """
        self.p.ping(parameter=1)


    def pong_slot(self, msg):
        """From the multiprocess to the main GUI
        """
        self.field.setText("got pong from multiprocess")


    def closeEvent(self, e):
        print("closeEvent!")
        e.accept()
        self.stopProcesses()


def main():
    app = QtWidgets.QApplication(["test_app"])
    mg = MyGui()
    mg.show()
    app.exec_()


if (__name__ == "__main__"):
    main()
