# -*- coding: utf-8 -*-

from scipy import signal
import numpy as np



class ButterworthFilter:
    """
    Classic filter with buterworth design.
    """
    name = 'Butterworth filter'
    
    
    def run(self, spikesorter,  f_low = 0. , N = 5):
        
        s = spikesorter
        
        if s.filteredBandAnaSig is None:
            s.filteredBandAnaSig = np.empty( s.fullBandAnaSig.shape, dtype = object)
        
        Wn = f_low/(s.signalSamplingRate/2.)
        #~ print Wn
        b,a = signal.iirfilter(N, Wn, btype = 'high', analog = 0, ftype = 'butter', output = 'ba')
        
        for rc, seg in np.ndindex(s.fullBandAnaSig.shape):
            #~ print rc, seg
            anasig = s.fullBandAnaSig[ rc, seg]
            s.filteredBandAnaSig[ rc, seg] = signal.lfilter(b, a, anasig, zi = None)

    