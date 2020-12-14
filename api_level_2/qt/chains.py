"""
chains.py : Some thread / filterchain classes for valkka qt examples

Copyright 2019 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    chains.py
@author  Sampsa Riikonen
@date    2019
@version 1.0.3 
@brief   
"""

import sys
import time
import random
from valkka import core # so, everything that has .core, refers to the api1 level (i.e. swig wrapped cpp code)
from valkka.api2.threads import LiveThread, OpenGLThread, FileThread # api2 versions of the thread classes
from valkka.api2.tools import parameterInitCheck, typeCheck
from valkka.api2 import BasicFilterchain


class MovementFilterchain(BasicFilterchain):
    """A filter chain with a shared mem hook

    ::

      (LiveThread:livethread) -->> (AVThread:avthread) --+
                                                         |   main branch
      {ForkFrameFilter: fork_filter} <-------------------+
                 |
        branch 1 +-->> (OpenGLThread:glthread)
                 |
        branch 2 +--> {MovementFrameFilter: movement_filter} --> {SwScaleFrameFilter: sws_filter} --> * {ThreadSafeFrameFilter: threadsafe_filter} ( --> {RGBShmemFrameFilter} )
                           (interval, treshold, duration)

    * Frames are decoded in the main branch from H264 => YUV
    * The stream of YUV frames is forked into two branches
    * branch 1 goes to OpenGLThread that interpolates YUV to RGB on the GPU
    * branch 2 goes to MovementFrameFilter:
    
            interval : How often the frame is checked (milliseconds)
            treshold : Treshold value for movement
            duration : Duration of a single event (milliseconds) 
    
    * movement_filter passes frames only during movement events
    * branch 2 is left open.  Its connected to a common ThreadSafeFrameFilter, defined outside this filterchain
    * the idea is, that there is a single multiprocess for all streams
    """

    parameter_defs = {  # additional parameters to the mother class
        # images passed over shmem are full-hd/4 reso
        "movement_interval"  : (int, 1000),
        "movement_treshold"  : (float, 0.01),
        "movement_duration"  : (int, 5000),
        "image_dimensions"   : (tuple, (1920 // 4, 1080 // 4)),
        "threadsafe_filter"  : core.ThreadSafeFrameFilter,
        "movement_callback"  : None
    }

    parameter_defs.update(BasicFilterchain.parameter_defs)  # don't forget!

    def __init__(self, **kwargs):
        # auxiliary string for debugging output
        self.pre = self.__class__.__name__ + " : "
        # check for input parameters, attach them to this instance as
        # attributes
        parameterInitCheck(self.parameter_defs, kwargs, self)
        typeCheck(self.image_dimensions[0], int)
        typeCheck(self.image_dimensions[1], int)
        self.init()

    def makeChain(self):
        """Create the filter chain
        """
        # branch 1
        # get input FrameFilter from OpenGLThread
        self.gl_in_filter = self.openglthread.getInput()

        # branch 2
        self.sws_filter = core.SwScaleFrameFilter(
            "sws_filter" + self.idst,
            self.image_dimensions[0],
            self.image_dimensions[1],
            self.threadsafe_filter)
        
        # MovementFrameFilter::MovementFrameFilter(char const *,long,float,long,FrameFilter *)
        self.movement_filter = core.MovementFrameFilter(
            "movement_" + self.idst,
            self.movement_interval,
            self.movement_treshold,
            self.movement_duration,
            self.sws_filter
            )
        
        if self.movement_callback is not None:
            self.movement_filter.setCallback(self.movement_callback)
            
        # main branch
        self.fork_filter = core.ForkFrameFilter(
            "fork_filter" + self.idst,
            self.gl_in_filter,
            self.movement_filter)
        
        self.framefifo_ctx = core.FrameFifoContext()
        self.framefifo_ctx.n_basic = self.n_basic
        self.framefifo_ctx.n_setup = self.n_setup
        self.framefifo_ctx.n_signal = self.n_signal
        self.framefifo_ctx.flush_when_full = self.flush_when_full

        self.avthread = core.AVThread(
            "avthread_" + self.idst,
            self.fork_filter,
            self.framefifo_ctx)  # AVThread writes to self.fork_filter
        self.avthread.setAffinity(self.affinity)
        # get input FrameFilter from AVThread
        self.av_in_filter = self.avthread.getFrameFilter()
        # self.av_in_filter is used by BasicFilterchain.createContext that passes self.av_in_filter to LiveThread
        # # self.live_out_filter =core.InfoFrameFilter    ("live_out_filter"+self.idst,self.av_in_filter)


def main():
  pass


if (__name__=="__main__"):
  main() 

