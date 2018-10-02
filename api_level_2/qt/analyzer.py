"""
analyzer.py : A base class for analyzing image streams using OpenCV and an example movement detector.

Copyright 2018 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Python3 examples library

Valkka Python3 examples library is free software: you can redistribute it and/or modify it under the terms of the MIT License.  This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the MIT License for more details.

@file    analyzer.py
@author  Sampsa Riikonen
@date    2018
@version 0.6.0 
@brief   A base class for analyzing image streams using OpenCV and an example movement detector.
"""

import sys
import time
import cv2
import imutils
import numpy
from valkka.api2.tools import parameterInitCheck


class Analyzer(object):
  """A generic analyzer class
  """

  parameter_defs={
    "verbose" : (bool,False), # :param verbose: verbose output or not?  Default: False.
    "debug"   : (bool,False)  # :param debug:   When this is True, will visualize on screen what the analyzer is doing (using OpenCV highgui)
    }


  def __init__(self,**kwargs):
    parameterInitCheck(Analyzer.parameter_defs,kwargs,self,undefined_ok=True) # checks that kwargs is consistent with parameter_defs.  Attaches parameters as attributes to self.  This is a mother class: there might be more parameters not defined here from child classes
    self.pre=self.__class__.__name__+" : "
    # self.reset() # do this in child classes only ..


  def reset(self):
    """If the analyzer has an internal state, reset it
    """
    pass
  
  
  def __call__(self,img):
    """Do the magic for image img. Shape of the image array is (i,j,colors)
    """
    pass
  
  
  def report(self,*args):
    if (self.verbose):
      print(self.pre,*args)
      # pass
    
    
    
class MovementDetector(Analyzer):
  """A demo movement detector, written using OpenCV
  """

  # return values:
  state_same    =0  # no state change
  state_start   =1  # movement started
  state_stop    =2  # movement stopped
  
  parameter_defs={
    "verbose"  : (bool,False),  # :param verbose:  Verbose output or not?  Default: False.
    "debug"    : (bool,False),  # :param debug:    When this is True, will visualize on screen what the analyzer is doing.  Uses OpenCV highgui.  WARNING: this will not work with multithreading/processing.
    "deadtime" : (int,3),       # :param deadtime: Movement inside this time interval belong to the same event
    "treshold" : (float,0.001)  # :param treshold: How much movement is an event (area of the image place)
    }
  
  
  def __init__(self,**kwargs):
    super().__init__(**kwargs)
    parameterInitCheck(MovementDetector.parameter_defs,kwargs,self) # checks that kwargs is consistent with parameter_defs.  Attaches parameters as attributes to self
    self.pre=self.__class__.__name__+" : "
    self.reset()
  
  
  def reset(self):
    self.prevframe =None
    self.wasmoving =False
    self.t0        =0
    
  
  def __call__(self,img):
    # self.report("got frame :",img)
      
    modframe = imutils.resize(img, width=500)
    
    if (self.debug): cv2.imshow("SimpleMovementDetector_channels-modframe",modframe)
    
    modframe = cv2.GaussianBlur(modframe, (21, 21), 0)
        
    if (self.prevframe.__class__==None.__class__): # first frame
      self.prevframe=modframe.copy()
      self.report("First image found!")
      result =self.state_same
    
    else: # second or n:th frame
      delta  = cv2.absdiff(self.prevframe.max(2), modframe.max(2))
      if (self.debug): cv2.imshow("SimpleMovementDetector_channels-delta0",delta)
      delta  = cv2.threshold(delta, 100, 1, cv2.THRESH_BINARY)[1] # TODO: how much treshold here..?
      val=delta.sum()/(delta.shape[0]*delta.shape[1])
      # print(self.pre,"MovementDetector: val=",val)
      self.prevframe=modframe.copy()
      
      if (val>=self.treshold): # one promille ok .. there is movement
        self.t0=time.time()
        self.report("==>MOVEMENT!")
        if (self.wasmoving):
          result =self.state_same
        else:
          self.t0_event=self.t0
          self.wasmoving=True
          self.report("==> NEW MOVEMENT EVENT!")
          result =self.state_start
          
      else: # no movement
        dt=time.time()-self.t0 # how much time since the last movement event
        if (dt>=self.deadtime and self.wasmoving): # lets close this event ..
          dt_event=time.time()-self.t0_event
          self.wasmoving=False
          result =self.state_stop
          self.report("==> MOVEMENT STOPPED!")
        else:
          result =self.state_same
        
      if (self.debug): cv2.imshow("SimpleMovementDetector_channels-delta",delta*255)
  
    if (self.debug):
      # cv2.waitKey(40*25) # 25 fps
      # cv2.waitKey(self.frametime)
      cv2.waitKey(1)
    
    return result
  
  

def test1():
  """Dummy-testing the movement analyzer
  """
  analyzer=MovementDetector(verbose=True,debug=True)
  
  img=numpy.zeros((1080//4,1920//4,3))
  result=analyzer(img)
  print("\nresult =",result,"\n")
  
  img=numpy.zeros((1080//4,1920//4,3))
  result=analyzer(img)
  print("\nresult =",result,"\n")
  
  img=numpy.ones((1080//4,1920//4,3))*100
  result=analyzer(img)
  print("\nresult =",result,"\n")
  
  
def test2():
  """TODO: demo here the OpenCV highgui with valkka
  """
  pass
  

def main():
  pre="main :"
  print(pre,"main: arguments: ",sys.argv)
  if (len(sys.argv)<2):
    print(pre,"main: needs test number")
  else:
    st="test"+str(sys.argv[1])+"()"
    exec(st)
  
  
if (__name__=="__main__"):
  main()


