# -*- coding: utf-8 -*-

from scipy import signal
import numpy as np
import quantities as pq

import scipy.interpolate

import time

class SlidingMedianFilter(object):
    """
    This filter is a hight pass filter by removing the median ina sliding.
    This method is quite good for slow drift removal.
    
    """
    name = 'Sliding median filter'
    params = [  {'name': 'window_size', 'type': 'quantity', 'value': 500.*pq.ms,'step' : 100*pq.ms },
                            {'name': 'sliding_step', 'type': 'quantity', 'value': 250.*pq.ms,'step' : 100*pq.ms },
                            {'name': 'interpolation', 'type': 'list', 'value': 'linear' ,'values' : ['linear',   'quadratic', 'cubic', 'spline'] },
                            ]
    
    def run(self, spikesorter, window_size =  500.*pq.ms,
                             sliding_step =  250.*pq.ms, interpolation = 'spline'):
        
        sps = spikesorter
        
        if sps.filtered_sigs is None:
            sps.filtered_sigs = np.empty( sps.full_band_sigs.shape, dtype = object)
        
        sr = sps.sig_sampling_rate
        win = int((window_size*sr).simplified)
        step = int((sliding_step*sr).simplified)
        
        for c, s in np.ndindex(sps.full_band_sigs.shape):
            anasig = sps.full_band_sigs[c, s]
            centers = np.concatenate([np.arange(0, anasig.size, step), [anasig.size-1]], axis=0)
            medians = np.zeros(centers.size)
            t0 = time.time()
            for i, center in enumerate(centers):
                i1, i2 = int(center-win/2.), int(center+win/2.)
                if i1<0: i1=0
                if i2>=anasig.size : i2=anasig.size
                medians[i] = np.median(anasig[i1:i2])
            t1 = time.time()
            if interpolation == 'spline':
                interpolation =2
            interp = scipy.interpolate.interp1d(centers, medians, kind = interpolation)
            t2 = time.time()
            sps.filtered_sigs[c, s] = anasig - interp(np.arange(anasig.size))
            t3 = time.time()
