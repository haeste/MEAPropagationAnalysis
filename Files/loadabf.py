import numpy
import neo.io
r = neo.io.AxonIO(filename='/var/run/media/chris/Media/Epilepsy_Data/Perfused/170614/170614-1/170614001-40.abf')
bl = r.read_block(lazy=False, cascade=True)
signals = bl.segments[0].analogsignals
t = numpy.linspace(1, (len(signals[0])*signals[0].sampling_rate.magnitude),  signals[0].sampling_rate.magnitude)
print signals




