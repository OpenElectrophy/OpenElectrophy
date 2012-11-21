import sys
sys.path = [ '../..' ] + sys.path


from OpenElectrophy.timefrequency.timefreq import *
from OpenElectrophy import *
import time
import neo



bl = TryItIO().read(nb_segment=1, duration = 10)
ana = bl.segments[0].analogsignals[0]

from matplotlib import pyplot

def test1():
    
    tfr = TimeFreq(ana)
    fig = pyplot.figure()
    ax = fig.add_subplot(1,1,1)
    tfr.plot(ax,  clim = [0,3])
    print tfr.sampling_rate
    print tfr.freqs.shape
    print tfr.times.shape
    print tfr.times[0], tfr.times[-1]
    print tfr.map.shape
    pyplot.show()
    


def test2():
    for i in range(6):
        t1 = time.time()
        if i<3:
            TimeFreq(ana)
        else:
            TimeFreq(ana, f_stop = 50)
        t2 = time.time()
        print i,  t2-t1
    


if __name__ == '__main__' :
    test1()
    #~ test2()

