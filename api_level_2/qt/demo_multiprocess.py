"""
demo_multiprocess.py : Multiprocesses / Qt intercommunication through pipes and signals.  See the test_studio_*.py for examples.

Copyright 2017, 2018 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    demo_multiprocess.py
@author  Sampsa Riikonen
@date    2017
@version 1.2.0 
@brief   Multiprocesses / Qt intercommunication through pipes and signals


When using python multiprocesses with Qt, we need a frontend thread that reads the process communication pipes and turns the messages sent by the process into Qt signals.

This file has QValkkaProcess, QValkkaOpenCVProcess and QValkkaThread - everything you need to get started with multiprocessing image analysis in Qt.  We suggest that you make a copy of this into your own module.
"""

# from PyQt5 import QtWidgets, QtCore, QtGui # If you use PyQt5, be aware
# of the licensing consequences
from PySide2 import QtWidgets, QtCore, QtGui
import sys
import time
from valkka.api2 import ValkkaProcess, Namespace, safe_select, ShmemClient, ShmemRGBClient
from valkka.api2.tools import *


class QValkkaProcess(ValkkaProcess):
    """A multiprocess with Qt signals
    """

    incoming_signal_defs = {  # each key corresponds to a front- and backend methods
        "test_": {"test_int": int, "test_str": str},
        "stop_": [],
        "ping_": {"message": str}
    }

    outgoing_signal_defs = {
        "pong_o": {"message": str}
    }

    # For each outgoing signal, create a Qt signal with the same name.  The
    # frontend Qt thread will read processes communication pipe and emit these
    # signals.
    class Signals(QtCore.QObject):

        # pong_o  =QtCore.pyqtSignal(object) # PyQt5
        pong_o = QtCore.Signal(object)  # PySide2

    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.signals = self.Signals()

    def cycle_(self):
        # Do whatever your process should be doing, remember timeout every now
        # and then
        time.sleep(0.5)
        # print(self.pre,"hello!")

    # *** backend methods corresponding to incoming signals ***

    def stop_(self):
        self.running = False

    def test_(self, test_int=0, test_str="nada"):
        print(self.pre, "test_ signal received with", test_int, test_str)

    def ping_(self, message="nada"):
        print(
            self.pre,
            "At backend: ping_ received",
            message,
            "sending it back to front")
        self.sendSignal_(name="pong_o", message=message)

    # ** frontend methods launching incoming signals

    def stop(self):
        self.sendSignal(name="stop_")

    def test(self, **kwargs):
        dictionaryCheck(self.incoming_signal_defs["test_"], kwargs)
        kwargs["name"] = "test_"
        self.sendSignal(**kwargs)

    def ping(self, **kwargs):
        dictionaryCheck(self.incoming_signal_defs["ping_"], kwargs)
        kwargs["name"] = "ping_"
        self.sendSignal(**kwargs)

    # ** frontend methods handling received outgoing signals ***
    def pong_o(self, message="nada"):
        print("At frontend: pong got message", message)
        ns = Namespace()
        ns.message = message
        self.signals.pong_o.emit(ns)


class QValkkaOpenCVProcess(ValkkaProcess):
    """A multiprocess with Qt signals, using OpenCV.  Reads RGB images from shared memory
    """

    incoming_signal_defs = {  # each key corresponds to a front- and backend methods
        "create_client_" : [],
        "test_": {"test_int": int, "test_str": str},
        "stop_": [],
        "ping_": {"message": str}
    }

    outgoing_signal_defs = {
        "pong_o": {"message": str}
    }

    # For each outgoing signal, create a Qt signal with the same name.  The
    # frontend Qt thread will read processes communication pipe and emit these
    # signals.
    class Signals(QtCore.QObject):
        # pong_o  =QtCore.pyqtSignal(object) # PyQt5
        pong_o = QtCore.Signal(object)  # PySide2

    parameter_defs = {
        "n_buffer": (int, 10),
        "image_dimensions": tuple,
        "shmem_name": str
    }

    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.signals = self.Signals()
        parameterInitCheck(QValkkaOpenCVProcess.parameter_defs, kwargs, self)
        typeCheck(self.image_dimensions[0], int)
        typeCheck(self.image_dimensions[1], int)

    def preRun_(self):
        """Create the shared memory client after fork
        """
        super().preRun_()
        self.client = None

    def cycle_(self):
        if self.client is None:
            time.sleep(1.0)
        else:            
            index, isize = self.client.pull()
            if (index is None):
                print(self.pre, "Client timed out..")
            else:
                print(self.pre, "Client index, size =", index, isize)
                data = self.client.shmem_list[index]
                img = data.reshape(
                    (self.image_dimensions[1], self.image_dimensions[0], 3))
                """ # WARNING: the x-server doesn't like this, i.e., we're creating a window from a separate python multiprocess, so the program will crash
                print(self.pre,"Visualizing with OpenCV")
                cv2.imshow("openCV_window",img)
                cv2.waitKey(1)
                """
                print(self.pre, ">>>", data[0:10])

                # res=self.analyzer(img) # does something .. returns something ..


    def postCreateClient_(self):
        """Override in child methods: call after the shmem client has been created
        """
        pass


    # *** backend methods corresponding to incoming signals ***

    def stop_(self):
        self.running = False

    
    def create_client_(self):
        self.client = ShmemRGBClient(
            name=self.shmem_name,
            n_ringbuffer=self.n_buffer,   # size of ring buffer
            width=self.image_dimensions[0],
            height=self.image_dimensions[1],
            # client timeouts if nothing has been received in 1000 milliseconds
            mstimeout=1000,
            verbose=False
        )
        self.postCreateClient_()
        

    def test_(self, test_int=0, test_str="nada"):
        print(self.pre, "test_ signal received with", test_int, test_str)

    def ping_(self, message="nada"):
        print(
            self.pre,
            "At backend: ping_ received",
            message,
            "sending it back to front")
        self.sendSignal_(name="pong_o", message=message)

    # ** frontend methods launching incoming signals

    def stop(self):
        self.sendSignal(name="stop_")

    def createClient(self):
        self.sendSignal(name="create_client_")

    def test(self, **kwargs):
        dictionaryCheck(self.incoming_signal_defs["test_"], kwargs)
        kwargs["name"] = "test_"
        self.sendSignal(**kwargs)

    def ping(self, **kwargs):
        dictionaryCheck(self.incoming_signal_defs["ping_"], kwargs)
        kwargs["name"] = "ping_"
        self.sendSignal(**kwargs)

    # ** frontend methods handling received outgoing signals ***
    def pong_o(self, message="nada"):
        print(self.pre, "At frontend: pong got message", message)
        ns = Namespace()
        ns.message = message
        self.signals.pong_o.emit(ns)


