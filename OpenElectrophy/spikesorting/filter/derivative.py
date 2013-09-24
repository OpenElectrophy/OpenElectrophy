# -*- coding: utf-8 -*-

from scipy import signal
import numpy as np
import quantities as pq


class DerivativeFilter(object):
    """
    This method take the derivatives of signals instead of classical band pass filter (IIR or FIR).
    This have this advantages:
       * very fast
       * behave like a hight pass filter
       * reduce spike duration (other filter expand spike length)
       
    This simple idea come from Christophe Pouzat.
    
    
    """
    name = 'Derivative filter'
    params = [ ]
    
    def run(self, spikesorter,):
        
        sps = spikesorter
        
        if sps.filtered_sigs is None:
            sps.filtered_sigs = np.empty( sps.full_band_sigs.shape, dtype = object)
        
        for c, s in np.ndindex(sps.full_band_sigs.shape):
            anasig = sps.full_band_sigs[c, s]
            sps.filtered_sigs[c, s] = np.diff(anasig)
            
