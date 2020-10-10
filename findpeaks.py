# -*- coding: utf-8 -*-
"""
Created on Tue Jul  1 15:37:23 2014

@author: chris
"""


def findpeaks(spikes):
    peaks = []
    length = 200
    for x in range(5, len(spikes)-length):
        ispeak = True
        # if point at x is bigger than all length infront and behind it then it can be added to peaks
        for y in range(1,length):
            if  spikes[x] <= spikes[x-y] or spikes[x] < spikes[x+y] or spikes[x] <= 1:
                ispeak = False
    
        if ispeak:
            peaks.append(x)
    return peaks

def getspeeds(peaks1, peaks2):
    comp_peaks = []
    gap = 10
    speeds = []
    #look through each peak in list one
    for peak1 in peaks1:
        #look in list two 
        for peak2 in peaks2:
            #if there is a value there that lies close enough to that in list one
            if abs(peak2 - peak1) < gap:#add to comparison list and break from loop
                comp_peaks.append((peak1, peak2))
                break
    for peaks in comp_peaks:
        diff = peaks[0] - peaks[1]
        speeds.append(diff)
        
    
    return speeds