class QValkkaThread(QtCore.QThread):
    """A QThread that sits between multiprocesses message pipe and Qt's signal system

    After ValkkaProcess instances have been given to this thread, they are accessible with:
    .process_name
    [process_index]

    The processes have methods that launch ingoing signals (like ping(message="hello")) and Qt signals that can be connected to slots (e.g. process.signals.pong_o.connect(slot))
    """

    def __init__(self, timeout=1, processes=[]):
        super().__init__()
        self.pre = self.__class__.__name__ + " : "
        self.timeout = timeout
        self.processes = processes
        self.process_by_pipe = {}
        self.process_by_name = {}
        for p in self.processes:
            self.process_by_pipe[p.getPipe()] = p
            self.process_by_name[p.name] = p

    def preRun(self):
        pass

    def postRun(self):
        pass

    def run(self):
        self.preRun()
        self.loop = True

        rlis = []
        wlis = []
        elis = []
        for key in self.process_by_pipe:
            rlis.append(key)

        while self.loop:
            tlis = safe_select(rlis, wlis, elis, timeout=self.timeout)
            for pipe in tlis[0]:
                # let's find the process that sent the message to the pipe
                p = self.process_by_pipe[pipe]
                # print("receiving from",p,"with pipe",pipe)
                st = pipe.recv()  # get signal from the process
                # print("got from  from",p,"with pipe",pipe,":",st)
                p.handleSignal(st)

        self.postRun()
        print(self.pre, "bye!")

    def stop(self):
        self.loop = False
        self.wait()

    def __getattr__(self, attr):
        return self.process_by_name[attr]

    def __getitem__(self, i):
        return self.processes[i]


class MyGui(QtWidgets.QMainWindow):
    """An example demo GUI
    """

    def __init__(self, parent=None):
        super(MyGui, self).__init__()
        self.initVars()
        self.setupUi()

    def initVars(self):
        self.process1 = QValkkaProcess("process1")
        self.process2 = QValkkaProcess("process2")

        self.process1.start()
        self.process2.start()

        self.thread = QValkkaThread(processes=[self.process1, self.process2])
        self.thread.start()

    def setupUi(self):
        self.setGeometry(QtCore.QRect(100, 100, 500, 500))
        self.w = QtWidgets.QWidget(self)
        self.setCentralWidget(self.w)

        self.lay = QtWidgets.QGridLayout(self.w)

        self.button1 = QtWidgets.QPushButton("Button 1", self.w)
        self.button2 = QtWidgets.QPushButton("Button 2", self.w)

        self.check1 = QtWidgets.QRadioButton(self.w)
        self.check2 = QtWidgets.QRadioButton(self.w)

        self.lay.addWidget(self.button1, 0, 0)
        self.lay.addWidget(self.check1, 0, 1)
        self.lay.addWidget(self.button2, 1, 0)
        self.lay.addWidget(self.check2, 1, 1)

        self.button1.clicked.connect(self.button1_slot)
        self.button2.clicked.connect(self.button2_slot)

        self.process1.signals.pong_o.connect(self.pong1_slot)
        self.process2.signals.pong_o.connect(self.pong2_slot)

    def button1_slot(self):
        self.process1.ping(message="<sent ping from button1>")
        self.check1.setChecked(True)

    def button2_slot(self):
        self.process2.ping(message="<sent ping from button2>")
        self.check2.setChecked(True)

    def pong1_slot(self, ns):
        print("pong1_slot: message=", ns.message)

    def pong2_slot(self, ns):
        print("pong2_slot: message=", ns.message)

    def closeEvent(self, e):
        print("closeEvent!")
        self.process1.stop()
        self.process2.stop()
        self.thread.stop()
        super().closeEvent(e)


def main():
    app = QtWidgets.QApplication(["test_app"])
    mg = MyGui()
    mg.show()
    app.exec_()


if (__name__ == "__main__"):
    main()
