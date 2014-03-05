import sys
sys.path = [ '../..' ] + sys.path


from OpenElectrophy.timefrequency import *
from OpenElectrophy import *
import time
import neo
import numpy as np
import quantities as pq


bl = TryItIO().read_block(nb_segment=1, duration = 10)
ana = bl.segments[0].analogsignals[0]

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
                 std_relative_threshold = 7.,
                 reference_zone = [ -np.inf, 0,5., 100.],
                 minimum_cycle_number= 0.,
                 eliminate_simultaneous = True,
                 regroup_full_overlap = True , 
                 eliminate_partial_overlap = True)        
    linedetector.computeAllStep()
    for osci in linedetector.list_oscillation:
        print osci.time_max, osci.freq_max
    
    
    tfr = TimeFreq(ana,f_start=5.,f_stop=100.,
                 deltafreq = 1.,sampling_rate = 400.)
    fig = pyplot.figure()
    ax = fig.add_subplot(1,1,1)
    tfr.plot(ax, clim = [0,2.8])
    pyplot.show()
    


if __name__ == '__main__' :
    test1()
