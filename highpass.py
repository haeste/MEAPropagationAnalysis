# -*- coding: utf-8 -*-
"""
Created on Fri Jun 13 15:04:56 2014

@author: chris
"""

from scipy.signal import butter, filtfilt

def highpass(data,samprate,cutoff):
  b,a = butter(2,cutoff/(samprate/2.0),btype='high',analog=0,output='ba')
  data_f = filtfilt(b,a,data)
  return data_f