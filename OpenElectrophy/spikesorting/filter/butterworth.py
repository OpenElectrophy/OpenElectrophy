# -*- coding: utf-8 -*-

from scipy import signal
import numpy as np



class ButterworthFilter(object):
    """
    Classic filter with buterworth design.
    """
    name = 'Butterworth filter'
    
    
    def run(self, spikesorter,  f_low = 0. , N = 5):
        
        sps = spikesorter
        
        if sps.filtered_sigs is None:
            sps.filtered_sigs = np.empty( sps.full_band_sigs.shape, dtype = object)
        
        Wn = f_low/(sps.sig_sampling_rate/2.)
        b,a = signal.iirfilter(N, Wn, btype = 'high', analog = 0, ftype = 'butter', output = 'ba')
        
        for c, s in np.ndindex(sps.full_band_sigs.shape):
            anasig = sps.full_band_sigs[c, s]
            sps.filtered_sigs[c, s] = signal.filtfilt(b, a, anasig)
            

    