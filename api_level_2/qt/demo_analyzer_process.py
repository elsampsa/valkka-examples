"""
demo_analyzer_process.py : Use analyzers from the local file "analyzer.py" in a QValkkaOpenCVProcess multiprocess

Copyright 2017, 2018 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    demo_analyzer_process.py
@author  Sampsa Riikonen
@date    2017
@version 1.0.3 
@brief   Use analyzers from the local file "analyzer.py" in a QValkkaOpenCVProcess multiprocess


When using python multiprocesses with Qt, we need a frontend thread that reads the process communication pipes and turns the messages sent by the process into Qt signals.
"""
import time
import importlib

# from PyQt5 import QtWidgets, QtCore, QtGui # If you use PyQt5, be aware
# of the licensing consequences
# If you use PyQt5, be aware of the licensing consequences
from PySide2 import QtWidgets, QtCore, QtGui

# Local imports from this directory
from demo_multiprocess import QValkkaOpenCVProcess
from analyzer import MovementDetector


class QValkkaMovementDetectorProcess(QValkkaOpenCVProcess):

    incoming_signal_defs = {  # each key corresponds to a front- and backend methods
        "create_client_" : [],
        "test_": {"test_int": int, "test_str": str},
        "stop_": [],
        "ping_": {"message": str}
    }

    outgoing_signal_defs = {
        "pong_o": {"message": str},
        "start_move": {},
        "stop_move": {}
    }

    # For each outgoing signal, create a Qt signal with the same name.  The
    # frontend Qt thread will read processes communication pipe and emit these
    # signals.
    class Signals(QtCore.QObject):
        # PyQt5 version:
        """
        pong_o     =QtCore.pyqtSignal(object)
        start_move =QtCore.pyqtSignal()
        stop_move  =QtCore.pyqtSignal()
        """
        # PySide2 version:
        pong_o = QtCore.Signal(object)
        start_move = QtCore.Signal()
        stop_move = QtCore.Signal()

    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)  # does parameterInitCheck
        self.signals = self.Signals()
        # # parameterInitCheck(QValkkaMovementDetectorProcess.parameter_defs, kwargs, self)
        # self.analyzer=MovementDetector(verbose=True)
        self.analyzer = MovementDetector(treshold=0.0001)


    def cycle_(self):
        if self.client is None:
            time.sleep(1.0)
        else:
            index, isize = self.client.pull()
            if (index is None):
                # print(self.pre, "Client timed out..")
                pass
            else:
                # print(self.pre, "Client index, size =", index, isize)
                data = self.client.shmem_list[index]
                try:
                    img = data.reshape(
                        (self.image_dimensions[1], self.image_dimensions[0], 3))
                except BaseException:
                    print("QValkkaMovementDetectorProcess: WARNING: could not reshape image")
                    pass
                else:
                    result = self.analyzer(img)
                    # print(self.pre,">>>",data[0:10])
                    if (result == MovementDetector.state_same):
                        pass
                    elif (result == MovementDetector.state_start):
                        self.sendSignal_(name="start_move")
                    elif (result == MovementDetector.state_stop):
                        self.sendSignal_(name="stop_move")

    # ** frontend methods handling received outgoing signals ***

    def start_move(self):
        print(self.pre, "At frontend: got movement")
        self.signals.start_move.emit()

    def stop_move(self):
        print(self.pre, "At frontend: movement stopped")
        self.signals.stop_move.emit()



class QValkkaGlobalDetectorProcess(QValkkaOpenCVProcess):
    
    outgoing_signal_defs = {
        "detected_objects": {"object_list": list}
    }
    
    class Signals(QtCore.QObject):
        # PySide2 version:
        detected_objects = QtCore.Signal(object)

    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)  # does parameterInitCheck
        self.signals = self.Signals()

    def preRun_(self):
        super().preRun_()
        # load yolo after the fork
        try:
            predictor_module = importlib.import_module("darknet.api2.predictor")
        except Exception as e:
            print("Could not import darknet: failed with:", str(e))
            self.yolo = None
        else:
            try:
                self.yolo = predictor_module.get_YOLOv3_Tiny_Predictor() # tiny yolo v3
            except Exception as e:
                print("Could not get yolo predictor: failed with:", str(e))
                self.yolo = None

    def cycle_(self):
        if self.client is None:
            time.sleep(1.0)
        else:
            index, meta = self.client.pullFrame()
            if (index is None):
                # print(self.pre, "Client timed out..")
                pass
            else:
                # print(self.pre, "Client index, size =", index, isize)
                data = self.client.shmem_list[index][0:meta.size]
                """# if you wanna be chatty
                print("data   : ",data[0:min(10,meta.size)])
                print("width  : ", meta.width)
                print("height : ", meta.height)
                print("slot   : ", meta.slot)
                print("time   : ", meta.mstimestamp)
                print("size required : ", meta.width * meta.height * 3)
                print("size copied   : ", meta.size)
                print()
                """
                try:
                    img = data.reshape(
                        (meta.height, meta.width, 3))
                except BaseException:
                    print("QValkkaMovementDetectorProcess: WARNING: could not reshape image")
                    pass
                else:
                    if self.yolo is not None:
                        lis = self.yolo(img) # e.g. [('sofa', 56, 239, 473, 111, 230)]
                        # print("slot",meta.slot,"got",lis)
                        object_list = []
                        for tup in lis:
                            # object_list.append(tup + (meta.slot, meta.mstimestamp)) # add information to tuple: slot number, mstimestamp
                            object_list.append(
                                (tup[0], tup[1], # name, prob
                                tup[2]/meta.width, tup[3]/meta.width, tup[4]/meta.height, tup[5]/meta.height, # coordinates: left, right, top, bottom & scaled to image width / height
                                meta.slot, meta.mstimestamp) # add information: slot number, mstimestamp
                                )
                        self.sendSignal_(name="detected_objects", object_list=object_list) # this'll appear at the frontend
                    
                    
    # *** frontend ***
                    
    def detected_objects(self, object_list):
        # print("frontend: object_list=", object_list)
        self.signals.detected_objects.emit(object_list)
        

def test1():
    pass


def main():
    pre = "main :"
    print(pre, "main: arguments: ", sys.argv)
    if (len(sys.argv) < 2):
        print(pre, "main: needs test number")
    else:
        st = "test" + str(sys.argv[1]) + "()"
        exec(st)


if (__name__ == "__main__"):
    main()
