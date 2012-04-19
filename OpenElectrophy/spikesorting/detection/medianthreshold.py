

import numpy as np
import quantities as pq

from .tools import (get_all_crossing_threshold, sweep_clean_in_segment)

class MedianThresholdDetection(object):
    """
    This medthod detect spikes with estimation of the threshold
    with a median of the signal.
    
    The threshold is calculated as
        median_thresh * median(abs(signal)/.6745) 
    """
    name = 'Median threshold detection'
     
    def run(self, spikesorter, sign = '-', median_thresh = 5.,
                        consistent_across_channels = False,
                        consistent_across_segments = True,
                        sweep_clean_method = 'fast',
                        sweep_clean_size = 0.8*pq.ms,
                        ):
        sps = spikesorter
        
        # Use 'sign' to set sign of threshold
        median_thresh = abs(median_thresh)
        
        # Threshold
        thresholds = np.zeros(sps.filtered_sigs.shape, dtype = float)
        for c, s in np.ndindex(sps.filtered_sigs.shape):
            #~ print rc, seg
            sig = sps.filtered_sigs[c, s]
            thresholds[c, s] = median_thresh * np.median(abs(sig)) / .6745
        
        if consistent_across_channels:
            thresholds[:] = np.mean(thresholds, axis=0)[np.newaxis,:]
            
        if consistent_across_segments:
            thresholds[:] = np.mean(thresholds, axis=1)[:, np.newaxis]
        
        if sign == '-':
            thresholds = -thresholds
        
        # Detection
        all_pos_spikes = np.empty(sps.filtered_sigs.shape, dtype = object)
        for c, s in np.ndindex(sps.filtered_sigs.shape):
            pos_spike = get_all_crossing_threshold( sps.filtered_sigs[c, s],
                                                thresholds[c, s], sign)
            all_pos_spikes[c, s] = pos_spike
        
        # Window cleaning
        sps.spike_index_array = np.empty( len(sps.segs), dtype = object)
        sweep_size = int((sps.sig_sampling_rate*sweep_clean_size).simplified)
        for s in range(len(sps.segs)):
            sps.spike_index_array[s] = sweep_clean_in_segment(
                                        all_pos_spikes[:,s],
                                        sps.filtered_sigs[:, s],
                                        sweep_size,
                                        method = sweep_clean_method)
            
