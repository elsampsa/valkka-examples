"""
single_stream_rtsp.py : Send N copies of an rtsp stream to the screen, using level 2 api

Copyright 2017, 2018 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    single_stream_rtsp.py
@author  Sampsa Riikonen
@date    2017
@version 0.9.0 
@brief   Send N copies of an rtsp stream to the screen, using level 2 api
"""

import sys
import time
from valkka.api2.threads import LiveThread, OpenGLThread
from valkka.api2.chains import BasicFilterchain


def main():
  if (len(sys.argv)<2):
    print("Give rtsp stream address, i.e. rtsp://passwd:user@ip")
    return
  else:
    address=sys.argv[1]
  
  livethread=LiveThread(
    name   ="live_thread",
    verbose=True
    )
  
  openglthread=OpenGLThread(
    name    ="mythread",
    n1440p  =5,
    verbose =True
    )
  
  # now livethread and openglthread are running
  
  chain=BasicFilterchain(
    livethread  =livethread, 
    openglthread=openglthread,
    address     =address,
    slot        =1
    )

  chain.decodingOn() # tell the decoding thread to start its job

  # let's create some windowses
  win_id1 =openglthread.createWindow()
  win_id2 =openglthread.createWindow()
  win_id3 =openglthread.createWindow()
  
  # send video to x windowses
  token1  =openglthread.connect(slot=1,window_id=win_id1)
  token2  =openglthread.connect(slot=1,window_id=win_id2)
  token3  =openglthread.connect(slot=1,window_id=win_id3)
    
  print("sleeping for some secs")
  time.sleep(10)
  
  openglthread.disconnect(token1)
  openglthread.disconnect(token2)
  openglthread.disconnect(token3)
  

if (__name__=="__main__"):
  main() 

