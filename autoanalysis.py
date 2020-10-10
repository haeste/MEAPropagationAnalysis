import neo.io
import numpy
import matplotlib
import matplotlib.widgets
import matplotlib.pyplot as plt
from Propagation import Propagation
from highpass import highpass
from findpeaks import findpeaks
from findpeaks import getspeeds
from scipy.signal import resample
from scipy.signal import find_peaks_cwt
from scipy.signal import argrelextrema
class Autoanalysis:
    def __init__(self, signals):
        self.signals = signals
        self.t = []
        self.spikes = []
        self.peaks = [None] * 2
        matplotlib.rc('xtick', labelsize=8)
        matplotlib.rc('ytick', labelsize=8)
        font = dict(family='normal', weight='normal', size=8)
        matplotlib.rc('font', **font)
        self.plt_length = (3 * len(self.signals))
        self.axes = [None] * self.plt_length
        self.times = None



    def analyse(self, threshold, window=100):
        prop = Propagation(self.signals, threshold, window)
        self.spikes = prop.getspikes()
        temp = self.spikes[0]
        self.spikes[0] = self.spikes[1]
        self.spikes[1] = temp
        self.spikes[0] = numpy.array(self.spikes[0])
        self.spikes[1] = numpy.array(self.spikes[1])
        print str(len(self.spikes[0]))
        self.peaks[0] = findpeaks(self.spikes[0])
        self.peaks[1] = findpeaks(self.spikes[1])
        times = getspeeds(self.peaks[0], self.peaks[1])
        self.times = [x*window/self.signals[0].sampling_rate.magnitude for x in times]
        print self.times
        return self.times

    def plot(self, widget):
        v = self.signals[0][:].magnitude
        t = numpy.linspace(1, len(self.signals[0])/self.signals[0].sampling_rate.magnitude, num=len(self.signals[0]))
        xs = numpy.linspace(1, len(self.signals[0])/self.signals[0].sampling_rate.magnitude, num=len(self.spikes[0]))
        self.axes[0] = widget.fig.add_subplot(self.plt_length, 1, 1, sharex=self.axes[0])
        self.axes[1] = widget.fig.add_subplot(self.plt_length, 1, 2, sharex=self.axes[0])
        self.axes[2] = widget.fig.add_subplot(self.plt_length, 1, 3, sharex=self.axes[0])
        self.axes[3] = widget.fig.add_subplot(self.plt_length, 1, 4, sharex=self.axes[0])
        self.axes[4] = widget.fig.add_subplot(self.plt_length, 1, 5, sharex=self.axes[0])
        self.axes[5] = widget.fig.add_subplot(self.plt_length, 1, 6, sharex=self.axes[0])


        self.axes[0].plot(t, v)
        self.axes[0].set_title(str(self.signals[0].name))
        self.axes[1].plot(t, highpass(self.signals[0][:].magnitude, self.signals[0].sampling_rate.magnitude, 500 ))
        self.axes[1].set_title(str(self.signals[0].name)+"(Filtered)")
        self.axes[2].plot(xs, self.spikes[1], linestyle='steps')
        self.axes[2].set_title(str(self.signals[0].name)+"(Spikes)")
        v = self.signals[1][:].magnitude
        self.axes[3].plot(t, v)
        self.axes[3].set_title(str(self.signals[1].name))
        self.axes[4].plot(t, highpass(self.signals[1][:].magnitude,self.signals[1].sampling_rate.magnitude, 500 ))
        self.axes[4].set_title(str(self.signals[1].name)+"(Filtered)")
        self.axes[5].plot(xs, self.spikes[0], linestyle='steps')
        self.axes[5].set_title(str(self.signals[1].name)+"(Spikes)")
        self.axes[5].plot(xs[self.peaks[0]], self.spikes[0][self.peaks[0]], 'rD')
        self.axes[2].plot(xs[self.peaks[1]], self.spikes[1][self.peaks[1]], 'rD')
        self.axes[5].set_xlabel("Time(s)")
        self.axes[0].set_ylabel(str(self.signals[0].units))
        self.axes[1].set_ylabel(str(self.signals[0].units))
        self.axes[2].set_ylabel('number of spikes')
        self.axes[3].set_ylabel(str(self.signals[1].units))
        self.axes[4].set_ylabel(str(self.signals[1].units))
        self.axes[5].set_ylabel('number of spikes')

    def get_results(self, rec, num, date, method):
        print "rec: " + str(rec) + " num: " + str(num) + " date: " + str(date) + " method: " + str(method)
        condition = ""
        if rec == "1":
            condition = "Control"
        if rec == "2":
            condition = "AUT1"
            num = int(num) + 6
        if rec == "3":
            condition = "Washout"
            num = int(num) + 12
        print "writing results.."
        output = ""
        for time in self.times:
            output = output + date + "\t" + str(int(num)*10) + "\t" + str(time) + "\t" + condition + "\t" + str(abs(time)) + "\t" + method + "\n"
        return output
