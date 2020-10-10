from scipy.signal import butter, filtfilt

class Propagation:
    def __init__(self, data, threshold=30, window=100):
        self.filterfreq = 500
        self.window = window
        self.threshold = threshold
        self.data = [None] * len(data)
        print "length of data: "+ str(len(data))
        for x in range(0, len(data)):
            self.data[x] = self.highpass(data[x], data[x].sampling_rate.magnitude, self.filterfreq)
        

    #Gets the count of spikes in bins of length window
    def getspikes(self):
        data = self.data
        spikes = [None] * len(data) # list of spike counts for each bin
        width = 10 # the width of a spike
        #for each channel count the number of spikes
        #in each bin of width window
        for x in range(0, len(data)):
            spike_loc = [0] # store the locations of the spikes
            print x
            count = 0 # for counting up to the length of the window
            spikes_index = 0 # keeps the index of the current bin
            spikes[x] = [0] #initial list
            print len(data[x])
            # for each data point in the signal
            for y in range(0, len(data[x])):
                count += 1
                #if we have reached the end of the current bin
                if count == self.window:
                    count = 0 #reset count
                    spikes[x].append(0) #add new bin to spikes
                    spikes_index += 1 #move to next bin

                if abs(data[x][y]) > self.threshold:
                    #if the data point is above threshold and far enough away from the last spike
                    # to not likely be the same spike, then add a new spike to the count
                    if y-spike_loc[-1]>width:
                        spikes[x][spikes_index] += 1
                    spike_loc.append(y)
        return spikes
        
    def highpass(self,data,samprate,cutoff):
        b,a = butter(2,cutoff/(samprate/2.0),btype='high',analog=0,output='ba')
        data_f = filtfilt(b,a,data)
        return data_f