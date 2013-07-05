# -*- coding: utf-8 -*-

from scipy import signal
import numpy as np
import quantities as pq


class ButterworthFilter(object):
    """
    Classic filter with buterworth design.
    """
    name = 'Butterworth filter'
    params = [  {'name': 'f_low', 'type': 'float', 'value': 200., 'step': 10.},
                            {'name': 'order_n', 'type': 'int', 'value': 5},
                            ]
    
    def run(self, spikesorter,  f_low = 0. , order_n = 5):
        
        sps = spikesorter
        
        if sps.filtered_sigs is None:
            sps.filtered_sigs = np.empty( sps.full_band_sigs.shape, dtype = object)
        
        Wn = f_low/(sps.sig_sampling_rate/2.)
        b,a = signal.iirfilter(order_n, Wn, btype = 'high', analog = 0, ftype = 'butter', output = 'ba')
        
        for c, s in np.ndindex(sps.full_band_sigs.shape):
            anasig = sps.full_band_sigs[c, s]
            sps.filtered_sigs[c, s] = signal.filtfilt(b, a, anasig)
            
