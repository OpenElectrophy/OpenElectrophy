import sys
sys.path = [ '../..' ] + sys.path


from OpenElectrophy.timefrequency.timefreq import *
import time
import neo


sig_size = 1e3
fs = 10.e3
t = np.arange(sig_size)/fs
t_start = -5.

sig = 7*np.sin(t*np.pi*2*25.) + np.random.randn(sig_size)*6
ana = neo.AnalogSignal(sig, units = 'uV', t_start=t_start*pq.s, sampling_rate = fs*pq.Hz)

from matplotlib import pyplot

def test1():
    
    tfr = TimeFreq(ana)
    fig = pyplot.figure()
    ax = fig.add_subplot(1,1,1)
    tfr.plot(ax)
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

