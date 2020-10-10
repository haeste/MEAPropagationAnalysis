# -*- coding: utf-8 -*-
"""
Created on Tue Apr  1 16:21:11 2014

@author: chris
"""

from scipy.signal import butter, filtfilt

def lowpass(data,samprate,cutoff):
  b,a = butter(2,cutoff/(samprate/2.0),btype='low',analog=0,output='ba')
  data_f = filtfilt(b,a,data)
  return data_f