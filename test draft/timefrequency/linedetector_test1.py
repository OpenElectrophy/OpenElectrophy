import sys
sys.path = [ '../..' ] + sys.path


from OpenElectrophy.timefrequency import *
import time
import neo
import numpy as np
import quantities as pq

sig_size = 10e3
fs = 1.e3
t = np.arange(sig_size)/fs
t_start = -5.

sig = 7*np.sin(t*np.pi*2*25.) + np.random.randn(sig_size)*6
ana = neo.AnalogSignal(sig, units = 'uV', t_start=t_start*pq.s, sampling_rate = fs*pq.Hz)
print ana.t_start, ana.t_stop

from matplotlib import pyplot

def test1():
    
    linedetector  = LineDetector(ana, 
                 f_start=5.,
                 f_stop=100.,
                 deltafreq = 1.,
                 sampling_rate = 400.,
                 t_start = -np.inf, 
                 t_stop = np.inf,
                 f0=2.5, 
                 normalisation = 0.,
                 detection_zone = [ 0, np.inf, 5, 80.],
                 manual_threshold = False,
                 abs_threshold = np.nan,
                 std_relative_threshold = 6.,
                 reference_zone = [ -np.inf, 0,5., 100.],
                 minimum_cycle_number= 0.,
                 eliminate_simultaneous = True,
                 regroup_full_overlap = True , 
                 eliminate_partial_overlap = True)        
    linedetector.computeAllStep()
    for osci in linedetector.list_oscillation:
        print osci
    
    
    tfr = TimeFreq(ana)
    fig = pyplot.figure()
    ax = fig.add_subplot(1,1,1)
    tfr.plot(ax, clim = [0,10])
    pyplot.show()
    


if __name__ == '__main__' :
    test1()
