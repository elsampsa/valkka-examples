from PySide2 import QtWidgets, QtCore, QtGui
import threading, select, time
from multiprocessing import Pipe


class QHandlerThread(QtCore.QThread):
    """A QThread that listens to several multiprocesses and converts their messages into Qt signals
    """
    def __init__(self):
        super().__init__()
        self.front_pipe, self.back_pipe = Pipe()
        self.processes_by_pipe = {} # key: a readable pipe, value: the corresponding process
        self.comlist = [] # list of tuples: (str, obj), representing the functions backend should perform
        self.comlist_lock = threading.Lock() # this is multithreading: we need to protect this list used both by front- and backend

    # THREAD BACKEND

    def run(self):
        """Threads functionality

        - listen to multiple intercommunication channels: pipes from the frontend and from the multiprocesses
        - new multiprocesses can be registered
        """
        self.active = True
        while self.active:
            rlis = [pipe for pipe, process in self.processes_by_pipe.items()]
            rlis.append(self.back_pipe)
            # now rlis includes all pipes we need to listen: pipes of the processes & the intercom pipe of this thread
            r, w, e = select.select(rlis, [], [], 1) # one sec timeout
            if (len(r) < 1):
                print("thread backend: no messages from main thread but I'm still alive")
                continue
            for pipe in r: # run through all pipes that are ready for reading
                if (pipe == self.back_pipe): # this thread's intercom pipe
                    msg = pipe.recv()
                    print("thread backend: message from the main program", msg)
                    if msg == "com":
                        # thread is notified that it should take a look into self.comlist
                        with self.comlist_lock: # we're doing multithreading, so protect comlist access with a lock
                            comstr, obj = self.comlist.pop()
                            print("thread backend: comstr, obj", comstr, obj)
                            if comstr == "addProcess":
                                self.addProcess__(obj)
                            elif comstr == "someSlot":
                                self.someSlot__(obj)
                    elif msg == "stop":
                        self.active = False
                        break
                else: # must be multiprocesses intercom pipe
                    process = self.processes_by_pipe[pipe]
                    msg = pipe.recv()
                    """We're expecting a dictionary like this:

                    ::

                        {"signal":"signal_name"}

                    Please look at demo_qthread.py: MovementDetectorProcess.sendSignal

                    That is then converted here into a signal that is emitted by this very
                    thread.  The member MovementDetectorProcess.signals is used directly
                    by this thread
                    """
                    print("thread backend: message from process", process)
                    if isinstance(msg, dict):
                        # message from the multiprocess is a dictionary
                        # should be of the form:
                        # msg = {"signal":"signal_name"}
                        if "signal" in msg:
                            signal_name = msg["signal"]
                            # look for signal with this name in process.signals
                            if hasattr(process.signals, signal_name):
                                # emit the signal into the Qt subsystem
                                print("found signal", signal_name, "emitting")
                                getattr(process.signals, signal_name).emit(None)
                    else:
                        print("thread backend: unkown message from process", process)

        print("thread: bye!")
                

    def addProcess__(self, process):
        """Register a process
        """
        self.processes_by_pipe[process.getPipe()] = process
        

    def someSlot__(self, par):
        print("thread backend: someSlot", par)


    # THREAD FRONTEND

    def addProcess(self, process):
        """Tell thread to start listening to a multiprocess
        """
        with self.comlist_lock: # we're doing multithreading, so protect comlist access with a lock
            self.comlist.append((
                "addProcess", process
            ))
        self.front_pipe.send("com") # tell thread backend to check out comlist

    
    def someSlot(self, par):
        with self.comlist_lock: # we're doing multithreading, so protect comlist access with a lock
            self.comlist.append((
                "someSlot", par
            ))
        self.front_pipe.send("com") # tell thread backend to check out comlist


    def stop(self):
        self.front_pipe.send("stop")
        self.wait()


def main():
    from valkka.multiprocess import MessageProcess, MessageObject, safe_select
    from demo_rgb import RGB24Process

    class TestProcess(RGB24Process):
        """To implement your own detector process, just override handleFrame__  :)
        """
        class Signals(QtCore.QObject):
            pong = QtCore.Signal(object)

        def __init__(self, mstimeout = 1000):
            super().__init__(mstimeout = mstimeout)
            self.signals = self.Signals()

        def sendSignal__(self, name):
            self.send_out__({"signal": name}) # send a dict object to the frontend
            # this message is typically captured by a QThread running in the frontend
            # which then converts it into a Qt signal
            
        def readPipes__(self, timeout):
            rlis = [self.back_pipe]
            rs, ws, es = safe_select(rlis, [], [], timeout = timeout)
            for fd in rs:
                # 1. handle the main intercom pipe
                if fd is self.back_pipe:
                    self.handleBackPipe__(self.back_pipe)
            self.sendSignal__("pong")


    p = TestProcess()
    p.start()
    t = QHandlerThread()
    t.start()
    t.addProcess(p)
    time.sleep(10)
    p.stop()
    t.stop()

if __name__ == "__main__":
    main()


