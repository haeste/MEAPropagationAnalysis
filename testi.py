import neo.io
import numpy
from Propagation import Propagation
from highpass import highpass
from findpeaks import findpeaks
from findpeaks import getspeeds
from scipy.signal import resample
from scipy.signal import find_peaks_cwt
from scipy.signal import argrelextrema
output = "Slice\t Time\t propagation_time\t condition\t abs_prop\t Method\n"
for rec in range(7,10):
    for y in range(1,7):
        num = y * 10
        foldername =  "/var/run/media/chris/Media/Epilepsy_Data/Perfused/Gabazine/280514"
        date = "280514"
        fileName = foldername+"/"+date+"00"+str(rec)+"-"+str(num)+".abf"
        print ("Loading " + fileName)
        try:
           r = neo.io.AxonIO(fileName)
           
           bl = r.read_block(lazy=False, cascade=True)
        except IOError: 
            break
        
        signals = [None] * 2
        signals[0] = bl.segments[0].analogsignals[0]
        signals[1] = bl.segments[0].analogsignals[15]
        t = numpy.linspace(1, signals[0].sampling_rate.magnitude, len(signals[0]))
        print ("Data loaded")
        prop = Propagation(signals)
        spikes = prop.getspikes()
        
        #peaks1 = find_peaks_cwt(spikes[0],numpy.arange(11,12))
        #peaks2 = find_peaks_cwt(spikes[1], numpy.arange(11,12))
        
        
        spikes1 = array(spikes[0])
        spikes2 = array(spikes[1])
        
        xs = numpy.linspace(1, signals[0].sampling_rate.magnitude, num=len(spikes1))
        peaks1 = findpeaks(spikes[0])
        peaks2 = findpeaks(spikes[1])
        print "Length of peaks1: " + str(len(peaks1))
        print "Length of peaks2: " + str(len(peaks2))
        
        plot = False
            
        
       
        if plot:
            f, axarr = plt.subplots(3*len(signals), sharex=True)
            v = signals[0][:].magnitude
            t = linspace(1, signals[0].sampling_rate.magnitude, (len(signals[0])))
            axarr[0].plot(t,v)
            axarr[1].plot(t,highpass(signals[0][:].magnitude,signals[0].sampling_rate.magnitude, 500 ))
            axarr[2].plot(xs, spikes1 )
            v = signals[1][:].magnitude
            t = linspace(1, signals[1].sampling_rate.magnitude, (len(signals[1])))
            axarr[3].plot(t,v)
            axarr[4].plot(t, highpass(signals[1][:].magnitude,signals[1].sampling_rate.magnitude, 500 ))
            axarr[5].plot(xs, spikes2)
            axarr[2].plot(xs[peaks1], spikes1[peaks1], 'rD')
            axarr[5].plot(xs[peaks2], spikes2[peaks2], 'rD')
            
        times = getspeeds(peaks1, peaks2)
        print "times: " + str(times)
        condition = "";
        if rec == 7:
            condition = "Control"
        if rec == 8:
            condition = "AUT1"
        if rec == 9:
            condition = "Washout"
            
        method = "Perfused/Gabazine"
        for time in times:
            output = output + date + "\t" + str(num) + "\t" + str(time*10) + "\t" + condition + "\t" + str(abs(time)*10) + "\t" + method+ "\n"
        
f = open('/home/chris/Copy/workfile.csv', 'w')
f.write(output)
f.close()
print output